from typing import Dict, List, NamedTuple

from lexicon.models import LexDefinition, LexDefinitionType, LexiconDoc
from lexicon.parser import lexicon_parse_dir
from nsid import NSID


def _filter_namespace_valid_definitions(definitions: Dict[str, LexDefinition]) -> Dict[str, LexDefinition]:
    result = {}

    for def_name, def_content in definitions.items():
        if def_content.type in (LexDefinitionType.QUERY, LexDefinitionType.PROCEDURE, LexDefinitionType.RECORD):
            result[def_name] = def_content

    return result


def get_definition_by_name(name: str, defs: Dict[str, LexDefinition]) -> LexDefinition:
    if name in defs:
        return defs[name]

    return defs['main']


class MethodInfo(NamedTuple):
    name: str
    definition: LexDefinition


class RecordInfo(NamedTuple):
    name: str
    definition: LexDefinition


def _enrich_namespace_tree(root: dict, nsid: NSID, defs: Dict[str, LexDefinition]) -> None:
    segments_count = len(nsid.segments)
    for path_level, segment in enumerate(nsid.segments):
        # if method
        if path_level == segments_count - 1:
            definition = get_definition_by_name(segment, defs)

            model_class = MethodInfo
            if definition.type is LexDefinitionType.RECORD:
                model_class = RecordInfo

            # TODO(MarshalX): fake records as namespaces with methods to be able to reuse code of generator?

            root.append(model_class(name=segment, definition=definition))
            continue

        if segment not in root:
            # if end of method's path
            if path_level == segments_count - 2:
                root[segment] = []
            else:
                root[segment] = {}
        root = root[segment]


def build_namespace_tree(lexicons: List[LexiconDoc]) -> dict:
    namespace_tree = {}
    for lexicon in lexicons:
        defs = _filter_namespace_valid_definitions(lexicon.defs)
        if not defs:
            continue

        nsid = NSID.from_str(lexicon.id)
        _enrich_namespace_tree(namespace_tree, nsid, defs)

    return namespace_tree


def build_namespaces() -> dict:
    lexicons = lexicon_parse_dir()
    namespace_tree = build_namespace_tree(lexicons)

    return namespace_tree


if __name__ == '__main__':
    build_namespaces()
