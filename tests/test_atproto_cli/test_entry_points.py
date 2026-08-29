import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'atproto_cli', *args], capture_output=True, text=True, check=False
    )


def test_module_is_executable() -> None:
    """`python -m atproto_cli` works alongside the `atp` and `atproto` scripts."""
    result = _run('--help')

    assert result.returncode == 0
    assert 'CLI of AT Protocol SDK for Python' in result.stdout


def test_subcommands_are_reachable() -> None:
    result = _run('gen', 'custom', '--help')

    assert result.returncode == 0
    assert '--package' in result.stdout
