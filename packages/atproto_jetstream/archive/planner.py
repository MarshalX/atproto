import typing as t
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from atproto_client import models

_SEGMENT_MODE = 'segment'
_BLOCKS_MODE = 'blocks'


@dataclass
class WorkUnit:
    """One downloadable piece of the archive, in plan order."""

    segment: str  #: Segment filename.
    checksum: str  #: xxh3 metadata checksum. Doubles as the ETag for a resumed download.
    min_seq: int  #: Lowest seq the unit may contain.
    max_seq: int  #: Highest seq the unit may contain.
    blocks: t.Optional[t.List[int]] = None  #: Block indexes to fetch, or :obj:`None` for the whole segment.

    @property
    def is_whole_segment(self) -> bool:
        """:obj:`bool`: Whether the whole segment file must be downloaded."""
        return self.blocks is None


@dataclass
class PlanFilters:
    """Filters shared by the planner and the row matcher."""

    kinds: t.List[str] = field(default_factory=list)
    dids: t.List[str] = field(default_factory=list)
    collections: t.List[str] = field(default_factory=list)

    def as_plan_input(self, after_seq: int, before_seq: t.Optional[int]) -> t.Dict[str, t.Any]:
        data: t.Dict[str, t.Any] = {'after_seq': after_seq}
        if before_seq is not None:
            data['before_seq'] = before_seq
        if self.kinds:
            data['kinds'] = list(self.kinds)
        if self.dids:
            data['dids'] = list(self.dids)
        if self.collections:
            data['collections'] = list(self.collections)

        return data


def _to_work_units(page: 'models.NetworkBskyJetstreamPlanSnapshot.Response') -> t.Iterator[WorkUnit]:
    for segment in page.segments:
        blocks: t.Optional[t.List[int]] = None
        if segment.mode == _BLOCKS_MODE:
            blocks = []
            for block_range in segment.blocks or ():
                blocks.extend(range(block_range.first, block_range.last + 1))

        yield WorkUnit(
            segment=segment.name,
            checksum=segment.checksum,
            min_seq=segment.min_seq,
            max_seq=segment.max_seq,
            blocks=blocks,
        )


class SnapshotPlan:
    """Pages `planSnapshot` and yields work units in seq order.

    The sealed tip is pinned from the first page: segments sealed while the sweep runs carry
    seqs above the pin and are deliberately left to the live tail's cold replay at cutover.

    Args:
        filters: Filters to plan against.
        after_seq: Exclusive lower bound.
        before_seq: Inclusive upper bound.
    """

    def __init__(
        self,
        filters: PlanFilters,
        after_seq: int = 0,
        before_seq: t.Optional[int] = None,
    ) -> None:
        self._filters = filters
        self._after_seq = after_seq
        self._before_seq = before_seq

        self._sealed_tip_seq: t.Optional[int] = None
        self._planned_through_seq = after_seq
        self._pages = 0

    @property
    def sealed_tip_seq(self) -> t.Optional[int]:
        """:obj:`int`: Pinned sealed tip, or :obj:`None` before the first page."""
        return self._sealed_tip_seq

    @property
    def planned_through_seq(self) -> int:
        """:obj:`int`: Highest sealed seq accounted for so far."""
        return self._planned_through_seq

    @property
    def pages(self) -> int:
        """:obj:`int`: Number of plan pages fetched."""
        return self._pages

    @property
    def is_complete(self) -> bool:
        """:obj:`bool`: Whether planning has reached the pinned sealed tip."""
        return self._sealed_tip_seq is not None and self._planned_through_seq >= self._sealed_tip_seq

    def next_page_input(self) -> t.Dict[str, t.Any]:
        """Build the `planSnapshot` input for the next page."""
        before_seq = self._before_seq
        if before_seq is None:
            # pin the snapshot so it cannot drift while it is being downloaded
            before_seq = self._sealed_tip_seq

        return self._filters.as_plan_input(self._planned_through_seq, before_seq)

    def consume_page(self, page: 'models.NetworkBskyJetstreamPlanSnapshot.Response') -> t.List[WorkUnit]:
        """Absorb a plan page and return its work units."""
        self._pages += 1
        if self._sealed_tip_seq is None:
            self._sealed_tip_seq = page.sealed_tip_seq

        units = list(_to_work_units(page))

        # planned_through_seq is the continuation cursor; it must never go backwards
        self._planned_through_seq = max(self._planned_through_seq, page.planned_through_seq)

        return units
