import typing as t
from dataclasses import dataclass, field

from atproto_core.nsid import NSID
from atproto_lexicon.models import (
    LexDefinition,
    LexDefinitionType,
    LexiconDoc,
    LexRecord,
    LexXrpcProcedure,
    LexXrpcQuery,
)

from atproto_codegen.config import CodegenConfig, get_config
from atproto_codegen.models.builder import parse_lexicons

_VALID_LEX_DEF_TYPES = {LexDefinitionType.QUERY, LexDefinitionType.PROCEDURE, LexDefinitionType.RECORD}


def _filter_namespace_valid_definitions(definitions: t.Dict[str, LexDefinition]) -> t.Dict[str, LexDefinition]:
    result = {}

    for def_name, def_content in definitions.items():
        if def_content.type in _VALID_LEX_DEF_TYPES:
            result[def_name] = def_content

    return result


def get_definition_by_name(name: str, defs: t.Dict[str, LexDefinition]) -> LexDefinition:
    if name in defs:
        return defs[name]

    return defs['main']


@dataclass
class ObjectInfo:
    name: str
    nsid: NSID


@dataclass
class ProcedureInfo(ObjectInfo):
    definition: LexXrpcProcedure


@dataclass
class QueryInfo(ObjectInfo):
    definition: LexXrpcQuery


MethodInfo = t.Union[ProcedureInfo, QueryInfo]


@dataclass
class RecordInfo(ObjectInfo):
    definition: LexRecord


@dataclass
class NamespaceNode:
    children: t.Dict[str, 'NamespaceNode'] = field(default_factory=dict)
    objects: t.List[t.Union[ProcedureInfo, QueryInfo, RecordInfo]] = field(default_factory=list)


def _enrich_namespace_tree(root: NamespaceNode, nsid: NSID, defs: t.Dict[str, LexDefinition]) -> None:
    root_node = root

    segments_count = len(nsid.segments)
    for path_level, segment in enumerate(nsid.segments):
        # if method
        if path_level == segments_count - 1:
            definition = get_definition_by_name(segment, defs)

            info: t.Union[ProcedureInfo, QueryInfo, RecordInfo]
            if isinstance(definition, LexXrpcProcedure):
                info = ProcedureInfo(name=segment, nsid=nsid, definition=definition)
            elif isinstance(definition, LexXrpcQuery):
                info = QueryInfo(name=segment, nsid=nsid, definition=definition)
            elif isinstance(definition, LexRecord):
                info = RecordInfo(name=segment, nsid=nsid, definition=definition)
            else:
                raise RuntimeError(f'Unknown definition type: {definition.type}')

            # TODO(MarshalX): fake records as namespaces with methods to be able to reuse code of generator?

            root_node.objects.append(info)
            continue

        root_node = root_node.children.setdefault(segment, NamespaceNode())


def build_namespace_tree(lexicons: t.List[LexiconDoc]) -> NamespaceNode:
    namespace_tree = NamespaceNode()
    for lexicon in lexicons:
        defs = _filter_namespace_valid_definitions(lexicon.defs)
        if not defs:
            continue

        nsid = NSID.from_str(lexicon.id)
        _enrich_namespace_tree(namespace_tree, nsid, defs)

    return namespace_tree


def build_namespaces(config: t.Optional[CodegenConfig] = None) -> NamespaceNode:
    return build_namespace_tree(list(parse_lexicons(config or get_config())))
