import re
import typing as t

if t.TYPE_CHECKING:
    from types import ModuleType

# Public helpers re-exports. Exposed lazily so that importing the models package
# does not pull in atproto_client.models.utils (and its record-type database) eagerly.
_UTILS_EXPORTS = frozenset(
    {
        'create_strong_ref',
        'get_model_as_dict',
        'get_model_as_json',
        'get_or_create',
        'is_record_type',
    }
)

_NOT_REBUILT_CLASSES = {
    'BaseModel',
    'ModelBase',
    'ParamsModelBase',
    'DataModelBase',
    'ResponseModelBase',
    'UnknownDict',
    'DotDict',
    'UnknownRecord',
    'RecordModelBase',
    'BlobRef',
    'CID',
}


def _get_forward_ref_namespace() -> t.Dict[str, t.Any]:
    """Return the names required to resolve the string forward references used across models.

    Generated model modules import these only under ``typing.TYPE_CHECKING`` (to keep imports
    cheap and to avoid eagerly loading the whole package), so they are absent from the module
    namespace at runtime. They have to be injected back so that pydantic can resolve the string
    forward references when it builds a model's schema.
    """
    from atproto_core.cid import CIDType

    from atproto_client import models
    from atproto_client.models import dot_dict
    from atproto_client.models.blob_ref import BlobRef
    from atproto_client.models.unknown_type import UnknownInputType, UnknownType

    return {
        'models': models,
        'dot_dict': dot_dict,
        'BlobRef': BlobRef,
        'UnknownType': UnknownType,
        'UnknownInputType': UnknownInputType,
        'CIDType': CIDType,
    }


def _nsid_name_to_module_name(name: str) -> str:
    # The NSID name segment is camelCase the generated module file is snake_case.
    # Mirrors atproto_codegen.utils.convert_camel_case_to_snake_case, which decides the module filenames.
    # Keep the two in sync!
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _module_path_from_nsid(package_name: str, nsid: str) -> str:
    *namespace, name = nsid.split('.')
    return '.'.join([package_name, *namespace, _nsid_name_to_module_name(name)])


def _model_aliases(package: 'ModuleType') -> t.List[str]:
    ids = package.__dict__.get('ids')
    if ids is None:
        return []

    return [alias for alias in vars(type(ids)) if not alias.startswith('_')]


def make_lazy_accessors(
    package_name: str,
) -> 't.Tuple[t.Callable[[str], t.Any], t.Callable[[], t.List[str]]]':
    """Build ``__getattr__``/``__dir__`` for the lazily-loaded models package.

    Resolved attributes are cached on the package, so each accessor runs at most once per name.
    """
    import importlib

    def __getattr__(name: str) -> t.Any:
        package = importlib.import_module(package_name)

        nsid = getattr(package.__dict__.get('ids'), name, None)
        if nsid is not None:
            module = importlib.import_module(_module_path_from_nsid(package_name, nsid))
            prepare_model_module(module)
            package.__dict__[name] = module
            return module

        if name in _UTILS_EXPORTS:
            utils = importlib.import_module(f'{package_name}.utils')
            value = getattr(utils, name)
            package.__dict__[name] = value
            return value

        raise AttributeError(f'module {package_name!r} has no attribute {name!r}')

    def __dir__() -> t.List[str]:
        package = importlib.import_module(package_name)
        return sorted({*package.__dict__, *_model_aliases(package), *_UTILS_EXPORTS})

    return __getattr__, __dir__


def prepare_model_module(module: 'ModuleType') -> None:
    """Inject the forward-reference namespace into a freshly imported generated model module.

    Pydantic resolves the string forward references against the module's globals when it (lazily) builds
    each model's schema on first validation, so the names must be present there.
    """
    module_dict = vars(module)
    for name, value in _get_forward_ref_namespace().items():
        module_dict.setdefault(name, value)


def _iter_rebuildable_models(module: 'ModuleType') -> t.Iterator[t.Any]:
    for name, value in vars(module).items():
        if name.startswith('_') or name in _NOT_REBUILT_CLASSES:
            continue

        if hasattr(value, 'model_rebuild'):
            yield value


def load_models() -> None:
    """Eagerly import and rebuild every generated model.

    Models are imported and built lazily on first access, so calling this is optional. Use it to
    pay the (one-time) cost up-front instead of on first use, e.g. before forking worker processes
    or to avoid a latency spike on the first request.
    """
    import importlib

    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef

    package_name = models.__name__
    module_paths = {
        _module_path_from_nsid(package_name, getattr(models.ids, alias)) for alias in _model_aliases(models)
    }

    modules = []
    for module_path in sorted(module_paths):
        module = importlib.import_module(module_path)
        prepare_model_module(module)
        modules.append(module)

    BlobRef.model_rebuild()

    seen_ids: t.Set[int] = set()
    for module in modules:
        for model in _iter_rebuildable_models(module):
            if id(model) in seen_ids:
                continue

            seen_ids.add(id(model))
            model.model_rebuild()
