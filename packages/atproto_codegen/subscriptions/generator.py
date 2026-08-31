import typing as t

from atproto_core.nsid import NSID
from atproto_lexicon.models import LexSubscription

from atproto_codegen.config import CodegenConfig, get_config, use_config
from atproto_codegen.consts import DISCLAIMER, PARAMS_MODEL
from atproto_codegen.models import builder
from atproto_codegen.utils import (
    _resolve_nsid_ref,
    convert_camel_case_to_snake_case,
    format_code,
    get_import_path,
    join_code,
    write_code,
)
from atproto_codegen.utils import get_code_intent as _

_SUBSCRIPTIONS_FILENAME = 'subscriptions.py'


def _message_alias(nsid: NSID) -> str:
    return f'{get_import_path(nsid)}Message'


def _type_map_name(nsid: NSID) -> str:
    return f'{convert_camel_case_to_snake_case(get_import_path(nsid)).upper()}_MESSAGE_TYPE_TO_MODEL'


def _parse_function_name(nsid: NSID) -> str:
    return f'parse_{convert_camel_case_to_snake_case(get_import_path(nsid))}_message'


def _refs(definition: LexSubscription) -> t.List[str]:
    if not definition.message or not definition.message.schema_:
        return []

    return list(getattr(definition.message.schema_, 'refs', []) or [])


def _get_imports(config: CodegenConfig) -> str:
    base = config.base_package

    return join_code(
        [
            DISCLAIMER,
            'import typing as t',
            '',
            f'from {config.package} import models',
            f'from {base}.models.utils import get_model_as_dict, get_or_create',
            'from atproto_subscription.client import AsyncSubscriptionClient, SubscriptionClient',
            '',
            'if t.TYPE_CHECKING:',
            f'{_(1)}from atproto_subscription.frames import MessageFrame',
        ]
    )


def _generate_message_types(nsid: NSID, definition: LexSubscription) -> t.List[str]:
    refs = _refs(definition)
    model_paths = [_resolve_nsid_ref(nsid, ref)[0] for ref in refs]

    lines = [f'#: Messages of the ``{nsid}`` subscription.', f'{_message_alias(nsid)} = t.Union[']
    lines.extend(f"{_(1)}'{path}'," for path in model_paths)
    lines.append(']')

    lines.append(f'{_type_map_name(nsid)} = {{')
    lines.extend(f"{_(1)}'{ref}': {path}," for ref, path in zip(refs, model_paths))
    lines.append('}')

    return lines


def _generate_parse_function(nsid: NSID) -> t.List[str]:
    alias = _message_alias(nsid)

    return [
        f"def {_parse_function_name(nsid)}(message: 'MessageFrame') -> '{alias}':",
        f'{_(1)}"""Parse a message frame of ``{nsid}`` into its model.',
        '',
        f'{_(1)}Args:',
        f'{_(2)}message: Message frame.',
        '',
        f'{_(1)}Returns:',
        f'{_(2)}:obj:`.{alias}`: Corresponding message model.',
        f'{_(1)}"""',
        # TODO(MarshalX): fix return type in get_or_create instead of casting
        f"{_(1)}return t.cast('{alias}', get_or_create(message.body, {_type_map_name(nsid)}[message.type]))",
    ]


def _generate_client(nsid: NSID, *, sync: bool) -> t.List[str]:
    prefix = '' if sync else 'Async'
    base_class = 'SubscriptionClient' if sync else 'AsyncSubscriptionClient'
    params_model = f'models.{get_import_path(nsid)}.{PARAMS_MODEL}'

    return [
        f'class {prefix}{get_import_path(nsid)}Client({base_class}):',
        f'{_(1)}"""Client of the ``{nsid}`` subscription.',
        '',
        f'{_(1)}Args:',
        f'{_(2)}base_uri: Base websocket URI, ending in ``/xrpc``.',
        f'{_(2)}params: Parameters model.',
        f'{_(2)}recv_timeout: Reconnect after this many seconds of inactivity.',
        f'{_(1)}"""',
        '',
        f'{_(1)}def __init__(',
        f'{_(2)}self,',
        f'{_(2)}base_uri: str,',
        f"{_(2)}params: t.Optional[t.Union[dict, '{params_model}']] = None,",
        f'{_(2)}recv_timeout: t.Optional[float] = None,',
        f'{_(1)}) -> None:',
        f'{_(2)}params_model = get_or_create(params, {params_model})',
        f'{_(2)}super().__init__(',
        f"{_(3)}method='{nsid}',",
        f'{_(3)}base_uri=base_uri,',
        f'{_(3)}params=get_model_as_dict(params_model) if params_model else None,',
        f'{_(3)}recv_timeout=recv_timeout,',
        f'{_(2)})',
    ]


def generate_subscriptions(config: t.Optional[CodegenConfig] = None) -> None:
    """Generate the message models and clients of every emitted subscription."""
    with use_config(config or get_config()) as active:
        blocks: t.List[str] = []

        for nsid, defs in builder.build_subscriptions(active).items():
            for definition in defs.values():
                if not isinstance(definition, LexSubscription) or not _refs(definition):
                    continue

                blocks.extend(_generate_message_types(nsid, definition))
                blocks.append('')
                blocks.extend(_generate_parse_function(nsid))
                blocks.append('')

                # a subprotocol means a bespoke transport, so the standard framing client does not apply
                if definition.subprotocol:
                    continue

                for sync in (True, False):
                    blocks.extend(_generate_client(nsid, sync=sync))
                    blocks.append('')

        filepath = active.output_dir.joinpath(_SUBSCRIPTIONS_FILENAME)
        write_code(filepath, join_code([_get_imports(active), '', *blocks]))
        format_code(filepath, root=active.output_dir)
