import importlib
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_codegen.config import DEFAULT_LEXICON_DIR, CodegenConfig
from atproto_codegen.models.generator import generate_models

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()
PACKAGE = 'chained_pkg'


@pytest.fixture(scope='session')
def custom_package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[t.Any]:
    """Generate a package from the custom lexicons, import it, and yield its models root.

    Session-scoped because importing it registers its record types globally; re-importing would
    leave the registry pointing at classes from a previous import.
    """
    root = tmp_path_factory.mktemp('chained')
    generate_models(
        CodegenConfig(
            emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,),
            ref_lexicon_dirs=(DEFAULT_LEXICON_DIR,),
            output_dir=root.joinpath(PACKAGE),
            package=PACKAGE,
        )
    )

    sys.path.insert(0, str(root))
    # the package stays in sys.modules for the session: registering its records hands the registry
    # a reference to it, and unloading would leave that reference pointing at nothing
    yield importlib.import_module(f'{PACKAGE}.models')
