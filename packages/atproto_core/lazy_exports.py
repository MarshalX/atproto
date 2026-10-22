import importlib
import sys
import typing as t


def lazy_exports(
    package_name: str,
    attributes: t.Mapping[str, t.Iterable[str]],
    modules: t.Optional[t.Mapping[str, str]] = None,
) -> t.Tuple[t.Callable[[str], t.Any], t.Callable[[], t.List[str]]]:
    """Build ``__getattr__`` and ``__dir__`` for a package that imports its exports on first access.

    Unknown names fall back to the package's submodules. Resolved values are cached on the package.

    Args:
        package_name: The package these belong to.
        attributes: Module to the names it exports under the same name.
        modules: Name to the module exported as is.
    """
    sources: t.Dict[str, t.Tuple[str, t.Optional[str]]] = {
        name: (module_name, name) for module_name, names in attributes.items() for name in names
    }
    for name, module_name in (modules or {}).items():
        sources[name] = (module_name, None)

    def __getattr__(name: str) -> t.Any:
        source = sources.get(name)
        if source is not None:
            module_name, attribute = source
            value = importlib.import_module(module_name)
            if attribute is not None:
                value = getattr(value, attribute)

            vars(sys.modules[package_name])[name] = value
            return value

        # dunders are import machinery probing the package, never a submodule
        if not name.startswith('_'):
            try:
                return importlib.import_module(f'{package_name}.{name}')
            except ModuleNotFoundError as e:
                if e.name != f'{package_name}.{name}':
                    raise

        raise AttributeError(f'module {package_name!r} has no attribute {name!r}')

    def __dir__() -> t.List[str]:
        return sorted({*vars(sys.modules[package_name]), *sources})

    return __getattr__, __dir__
