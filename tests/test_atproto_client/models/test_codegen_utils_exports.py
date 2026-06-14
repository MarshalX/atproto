from atproto_client.models import models_loader
from atproto_codegen.models import generator


def test_codegen_utils_exports_in_sync() -> None:
    # This guards the two copies against drifting apart.
    assert generator._UTILS_EXPORTS == models_loader._UTILS_EXPORTS
