import keyword
import re
import shutil
import subprocess
import sys
import sysconfig
import typing as t
from functools import cache
from pathlib import Path

from atproto_core.exceptions import InvalidNsidError
from atproto_core.nsid import NSID
from atproto_lexicon.models import LexDefinitionType

from atproto_codegen.config import get_config
from atproto_codegen.consts import INPUT_DICT, INPUT_MODEL, OUTPUT_MODEL, PARAMS_DICT, PARAMS_MODEL
from atproto_codegen.diagnostics import warn
from atproto_codegen.exceptions import RuffNotFoundError, UnresolvedReferenceError
from atproto_codegen.models import builder

RUFF_CONFIG_PATH = Path(__file__).parent.joinpath('ruff_generated.toml')

_VT = t.TypeVar('_VT')


@cache
def find_ruff() -> str:
    """Return the path to the Ruff binary.

    Looks in the running interpreter's script directories before falling back to ``PATH``, so a
    Ruff installed into the active virtual environment wins over an unrelated global one.

    Raises:
        RuffNotFoundError: Ruff is not installed.
    """
    executable = f'ruff{sysconfig.get_config_var("EXE")}'
    script_dirs = [
        sysconfig.get_path('scripts'),
        sysconfig.get_path('scripts', vars={'base': sys.base_prefix}),
    ]

    for script_dir in script_dirs:
        if not script_dir:
            continue

        candidate = Path(script_dir, executable)
        if candidate.is_file():
            return str(candidate)

    found = shutil.which(executable)
    if found is None:
        raise RuffNotFoundError(
            'Ruff is required to format generated code but was not found. Install it with `pip install ruff`.'
        )

    return found


def format_code(path: Path, quiet: bool = True, root: t.Optional[Path] = None) -> None:
    """Format generated code under the generator's own Ruff settings.

    Ruff resolves the per-file-ignores of ``RUFF_CONFIG_PATH`` against the working directory,
    so it runs from the generated package root rather than from wherever codegen was invoked.

    Args:
        path: File or directory to format.
        quiet: Suppress Ruff's own output.
        root: Generated package root. Defaults to the directory being formatted.

    Raises:
        RuffNotFoundError: Ruff is not installed.
    """
    if not isinstance(path, Path):
        return

    ruff = find_ruff()
    options = [f'--config={RUFF_CONFIG_PATH}', '--no-cache']
    if quiet:
        options.append('--quiet')

    cwd = root or (path if path.is_dir() else path.parent)

    # per-file-ignores are matched against the path as given
    try:
        target = path.relative_to(cwd)
    except ValueError:
        target = path

    def run(*args: str) -> None:
        # check=False: `ruff check` exits non-zero on leftover unfixable lints, which is fine here
        subprocess.run([ruff, *args, *options, str(target)], cwd=cwd, check=False)  # noqa: S603

    run('format')
    run('check', '--fix')
    run('format')


def append_code(filepath: Path, code: str) -> None:
    _write_code(filepath, code, append=True)


def write_code(filepath: Path, code: str) -> None:
    _write_code(filepath, code)


def _write_code(filepath: Path, code: str, *, append: bool = False) -> None:
    filepath.parent.mkdir(exist_ok=True, parents=True)

    mode = 'w'
    if append:
        mode = 'a'

    with open(filepath, mode=mode, encoding='UTF-8') as f:
        f.write(code)


def to_identifier(name: str) -> str:
    """Turn a lexicon name into a valid Python identifier that is not a keyword.

    Mirrored by ``atproto_client.models.models_loader._to_module_name``, which locates the generated
    modules at runtime. Keep the two in sync!
    """
    identifier = re.sub(r'\W', '_', name)
    if not identifier or identifier[0].isdigit():
        identifier = f'_{identifier}'
    if keyword.iskeyword(identifier):
        identifier = f'{identifier}_'

    return identifier


def to_pascal_case(parts: t.Iterable[str]) -> str:
    """Join name parts into a class name, dropping the characters an identifier can not hold."""
    words = [word for part in parts for word in re.split(r'[^a-zA-Z0-9]+', part) if word]
    return ''.join(word.capitalize() for word in words)


