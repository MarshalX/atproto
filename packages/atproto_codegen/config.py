import typing as t
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
from pathlib import Path

_PACKAGES_DIR = Path(__file__).parent.parent.absolute()

DEFAULT_LEXICON_DIR = _PACKAGES_DIR.parent.joinpath('lexicons')
DEFAULT_PACKAGE = 'atproto_client'
DEFAULT_OUTPUT_DIR = _PACKAGES_DIR.joinpath(DEFAULT_PACKAGE)


@dataclass(frozen=True)
class CodegenConfig:
    """Inputs and outputs of a single codegen run.

    Frozen and hashable so that parsed lexicon databases can be cached per run instead of
    globally, which is what allows two runs with different lexicons in one process.
    """

    emit_lexicon_dirs: t.Tuple[Path, ...] = (DEFAULT_LEXICON_DIR,)
    """Lexicons to generate code for."""

    package: str = DEFAULT_PACKAGE
    """Import name of the generated package."""

    output_dir: Path = DEFAULT_OUTPUT_DIR
    """Filesystem root of the generated package."""

    base_package: str = DEFAULT_PACKAGE
    """Package providing the hand-written base classes the generated code builds on.

    References out of the emitted lexicons resolve into its models, so they must name something it defines.
    """

    @property
    def models_output_dir(self) -> Path:
        return self.output_dir.joinpath('models')

    @property
    def namespaces_output_dir(self) -> Path:
        return self.output_dir.joinpath('namespaces')

    @property
    def models_package(self) -> str:
        return f'{self.package}.models'

    @property
    def is_self_gen(self) -> bool:
        """Whether the run targets the SDK's own package."""
        return self.package == self.base_package

    def with_overrides(self, **kwargs: t.Any) -> 'CodegenConfig':
        return replace(self, **kwargs)

    def module_import_path(self, models_subdir: Path) -> str:
        """Return the dotted import path of a directory inside the generated models package."""
        rel = models_subdir.relative_to(self.models_output_dir)
        return '.'.join([self.models_package, *rel.parts])

    def nsid_segments(self, models_subdir: Path) -> t.List[str]:
        """Return the NSID segments a directory inside the generated models package stands for."""
        return list(models_subdir.relative_to(self.models_output_dir).parts)


_active: ContextVar[t.Optional[CodegenConfig]] = ContextVar('atproto_codegen_config', default=None)


def get_config() -> CodegenConfig:
    """Return the config of the run in progress, or the SDK's own defaults outside a run."""
    return _active.get() or CodegenConfig()


@contextmanager
def use_config(config: CodegenConfig) -> t.Generator[CodegenConfig, None, None]:
    """Activate a config for the duration of a run."""
    token = _active.set(config)
    try:
        yield config
    finally:
        _active.reset(token)
