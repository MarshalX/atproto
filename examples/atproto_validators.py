# /// script
# dependencies = ["rich", "pydantic"]
# ///

# run this file from repo root with `uv run examples/atproto_validators.py`

import re
import string
from datetime import datetime
from typing import Annotated, Callable, Union
from urllib.parse import urlparse

from pydantic import BaseModel, BeforeValidator, Field, TypeAdapter, ValidationError, ValidationInfo

DOMAIN_RE = re.compile(r'([a-z0-9][a-z0-9-]{0,62}(?<!-)\.){1,}[a-z][a-z0-9-]*(?<!-)')
DID_RE = re.compile(r'did:[a-z]+:[A-Za-z0-9._%:-]{1,2048}(?<!:)')
NSID_RE = re.compile(r'(?![0-9])((?!-)[a-z0-9-]{1,63}(?<!-)\.){2,}[a-zA-Z]{1,63}')
LANG_RE = re.compile(r'^(i|[a-z]{2,3})(-[A-Za-z0-9-]+)?$')
RKEY_RE = re.compile(r'^[A-Za-z0-9._:~-]{1,512}$')
TID_RE = re.compile(rf'^[{string.ascii_lowercase}234567]{{13}}$')
CID_RE = re.compile(r'^[A-Za-z0-9+]{8,}$')
AT_URI_RE = re.compile(r'at://[^/]+(/[^/]+(/[^/]+)?)?')


def only_validate_if_strict(validate_fn: Callable) -> Callable:
    def wrapper(v: str, info: ValidationInfo) -> str:
        if not (info and info.context and info.context.get('strict', False)):
            return v
        return validate_fn(v, info)

    return wrapper


@only_validate_if_strict
def validate_handle(v: str, info: ValidationInfo) -> str:
    if not DOMAIN_RE.match(v.lower()) or len(v) > 253:
        return v
    if not DOMAIN_RE.match(v.lower()) or len(v) > 253:
        raise ValueError('Invalid handle')
    return v


@only_validate_if_strict
def validate_did(v: str, info: ValidationInfo) -> str:
    if not DID_RE.match(v):
        raise ValueError('Invalid DID')
    return v


@only_validate_if_strict
def validate_nsid(v: str, info: ValidationInfo) -> str:
    if not NSID_RE.match(v) or '.' not in v or len(v) > 317:
        return v
    if not NSID_RE.match(v) or '.' not in v or len(v) > 317:
        raise ValueError('Invalid NSID')
    return v


@only_validate_if_strict
def validate_language(v: str, info: ValidationInfo) -> str:
    if not LANG_RE.match(v):
        raise ValueError('Invalid language code')
    return v


@only_validate_if_strict
def validate_record_key(v: str, info: ValidationInfo) -> str:
    if v in ('.', '..') or not RKEY_RE.match(v):
        raise ValueError('Invalid record key')
    return v


@only_validate_if_strict
def validate_cid(v: str, info: ValidationInfo) -> str:
    if not CID_RE.match(v):
        raise ValueError('Invalid CID')
    return v


@only_validate_if_strict
def validate_at_uri(v: str, info: ValidationInfo) -> str:
    if len(v) >= 8 * 1024 or '/./' in v or '/../' in v or v.endswith(('/.', '/..')):
        raise ValueError('Invalid AT-URI')
    if not AT_URI_RE.match(v):
        raise ValueError('Invalid AT-URI format')
    return v


@only_validate_if_strict
def validate_datetime(v: str, info: ValidationInfo) -> str:
    # could just use pydantic_extra_types.pendulum_dt.DateTime but
    # see https://github.com/pydantic/pydantic-extra-types/issues/239
    if 'T' not in v or not any(v.endswith(x) for x in ('Z', '+00:00')):
        raise ValueError('Invalid datetime format')
    try:
        datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    except ValueError:
        raise ValueError('Invalid datetime format') from None


@only_validate_if_strict
def validate_tid(v: str, info: ValidationInfo) -> str:
    if not TID_RE.match(v):
        raise ValueError('Invalid TID format')
    if ord(v[0]) & 0x40:
        raise ValueError('Invalid TID: high bit cannot be 1')
    return v


@only_validate_if_strict
def validate_uri(v: str, info: ValidationInfo) -> str:
    if len(v) >= 8 * 1024 or ' ' in v:
        raise ValueError('Invalid URI')
    parsed = urlparse(v)
    if not (
        parsed.scheme
        and parsed.scheme[0].isalpha()
        and (parsed.netloc or parsed.path or parsed.query or parsed.fragment)
    ):
        raise ValueError('Invalid URI')
    return v


Handle = Annotated[str, BeforeValidator(validate_handle)]
Did = Annotated[str, BeforeValidator(validate_did)]
Nsid = Annotated[str, BeforeValidator(validate_nsid)]
Language = Annotated[str, BeforeValidator(validate_language)]
RecordKey = Annotated[str, BeforeValidator(validate_record_key)]
Cid = Annotated[str, BeforeValidator(validate_cid)]
AtUri = Annotated[str, BeforeValidator(validate_at_uri)]
DateTime = Annotated[str, BeforeValidator(validate_datetime)]  # see pydantic-extra-types #239
Tid = Annotated[str, BeforeValidator(validate_tid)]
Uri = Annotated[str, BeforeValidator(validate_uri)]

# Any valid ATProto string format
ATProtoString = Annotated[
    Union[Handle, Did, Nsid, AtUri, Cid, DateTime, Tid, RecordKey, Uri, Language],
    Field(description='ATProto string format'),
]

