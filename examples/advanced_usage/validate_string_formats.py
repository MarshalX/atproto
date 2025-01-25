from atproto_client.models import string_formats
from pydantic import TypeAdapter, ValidationError

some_good_handle = 'test.bsky.social'
some_bad_handle = 'invalid@ @handle'

strict_validation_context = {'strict_string_format': True}
HandleTypeAdapter = TypeAdapter(string_formats.Handle)

assert string_formats._OPT_IN_KEY == 'strict_string_format'

# values will not be validated if not opting in
sneaky_bad_handle = HandleTypeAdapter.validate_python(some_bad_handle)

assert sneaky_bad_handle == some_bad_handle

print(f'{sneaky_bad_handle=}\n\n')

# values will be validated if opting in
validated_good_handle = HandleTypeAdapter.validate_python(some_good_handle, context=strict_validation_context)

assert validated_good_handle == some_good_handle

print(f'{validated_good_handle=}\n\n')

try:
    print('Trying to validate a bad handle with strict validation...')
    HandleTypeAdapter.validate_python(some_bad_handle, context=strict_validation_context)
except ValidationError as e:
    print(e)
