"""repro for issue #625: pydantic field warning"""
import warnings

# make pydantic warnings visible
warnings.filterwarnings('default', category=Warning)

# this should trigger the warning
from atproto import Client

print("✓ import successful, check for warnings above")
