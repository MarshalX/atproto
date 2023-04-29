from typing import Dict, List, NamedTuple, Union

from lexicon.models import LexDefinition, LexDefinitionType, LexiconDoc
from lexicon.parser import lexicon_parse_dir
from nsid import NSID

_NAMESPACE_SUFFIX = 'Namespace'
_RECORD_SUFFIX = 'Record'


def _get_namespace_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_NAMESPACE_SUFFIX}'


def _get_record_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_RECORD_SUFFIX}'


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


def _generate_namespace(namespace_tree: Union[dict, list]):
    for node_name, sub_node in namespace_tree.items():
        if isinstance(sub_node, dict):
            print(f'{_get_namespace_name(node_name)}:')
            print('    Sub-namespaces:')
            for sub_namespace in sub_node.keys():
                print(f'        - {sub_namespace}: {_get_namespace_name(sub_namespace)}')

            _generate_namespace(sub_node)

        if isinstance(sub_node, list):
            print(f'{_get_namespace_name(node_name)}:')
            records = [info for info in sub_node if isinstance(info, RecordInfo)]
            if records:
                print('    Records:')
            for record in records:
                print(f'        - {record.name}: {_get_record_name(record.name)}')

            methods = [info for info in sub_node if isinstance(info, MethodInfo)]
            if methods:
                print('    Methods:')
            for method in methods:
                print(f'        - {method.name}(...)')


def generate_namespaces() -> None:
    lexicons = lexicon_parse_dir()
    namespace_tree = build_namespace_tree(lexicons)

    print(namespace_tree)
    _generate_namespace(namespace_tree)


if __name__ == '__main__':
    generate_namespaces()
