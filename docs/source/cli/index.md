# The atp CLI

Installing the SDK also installs a command-line tool that runs the code generator. It is the same generator the SDK uses on itself: the models, namespaces, and clients under `atproto_client/` are all produced by it from the JSON lexicons in `lexicons/`.

You need it for one of two reasons:

- You have **lexicons of your own** that are not baked into the SDK, and you want typed models and a working client for them. See [Custom lexicons](custom-lexicons.md).
- You are **working on the SDK itself** and need to regenerate after a lexicon update.

## Invoking it

Three spellings, all the same program:

```bash
atp --help
atproto --help
python -m atproto_cli --help
```

Commands accept unambiguous prefixes, so these are equivalent:

```bash
atp gen --lexicon-dir ./lexicons custom --output-dir ./my_pkg --package my_pkg
atp g   --lexicon-dir ./lexicons c      --output-dir ./my_pkg --package my_pkg
```

An ambiguous prefix fails rather than guessing: `atp gen a` matches both `all` and `async` and reports `Too many matches: all, async`.

`--silent` / `-s` on the root command suppresses progress output:

```bash
atp -s gen all
```

## Ruff is required

The generator formats everything it writes by shelling out to [Ruff](https://docs.astral.sh/ruff/), using a config it owns so the output does not pick up the style of whatever project the output directory happens to sit in.

Ruff is deliberately **not** a dependency of the SDK, and is only needed when generating. If it is missing you get a `RuffNotFoundError` telling you to install it:

```bash
pip install ruff
```

The generator looks in your interpreter's script directory first, then on `PATH`.

## atp gen

All generation lives under `gen`. One option belongs to the **group**, not to the subcommands:

`--lexicon-dir PATH`
: Directory of `.json` lexicon files to generate code for. Defaults to the SDK's own `lexicons/`.

:::{important}
`--lexicon-dir` must come **before** the subcommand, because it belongs to `gen` rather than to what follows it:

```bash
atp gen --lexicon-dir ./lexicons custom --output-dir ./my_pkg --package my_pkg
#       ^^^^^^^^^^^^^^^^^^^^^^^^ here    ^^^^^^ not after here
```

`atp gen custom --lexicon-dir ./lexicons ...` fails with `Error: '--lexicon-dir' is required. Pass it before the subcommand`.
:::

### atp gen custom

Generate a standalone, importable package from your own lexicons. This is the one you want if you are not working on the SDK itself. It has [its own page](custom-lexicons.md).

```bash
atp gen --lexicon-dir ./lexicons custom --output-dir ./my_pkg --package my_pkg
```

| Option                | Required | Meaning                                                                                                                    |
| --------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| `--output-dir PATH`   | yes      | Root of the package to generate. Created if it does not exist.                                                             |
| `--package NAME`      | yes      | Import name of the generated package. Must match the last path segment of `--output-dir` for the package to be importable. |
| `--no-client`         | no       | Emit models and namespaces only, no `client.py` / `async_client.py`.                                                       |

### atp gen all

Regenerate everything with the SDK's defaults: models, then namespaces, then subscriptions, then the async client. This is the SDK's own build step.

```bash
atp gen all
```

### atp gen models

```bash
atp gen models [--output-dir PATH]
```

`--output-dir` is the **package root**, not the models directory: models are written to its `models/` subdirectory.

### atp gen namespaces

```bash
atp gen namespaces [--output-dir PATH] [--sync-filename sync_ns.py] [--async-filename async_ns.py]
```

`--sync-filename` and `--async-filename` override the generated filenames and must end in `.py`.

### atp gen async

```bash
atp gen async
```

Regenerates `async_client.py` from `client.py` by rewriting the source of a hardcoded list of methods.

:::{warning}
This one is maintainer-only. It operates on the SDK's own `atproto_client/client/` files and ignores `--output-dir` and `--lexicon-dir` entirely. It will not do anything useful to a package you generated, since `atp gen custom` already emits both the sync and async sides.
:::

## Generating without the CLI

Every subcommand is a thin wrapper over a function you can call yourself. The unit of configuration is [CodegenConfig](#atproto_codegen.config.CodegenConfig), which is frozen and hashable so that two runs with different lexicons can happen in one process:

```python
from pathlib import Path

from atproto_codegen.config import CodegenConfig
from atproto_codegen.models.generator import generate_models
from atproto_codegen.namespaces.generator import generate_namespaces
from atproto_codegen.subscriptions.generator import generate_subscriptions

config = CodegenConfig(
    emit_lexicon_dirs=(Path('./lexicons'),),
    output_dir=Path('./my_pkg'),
    package='my_pkg',
)

generate_models(config)
generate_namespaces(config)
generate_subscriptions(config)
```

Useful when generation is a step in a build script rather than something you type. See the [code generator reference](reference.md) for the full API.

```{toctree}
:hidden:
:maxdepth: 1

custom-lexicons
reference
```
