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

from atproto_codegen.models import builder

RUFF_CONFIG_PATH = Path(__file__).parent.joinpath('ruff_generated.toml')


class RuffNotFoundError(FileNotFoundError):
    """Ruff is needed to format generated code but is not installed."""


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

    Ruff resolves the per-file-ignores of :obj:`RUFF_CONFIG_PATH` against the working directory,
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
    options = [f'--config={RUFF_CONFIG_PATH}']
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


def get_file_path_parts(nsid: NSID) -> t.List[str]:
    return [*nsid.segments[:-1], f'{convert_camel_case_to_snake_case(nsid.name)}.py']


def get_import_path_old(nsid: NSID) -> str:
    return '.'.join([*nsid.segments[:-1], f'{convert_camel_case_to_snake_case(nsid.name)}'])


def get_import_path(nsid: NSID) -> str:
    nsid_parts = nsid.segments[:-1] + camel_case_split(nsid.name)
    return ''.join([p.capitalize() for p in nsid_parts])


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


def sort_dict_by_key(d: dict) -> dict:
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


def get_def_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}'


def get_record_model_name(_: t.Optional[str] = None) -> str:
    return 'Record'


def get_model_path(nsid: NSID, method_name: str) -> str:
    # ALL scope because a reference may point into a lexicon that is resolved against but not emitted,
    # and only the record database tells us that "#main" is named "Record" rather than "Main"
    record_models_for_nsid = builder.build_record_models(scope=builder.Scope.ALL).get(nsid, {})
    is_main_record_model = method_name == 'Main' and record_models_for_nsid.get('main')

    # edge case since we name classes "Record" for record types,
    # but references in schemes are still pointer to #main ("Main"),
    # so we need to rename Main to Record here
    model_name = get_record_model_name() if is_main_record_model else get_def_model_name(method_name)

    return f'models.{get_import_path(nsid)}.{model_name}'


def _resolve_nsid_ref(nsid: NSID, ref: str, *, local: bool = False) -> t.Tuple[str, str]:
    """Return the path to the model and model name."""
    if '#' in ref:
        ref_nsid_str, def_name = ref.split('#', 1)
        def_name = get_def_model_name(def_name)

        try:
            ref_nsid = NSID.from_str(ref_nsid_str)
            return get_model_path(ref_nsid, def_name), def_name
        except InvalidNsidError:
            if local:
                return def_name, def_name
            return get_model_path(nsid, def_name), def_name
    else:
        ref_nsid = NSID.from_str(ref)
        def_name = get_def_model_name(nsid.name)

        if local:
            return def_name, def_name

        # FIXME(MarshalX): Is it works well? ;d
        return get_model_path(ref_nsid, 'Main'), def_name
