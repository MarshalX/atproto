import typing as t
from dataclasses import dataclass

from atproto_core.uri import SpaceRef
from atproto_core.uri.space import is_record_key

if t.TYPE_CHECKING:
    from atproto_lexicon.models import LexiconDoc

_MAIN_DEF_NAME: t.Final = 'main'
_KEY_TYPES: t.Final = frozenset({'any', 'nsid', 'tid'})
_LITERAL_KEY_PREFIX: t.Final = 'literal:'


@dataclass(frozen=True)
class SpaceType:
    """Type of a space, as its lexicon declares it.

    Attributes:
        nsid: NSID of the space type.
        key: Type of the space key: ``any``, ``nsid``, ``tid`` or ``literal:<key>``.
        collections: NSIDs of the collections that the spaces of this type hold.

    Raises:
        :class:`ValueError`: The key is not a type of a space key.
    """

    nsid: str
    key: str
    collections: t.Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        literal = self.key[len(_LITERAL_KEY_PREFIX) :]
        is_literal = self.key.startswith(_LITERAL_KEY_PREFIX) and is_record_key(literal)
        if self.key not in _KEY_TYPES and not is_literal:
            raise ValueError("Space key must be 'any', 'nsid', 'tid' or 'literal:<record key>'")

    @classmethod
    def from_lexicon(cls, lexicon: 'LexiconDoc') -> 'SpaceType':
        """Create `SpaceType` instance from the lexicon that declares it.

        Args:
            lexicon: Lexicon document whose main definition is a space.

        Returns:
            :obj:`SpaceType`: Type of a space.

        Raises:
            :class:`ValueError`: The main definition of the lexicon is not a space.
        """
        from atproto_lexicon.models import LexSpace

        definition = lexicon.defs.get(_MAIN_DEF_NAME)
        if not isinstance(definition, LexSpace):
            raise ValueError(f'Lexicon {lexicon.id} does not declare a space type')  # noqa: TRY004

        return cls(nsid=lexicon.id, key=definition.key, collections=tuple(definition.collections))

    def ref_for(self, space_did: str, skey: t.Optional[str] = None) -> SpaceRef:
        """Get the reference to a space of this type.

        Args:
            space_did: DID of the space authority.
            skey: Key of the space. The key of a type with a literal key by default.

        Returns:
            :obj:`atproto_core.uri.SpaceRef`: Reference to the space.

        Raises:
            :class:`ValueError`: The key is missing, or it is not the literal key of the type.
            :class:`atproto.exceptions.InvalidAtUriError`: The DID or the key is not valid.
        """
        if self.key.startswith(_LITERAL_KEY_PREFIX):
            literal = self.key[len(_LITERAL_KEY_PREFIX) :]
            if skey is not None and skey != literal:
                raise ValueError(f'Key of a {self.nsid} space must be {literal}')

            skey = literal
        elif not skey:
            raise ValueError(f'Key of a {self.nsid} space is required')

        return SpaceRef.from_str(str(SpaceRef(space_did, self.nsid, skey)))