def to_one_line(text: str) -> str:
    """Collapse whitespace so that the text can not leave the comment it is written into."""
    return ' '.join(text.split())


def to_docstring_text(text: str) -> str:
    """Make the text safe to place between triple double quotes."""
    return to_one_line(text).replace('\\', '\\\\').replace('"""', '\\"\\"\\"')


def get_module_path_parts(nsid: NSID) -> t.List[str]:
    """Return the package path and the module name a lexicon is generated into."""
    module_name = to_identifier(convert_camel_case_to_snake_case(nsid.name))
    return [*(to_identifier(segment) for segment in nsid.segments[:-1]), module_name]


def get_file_path_parts(nsid: NSID) -> t.List[str]:
    *packages, module_name = get_module_path_parts(nsid)
    return [*packages, f'{module_name}.py']


def _get_plain_alias(nsid: NSID) -> str:
    return to_pascal_case([*nsid.segments[:-1], *camel_case_split(nsid.name)])


def _get_distinct_alias(nsid: NSID) -> str:
    # keeps the segment boundaries, which the plain alias loses: `a.bC` and `a.b.c` are both `ABC`
    parts = [*([segment] for segment in nsid.segments[:-1]), camel_case_split(nsid.name)]
    return '_'.join(to_pascal_case(part) for part in parts)


def build_aliases(nsids: t.Iterable[NSID]) -> t.Dict[NSID, str]:
    """Map lexicons to the names their model modules are exposed under.

    Lexicons whose plain aliases collide keep it only for the one with the fewest segments.
    """
    by_alias: t.Dict[str, t.List[NSID]] = {}
    for nsid in nsids:
        by_alias.setdefault(_get_plain_alias(nsid), []).append(nsid)

    aliases = {}
    for alias, group in by_alias.items():
        first, *rest = sorted(group, key=lambda nsid: (len(nsid.segments), str(nsid)))
        aliases[first] = alias
        aliases.update({nsid: _get_distinct_alias(nsid) for nsid in rest})

    return aliases


def get_import_path(nsid: NSID) -> str:
    return builder.get_alias(nsid) or _get_plain_alias(nsid)


def convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def camel_case_split(string: str) -> t.List[str]:
    return ''.join(['_' + x if x.isupper() else x for x in string]).split('_')


def gen_description_by_camel_case_name(name: str) -> str:
    words = camel_case_split(name)
    words = [w.lower() for w in words]
    words[0] = words[0].capitalize()
    return ' '.join(words)


def sort_dict_by_key(d: t.Dict[str, _VT]) -> t.Dict[str, _VT]:
    return dict(sorted(d.items()))


def get_code_intent(level: int) -> str:
    return ' ' * 4 * level


def join_code(lines: t.List[str]) -> str:
    return '\n'.join(lines)


def get_sync_async_keywords(*, sync: bool) -> t.Tuple[str, str]:
    definition, call = 'async ', 'await '
    if sync:
        definition, call = '', ''

    return definition, call


def capitalize_first_symbol(string: str) -> str:
    if string and string[0].islower():
        chars = list(string[1:])
        chars.insert(0, string[0].upper())
        return ''.join(chars)

    return string


#: Names every generated model module resolves annotations with. A class of the same name would replace them.
_RESERVED_CLASS_NAMES = frozenset({'BlobRef', 'CIDType', 'Field', 'UnknownInputType', 'UnknownType'})


_RECORD_CLASS_NAMES = frozenset({'Record', 'GetRecordResponse', 'ListRecordsResponse', 'CreateRecordResponse'})
_PARAMS_CLASS_NAMES = frozenset({PARAMS_MODEL, PARAMS_DICT})
#: Classes a model module defines for the main definition of its lexicon, by the type of that definition.
_MODULE_CLASS_NAMES = {
    LexDefinitionType.RECORD: _RECORD_CLASS_NAMES,
    LexDefinitionType.QUERY: _PARAMS_CLASS_NAMES | {OUTPUT_MODEL},
    LexDefinitionType.PROCEDURE: _PARAMS_CLASS_NAMES | {INPUT_MODEL, INPUT_DICT, OUTPUT_MODEL},
    LexDefinitionType.SUBSCRIPTION: _PARAMS_CLASS_NAMES,
}
_DEF_SUFFIX = 'Def'


