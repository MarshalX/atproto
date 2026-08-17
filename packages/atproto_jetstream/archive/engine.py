import asyncio
import typing as t

from atproto_jetstream.archive.downloader import ArchiveDownloader, AsyncArchiveDownloader, iter_block_frames
from atproto_jetstream.archive.events import ArchivedEventsMessage, to_messages
from atproto_jetstream.archive.matcher import RowMatcher
from atproto_jetstream.archive.planner import PlanFilters, SnapshotPlan
from atproto_jetstream.archive.segment import decode_block


class SweepState:
    """Progress of an archive sweep."""

    def __init__(self, after_seq: int = 0) -> None:
        self.last_seq = after_seq
        self.sealed_tip_seq: t.Optional[int] = None
        self.units = 0

    @property
    def cutover_seq(self) -> int:
        """:obj:`int`: Cursor the live tail must resume from.

        The maximum matters: on a re-planned sweep the freshly learned sealed tip can sit
        below what was already delivered, and cutting over there would replay out of order.
        """
        return max(self.sealed_tip_seq or 0, self.last_seq)


def sweep_archive(
    downloader: ArchiveDownloader,
    filters: PlanFilters,
    matcher: RowMatcher,
    state: SweepState,
    after_seq: int = 0,
    before_seq: t.Optional[int] = None,
    *,
    with_cid: bool = True,
) -> t.Iterator[ArchivedEventsMessage]:
    """Page the plan, download each unit, and yield matching rows in seq order."""
    plan = SnapshotPlan(filters, after_seq=after_seq, before_seq=before_seq)

    while True:
        page = downloader.plan_page(plan.next_page_input())
        units = plan.consume_page(page)
        state.sealed_tip_seq = plan.sealed_tip_seq

        for unit in units:
            state.units += 1
            for message in to_messages(matcher.filter(downloader.rows(unit)), with_cid=with_cid):
                state.last_seq = max(state.last_seq, message.seq)
                yield message

        if plan.is_complete:
            return


async def sweep_archive_async(
    downloader: AsyncArchiveDownloader,
    filters: PlanFilters,
    matcher: RowMatcher,
    state: SweepState,
    after_seq: int = 0,
    before_seq: t.Optional[int] = None,
    *,
    with_cid: bool = True,
) -> t.AsyncIterator[ArchivedEventsMessage]:
    """Async twin of :obj:`sweep_archive`.

    Downloads run on the event loop; decoding is offloaded so a block never stalls it.
    """
    plan = SnapshotPlan(filters, after_seq=after_seq, before_seq=before_seq)
    loop = asyncio.get_running_loop()

    while True:
        page = await downloader.plan_page(plan.next_page_input())
        units = plan.consume_page(page)
        state.sealed_tip_seq = plan.sealed_tip_seq

        for unit in units:
            state.units += 1
            frames: t.List[bytes] = []
            if unit.is_whole_segment:
                segment = await downloader.fetch_segment(unit.segment)
                frames = list(iter_block_frames(segment))
            else:
                for block_index in unit.blocks or ():
                    frames.append(await downloader.fetch_block(unit.segment, block_index))

            for frame in frames:
                # decode is GIL-bound and synchronous; keep it off the loop
                rows = await loop.run_in_executor(None, decode_block, frame)
                for message in to_messages(matcher.filter(rows), with_cid=with_cid):
                    state.last_seq = max(state.last_seq, message.seq)
                    yield message

        if plan.is_complete:
            return
