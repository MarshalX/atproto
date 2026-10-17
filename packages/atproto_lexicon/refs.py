import typing as t

from pydantic import BaseModel

from atproto_lexicon import models


def _iter_refs(node: t.Any) -> t.Iterator[str]:
    if isinstance(node, models.LexRef):
        yield node.ref
    elif isinstance(node, models.LexRefUnion):
        yield from node.refs
    elif isinstance(node, models.LexString):
        # tokens named in knownValues or enum resolve to models just like refs
        values = [*(node.known_values or []), *(node.enum or [])]
        yield from (value for value in values if '#' in value)
    elif isinstance(node, BaseModel):
        for name in type(node).model_fields:
            yield from _iter_refs(getattr(node, name))
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_refs(value)


def _split_ref(doc_id: str, ref: str) -> t.Tuple[str, str]:
    nsid, _, def_name = ref.partition('#')
    return nsid or doc_id, def_name or 'main'


def find_unresolved_refs(docs: t.Iterable[models.LexiconDoc]) -> t.Dict[str, t.List[str]]:
    """Find references to definitions that the given lexicons do not define.

    Returns:
        Each missing target mapped to the sorted NSIDs of the lexicons referencing it. A target is the NSID
        of a missing lexicon, or ``nsid#def`` for a def missing from a present one.
    """
    docs = list(docs)
    defs_by_nsid = {doc.id: doc.defs for doc in docs}

    unresolved: t.Dict[str, t.Set[str]] = {}
    for doc in docs:
        for ref in _iter_refs(doc.defs):
            nsid, def_name = _split_ref(doc.id, ref)

            defs = defs_by_nsid.get(nsid)
            if defs is None:
                unresolved.setdefault(nsid, set()).add(doc.id)
            elif def_name not in defs:
                unresolved.setdefault(f'{nsid}#{def_name}', set()).add(doc.id)

    return {target: sorted(referrers) for target, referrers in sorted(unresolved.items())}
