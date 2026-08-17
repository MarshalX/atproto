"""Plan paging, work-unit expansion, and quota back-off. All pure logic, no network."""

import typing as t

import pytest
from atproto_client import models
from atproto_client.exceptions import RequestException, UnauthorizedError
from atproto_client.models.common import XrpcError
from atproto_client.request import Response
from atproto_jetstream.archive.downloader import quota_retry_after
from atproto_jetstream.archive.planner import PlanFilters, SnapshotPlan


def make_page(
    planned_through: int,
    sealed_tip: int,
    segments: t.Optional[t.List[t.Dict[str, t.Any]]] = None,
) -> t.Any:
    return models.NetworkBskyJetstreamPlanSnapshot.Response(
        planned_through_seq=planned_through,
        sealed_tip_seq=sealed_tip,
        segments=[models.NetworkBskyJetstreamPlanSnapshot.Segment(**segment) for segment in (segments or [])],
        stats=models.NetworkBskyJetstreamPlanSnapshot.Stats(
            blocks_matched=0, entries=0, segments_examined=0, segments_matched=0
        ),
    )


def segment(name: str = 'seg_0.jss', mode: str = 'segment', blocks: t.Any = None) -> t.Dict[str, t.Any]:
    return {
        'checksum': '0123456789abcdef',
        'index': 0,
        'min_seq': 1,
        'max_seq': 100,
        'mode': mode,
        'name': name,
        'blocks': blocks,
    }


def test_plan_filters_omit_empty_axes() -> None:
    data = PlanFilters().as_plan_input(after_seq=5, before_seq=None)

    assert data == {'after_seq': 5}


def test_plan_filters_pass_every_axis() -> None:
    filters = PlanFilters(kinds=['commit'], dids=['did:plc:aaa'], collections=['app.bsky.feed.post'])

    data = filters.as_plan_input(after_seq=0, before_seq=99)

    assert data == {
        'after_seq': 0,
        'before_seq': 99,
        'kinds': ['commit'],
        'dids': ['did:plc:aaa'],
        'collections': ['app.bsky.feed.post'],
    }


def test_plan_pins_the_sealed_tip_from_the_first_page() -> None:
    plan = SnapshotPlan(PlanFilters())

    plan.consume_page(make_page(planned_through=50, sealed_tip=100))
    # the archive grew while we were sweeping; the pin must not move
    plan.consume_page(make_page(planned_through=100, sealed_tip=500))

    assert plan.sealed_tip_seq == 100
    assert plan.is_complete


def test_plan_continues_from_planned_through_seq() -> None:
    plan = SnapshotPlan(PlanFilters(), after_seq=10)

    assert plan.next_page_input()['after_seq'] == 10

    plan.consume_page(make_page(planned_through=60, sealed_tip=100))

    assert plan.next_page_input()['after_seq'] == 60
    assert not plan.is_complete


def test_plan_caps_later_pages_at_the_pinned_tip() -> None:
    plan = SnapshotPlan(PlanFilters())
    plan.consume_page(make_page(planned_through=50, sealed_tip=100))

    # pinning before_seq is what stops the snapshot drifting mid-download
    assert plan.next_page_input()['before_seq'] == 100


def test_plan_keeps_an_explicit_before_seq() -> None:
    plan = SnapshotPlan(PlanFilters(), before_seq=42)
    plan.consume_page(make_page(planned_through=10, sealed_tip=100))

    assert plan.next_page_input()['before_seq'] == 42


def test_plan_cursor_never_goes_backwards() -> None:
    plan = SnapshotPlan(PlanFilters())
    plan.consume_page(make_page(planned_through=80, sealed_tip=100))
    plan.consume_page(make_page(planned_through=20, sealed_tip=100))

    assert plan.planned_through_seq == 80


def test_segment_mode_downloads_the_whole_file() -> None:
    plan = SnapshotPlan(PlanFilters())

    units = plan.consume_page(make_page(1, 1, [segment(mode='segment')]))

    assert units[0].is_whole_segment
    assert units[0].blocks is None


def test_blocks_mode_expands_inclusive_ranges() -> None:
    plan = SnapshotPlan(PlanFilters())
    ranges = [
        models.NetworkBskyJetstreamPlanSnapshot.BlockRange(first=2, last=4),
        models.NetworkBskyJetstreamPlanSnapshot.BlockRange(first=9, last=9),
    ]

    units = plan.consume_page(make_page(1, 1, [segment(mode='blocks', blocks=ranges)]))

    assert not units[0].is_whole_segment
    assert units[0].blocks == [2, 3, 4, 9]


def test_work_unit_carries_the_checksum_for_if_range() -> None:
    plan = SnapshotPlan(PlanFilters())

    units = plan.consume_page(make_page(1, 1, [segment()]))

    assert units[0].checksum == '0123456789abcdef'


def _error(status_code: int, headers: t.Optional[dict] = None) -> t.Any:
    return Response(
        success=False,
        status_code=status_code,
        content=XrpcError('byte limit exceeded', None),
        headers=headers or {},
    )


def test_quota_retry_after_honours_the_header() -> None:
    assert quota_retry_after(RequestException(_error(429, {'retry-after': '12'}))) == 12.0


def test_quota_retry_after_defaults_when_the_header_is_missing() -> None:
    delay = quota_retry_after(RequestException(_error(429)))

    assert delay is not None
    assert delay > 0


def test_quota_retry_after_defaults_when_the_header_is_junk() -> None:
    delay = quota_retry_after(RequestException(_error(429, {'retry-after': 'soon'})))

    assert delay is not None
    assert delay > 0


def test_quota_retry_after_is_capped() -> None:
    delay = quota_retry_after(RequestException(_error(429, {'retry-after': '999999'})))

    assert delay is not None
    assert delay <= 300.0


def test_quota_retry_after_ignores_other_failures() -> None:
    # a bad key must fail immediately rather than being retried against the quota
    assert quota_retry_after(UnauthorizedError(_error(401))) is None
    assert quota_retry_after(RequestException(_error(500))) is None
    assert quota_retry_after(ValueError('unrelated')) is None


@pytest.mark.parametrize('status_code', [200, 400, 401, 403, 404, 500, 503])
def test_only_429_is_a_quota_rejection(status_code: int) -> None:
    assert quota_retry_after(RequestException(_error(status_code))) is None
