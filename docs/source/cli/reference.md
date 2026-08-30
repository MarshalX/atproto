# Code generator reference

The API behind the [`atp` CLI](index.md). Reach for this when generation is a step in a build script rather than something you type, or when you want to know exactly what a flag does.

Everything is driven by one object. [CodegenConfig](#atproto_codegen.config.CodegenConfig) is frozen and hashable, which is what lets the parsed lexicon databases be cached per run instead of globally, so two runs with different lexicons can happen in the same process.

```python
from pathlib import Path

from atproto_codegen.config import CodegenConfig

config = CodegenConfig(
    emit_lexicon_dirs=(Path('./lexicons'),),
    ref_lexicon_dirs=(Path('./sdk-lexicons'),),
    output_dir=Path('./my_pkg'),
    package='my_pkg',
)
```

## Configuration

```{eval-rst}
.. automodule:: atproto_codegen.config
   :members:
   :undoc-members:
   :show-inheritance:
```

## Generators

Each of these takes a config and writes part of the package. `atp gen custom` calls all three in order.

```{eval-rst}
.. autofunction:: atproto_codegen.models.generator.generate_models

.. autofunction:: atproto_codegen.namespaces.generator.generate_namespaces

.. autofunction:: atproto_codegen.subscriptions.generator.generate_subscriptions
```

## Formatting

Generated code is formatted by shelling out to Ruff with a config the generator owns, so the output does not inherit the style of whatever project the output directory sits in. Ruff is deliberately not a declared dependency of the SDK.

```{eval-rst}
.. automodule:: atproto_codegen.utils
   :members:
   :undoc-members:
   :show-inheritance:
```