# Example usage
if __name__ == '__main__':
    import random
    import string
    import time

    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table

    class Example(BaseModel):
        handle: Handle
        uri: AtUri
        datetime: DateTime
        generic_uri: Uri
        any_format: ATProtoString

    console = Console()

    # Original validation examples
    console.print(
        Panel.fit(
            '[bold blue]ATProto Validators Demo[/bold blue]\n'
            '[dim]A demonstration of ATProto string format validation[/dim]',
            border_style='blue',
        )
    )

    # Example that will pass with strict validation
    valid_example_data = {
        'handle': 'jay.bsky.team',
        'uri': 'at://jay.bsky.team/app.bsky.feed.post/3kduixjeb2e2z',
        'datetime': '2024-03-15T09:42:31Z',
        'generic_uri': 'https://bsky.app/profile/jay.bsky.team/post/3kduixjeb2e2z',
        'any_format': 'did:plc:q6gjnaw2blty4criciuswz4k',
    }

    # A valid but unvalidated example
    valid = Example(**valid_example_data)
    console.print(
        Panel(
            Syntax(valid.model_dump_json(indent=2), 'json', theme='monokai'),
            title='[bold green]🍀 Luckily valid data[/bold green]',
            border_style='green',
        )
    )

    # Example that will fail without strict validation
    invalid_example = {
        'handle': 'jay.bsky.social!',
        'uri': 'https://bsky.app/profile/jay.bsky.team',
        'datetime': '2024-03-15 09:42:31',
        'generic_uri': 'bsky.app/profile/jay',
        'any_format': 'plc:q6gjnaw2blty4criciuswz4k',
    }

    invalid_but_passes = Example(**invalid_example)

    console.print(
        Panel(
            Syntax(invalid_but_passes.model_dump_json(indent=2), 'json', theme='monokai'),
            title='[bold yellow]⚠ Invalid data (non-strict mode)[/bold yellow]',
            border_style='yellow',
        )
    )

    # Opting into strict validation and failing
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Field')
    table.add_column('Value')
    table.add_column('Result')

    try:
        Example.model_validate(invalid_example, context={'strict': True})
    except ValidationError as e:
        seen_fields = set()
        for error in e.errors():
            if (field := str(error['loc'][0])) not in seen_fields:
                seen_fields.add(field)
                value = invalid_example[field]
                table.add_row(field, value, f'[red]❌ {error["msg"]}[/red]')

    console.print(Panel(table, title='[bold red]! Invalid data (strict mode)[/bold red]', border_style='red'))

    # Opting into strict validation and succeeding
    strictly_valid = Example.model_validate(valid_example_data, context={'strict': True})
    console.print(
        Panel(
            Syntax(strictly_valid.model_dump_json(indent=2), 'json', theme='monokai'),
            title='[bold green]✓ Strictly valid data[/bold green]',
            border_style='green',
        )
    )

    # Performance Testing Section

    def generate_random_data() -> dict:
        handle = f"{''.join(random.choices(string.ascii_lowercase, k=10))}.bsky.social"  # noqa: S311
        uri = f"at://{handle}.bsky.team/app.bsky.feed.post/{''.join(random.choices(string.ascii_lowercase + string.digits, k=13))}"  # noqa: S311
        datetime = f'2024-03-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z'  # noqa: S311
        generic_uri = f"https://{''.join(random.choices(string.ascii_lowercase, k=10))}.com/{''.join(random.choices(string.ascii_lowercase, k=5))}"  # noqa: S311
        any_format = f"did:plc:{''.join(random.choices(string.ascii_lowercase + string.digits, k=24))}"  # noqa: S311
        return {
            'handle': handle,
            'uri': uri,
            'datetime': datetime,
            'generic_uri': generic_uri,
            'any_format': any_format,
        }

    # Performance testing table
    N = 100_000
    console.print('\n')
    console.print(
        Panel.fit(
            '[bold blue]ATProto Validators Performance Test[/bold blue]\n'
            f'[dim]Testing validation performance across {N:,} strings[/dim]',
            border_style='blue',
        )
    )
    perf_table = Table(show_header=True, header_style='bold cyan')
    perf_table.add_column('Test Type')
    perf_table.add_column('Items')
    perf_table.add_column('Time (seconds)')
    perf_table.add_column('Items/second')

    # Test 1: Raw dictionary creation (no validation)
    start_time = time.time()
    raw_data = [generate_random_data() for _ in range(N)]
    raw_time = time.time() - start_time
    perf_table.add_row('Raw dictionaries', f'{N:,}', f'{raw_time:.2f}', f'{N/raw_time:,.0f}')

    # Test 2: Non-strict validation
    start_time = time.time()
    non_strict_data = TypeAdapter(list[Example]).validate_python([generate_random_data() for _ in range(N)])
    non_strict_time = time.time() - start_time
    perf_table.add_row('Skipped validation (default)', f'{N:,}', f'{non_strict_time:.2f}', f'{N/non_strict_time:,.0f}')

    # Test 3: Strict validation
    start_time = time.time()
    strict_data = TypeAdapter(list[Example]).validate_python(
        [generate_random_data() for _ in range(N)], context={'strict': True}
    )
    strict_time = time.time() - start_time
    perf_table.add_row('Opted-in to strict validation', f'{N:,}', f'{strict_time:.2f}', f'{N/strict_time:,.0f}')

    console.print(Panel(perf_table, title='[bold green]Performance Results[/bold green]', border_style='green'))
