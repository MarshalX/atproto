## String Formats

The AT Protocol defines several string formats that are used throughout the protocol. This page describes these formats and how to validate them in your code.

### Overview

The SDK provides optional strict validation for AT Protocol string formats. By default, validation is disabled for performance reasons, but you can enable it when needed.

### Validation Examples

Using `Handle` as an example, here are the four main validation cases:

```python
from pydantic import TypeAdapter
from atproto_client.models.string_formats import Handle

HandleAdapter = TypeAdapter(Handle)

# Case 1: Valid handle without validation (passes)
handle1 = HandleAdapter.validate_python("alice.bsky.social")

# Case 2: Valid handle with validation (passes)
handle2 = HandleAdapter.validate_python(
    "alice.bsky.social",
    context={"strict_string_format": True}
)

# Case 3: Invalid handle without validation (passes)
handle3 = HandleAdapter.validate_python("not a valid handle!")

# Case 4: Invalid handle with validation (raises ValidationError)
try:
    HandleAdapter.validate_python(
        "not a valid handle!",
        context={"strict_string_format": True}
    )
except ValidationError as e:
    print("Validation failed:", e)
```

### Supported String Formats

The SDK supports validation of the following string formats:

:::{attention}
These formats are a working empirical understanding of the required formats based on the following resources:

- https://atproto.com/specs/lexicon

- https://github.com/bluesky-social/atproto/tree/main/interop-test-files/syntax

:::


#### Handle
A handle must be a valid domain name (e.g., `user.bsky.social`):
- 2+ segments separated by dots
- ASCII alphanumeric characters and hyphens only
- 1-63 chars per segment
- Max 253 chars total
- Last segment cannot start with a digit

#### DID (Decentralized Identifier)
A DID follows the pattern `did:method:identifier`:
- Method must be lowercase letters
- Identifier allows alphanumeric chars, dots, underscores, hyphens, and percent
- Max 2KB length
- No /?#[]@ characters allowed

#### NSID (Namespaced Identifier)
An NSID must have:
- 3+ segments separated by dots
- Reversed domain name (lowercase alphanumeric + hyphen)
- Name segment (letters only)
- Max 317 chars total
- No segments ending in numbers
- No @_*#! special characters
- Max 63 chars per segment

#### AT-URI
An AT-URI must follow the pattern `at://authority/collection/record-key`:
- Starts with `at://`
- Contains handle or DID
- Optional /collection/record-key path
- Max 8KB length
- No query parameters or fragments

#### CID (Content Identifier)
Must be:
- Minimum 8 characters
- Alphanumeric characters and plus signs only

#### DateTime
Requirements:
- Must use uppercase T as time separator
- Must include seconds (HH:MM:SS)
- Must have timezone (Z or ±HH:MM)
- No -00:00 timezone allowed
- Valid fractional seconds format if used
- No whitespace allowed

#### TID (Temporal ID)
Must be:
- Exactly 13 characters
- Only lowercase letters and numbers 2-7
- First byte's high bit (0x40) must be 0

#### Record Key
A record key must:
- Be 1-512 characters
- Contain only alphanumeric chars, dots, underscores, colons, tildes, or hyphens
- Not be "." or ".."

#### URI
Requirements:
- Must have a scheme starting with a letter
- Must have authority (netloc) or path/query/fragment
- Max 8KB length
- No spaces allowed
- Must follow RFC-3986 format

#### Language
Must match pattern:
- 2-3 letter language code or 'i'
- Optional subtag with alphanumeric chars and hyphens

### Using Validation in Your Code

There are two ways to enable validation:

1. Using `get_or_create` with `strict_string_format=True`:

```python
from atproto_client.models.utils import get_or_create
from atproto_client.models.string_formats import Handle
from pydantic import BaseModel

class MyModel(BaseModel):
    handle: Handle

data = {"handle": "alice.bsky.social"}
model = get_or_create(data, MyModel, strict_string_format=True)
```

2. Using Pydantic's validation context:

```python
from pydantic import BaseModel
from atproto_client.models.string_formats import Handle

class MyModel(BaseModel):
    handle: Handle

model = MyModel.model_validate(
    {"handle": "alice.bsky.social"},
    context={"strict_string_format": True}
)
```

When validation is disabled (the default), any string value will be accepted. When enabled, the values must conform to the above validation rules, or else a `ValidationError` will be raised.