def get_def_model_name(method_name: str, nsid: t.Optional[NSID] = None) -> str:
    """Return the class name of a definition.

    Args:
        method_name: Name of the definition.
        nsid: Lexicon of the definition. Given, the name is kept apart from the classes its module defines.
    """
    name = to_identifier(capitalize_first_symbol(method_name))
    if name in _RESERVED_CLASS_NAMES:
        name = f'{name}_'

    main = builder.get_defs(nsid).get('main') if nsid is not None else None
    if main is not None and name in _MODULE_CLASS_NAMES.get(main.type, frozenset()):
        name = f'{name}{_DEF_SUFFIX}'

    return name


def get_record_model_name(_: t.Optional[str] = None) -> str:
    return 'Record'


def get_model_path(nsid: NSID, method_name: str) -> str:
    is_main_record_model = method_name == 'Main' and builder.is_record(nsid)

    # edge case since we name classes "Record" for record types,
    # but references in schemes are still pointer to #main ("Main"),
    # so we need to rename Main to Record here
    model_name = get_record_model_name() if is_main_record_model else get_def_model_name(method_name)
    alias = get_import_path(nsid)

    if not builder.reference_model_exists(nsid, alias, model_name):
        config = get_config()
        where = 'the lexicons being generated'
        if not config.is_self_gen:
            where += f" or the installed '{config.base_package}' package"
        raise UnresolvedReferenceError(
            f"'{nsid}' (model '{model_name}') is referenced but not found in {where}. "
            'Add its lexicon to the lexicon directory.'
        )

    return f'models.{alias}.{model_name}'


def _check_emitted_def_exists(nsid: NSID, ref: str) -> None:
    ref_nsid_str, _, def_name = ref.partition('#')
    target = NSID.from_str(ref_nsid_str) if ref_nsid_str else nsid
    if target in builder.emitted_nsids(get_config()) and (def_name or 'main') not in builder.get_defs(target):
        raise UnresolvedReferenceError(f"'{ref}' names a definition that '{target}' does not have.")


def resolve_ref(nsid: NSID, ref: str) -> t.Optional[str]:
    """Return the path to the model a reference names.

    Returns:
        :obj:`None` if the reference can not be resolved and the run skips invalid input.

    Raises:
        UnresolvedReferenceError: The reference can not be resolved and the run is strict.
    """
    try:
        _check_emitted_def_exists(nsid, ref)
        return _resolve_nsid_ref(nsid, ref)[0]
    except InvalidNsidError as e:
        error = UnresolvedReferenceError(f"'{ref}' is not a reference.")
        error.__cause__ = e
    except UnresolvedReferenceError as e:
        error = e

    if not get_config().skip_invalid:
        raise error

    warn(f"Unresolved reference '{ref}' in {nsid}: {error}")
    return None


def _resolve_nsid_ref(nsid: NSID, ref: str, *, local: bool = False) -> t.Tuple[str, str]:
    """Return the path to the model and model name."""
    if '#' in ref:
        ref_nsid_str, def_name = ref.split('#', 1)

        try:
            ref_nsid = NSID.from_str(ref_nsid_str)
        except InvalidNsidError:
            ref_nsid = nsid
            if local:
                def_name = get_def_model_name(def_name, nsid)
                return def_name, def_name

        def_name = get_def_model_name(def_name, ref_nsid)
        return get_model_path(ref_nsid, def_name), def_name
    ref_nsid = NSID.from_str(ref)
    def_name = get_def_model_name(nsid.name)

    if local:
        return def_name, def_name

    # FIXME(MarshalX): Is it works well? ;d
    return get_model_path(ref_nsid, 'Main'), def_name
