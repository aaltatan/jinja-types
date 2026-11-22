"""Phase 5: `date`, `datetime`, `time` and `timedelta`."""

from datetime import UTC, date, datetime, time, timedelta

import pytest
from jinja2.sandbox import ImmutableSandboxedEnvironment

from jinja_types import JinjaTypesError, Registry, install

REGISTRY = Registry.default()
MOMENT = datetime(2026, 11, 22, 14, 30, 5, tzinfo=UTC)
CONSTANTS = {"min", "max", "resolution"}
# today/now/utcnow: use the today() and now() globals; utcfromtimestamp is deprecated
SKIPPED = CONSTANTS | {"today", "now", "utcnow", "utcfromtimestamp"}


def render(template: str, *, coerce: bool = False, **context: object) -> str:
    env = ImmutableSandboxedEnvironment()

    install(env, REGISTRY, coerce=coerce)

    return env.from_string(template).render(**context)


def registered(namespace: str) -> set[str]:
    return {spec.member for spec in REGISTRY.specs() if spec.namespace.name == namespace}


@pytest.mark.parametrize(
    ("namespace", "members"),
    [
        ("date", dir(date)),
        ("datetime", vars(datetime)),  # only what datetime adds or overrides
        ("time", dir(time)),
        ("timedelta", dir(timedelta)),
    ],
)
def test_every_public_member_is_registered(namespace: str, members: list[str]) -> None:
    public = {name for name in members if not name.startswith("_")}

    assert registered(namespace) == public - SKIPPED


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("{{ d | date.strftime('%H:%M') }}", "14:30"),
        ("{{ d | date.replace(hour=9, minute=0) }}", "2026-11-22 09:00:05+00:00"),
        ("{{ d | date.isoformat(' ', 'seconds') }}", "2026-11-22 14:30:05+00:00"),
        ("{{ d | date.ctime }}", "Sun Nov 22 14:30:05 2026"),
    ],
)
def test_date_members_dispatch_to_datetime(template: str, expected: str) -> None:
    assert render(template, d=MOMENT) == expected


def test_date_members_on_a_date_do_not_take_datetime_arguments() -> None:
    with pytest.raises(JinjaTypesError, match=r"date\.replace: TypeError.*Hint: check the"):
        render("{{ d | date.replace(hour=9) }}", d=date(2026, 11, 22))


def test_datetime_members_reject_a_plain_date() -> None:
    with pytest.raises(
        JinjaTypesError, match=r"got 'date', expected datetime\. Hint: .*to_datetime"
    ):
        render("{{ d | datetime.hour }}", d=date(2026, 11, 22))


def test_timezone_names() -> None:
    assert render("{{ d | datetime.astimezone('Asia/Damascus') | datetime.tzname }}", d=MOMENT) == (
        "+03"
    )

    with pytest.raises(JinjaTypesError, match=r"datetime\.astimezone: .*Mars/Olympus"):
        render("{{ d | datetime.astimezone('Mars/Olympus') }}", d=MOMENT)


def test_replace_keeps_or_drops_the_timezone() -> None:
    assert render("{{ d | datetime.replace(day=1) }}", d=MOMENT) == "2026-11-01 14:30:05+00:00"
    assert render("{{ d | datetime.replace(tzinfo=none) }}", d=MOMENT) == "2026-11-22 14:30:05"


def test_coerce_dates() -> None:
    assert render("{{ '2026-11-22' | date.weekday }}", coerce=True) == "6"
    assert render("{{ '2026-11-22T09:15' | datetime.hour }}", coerce=True) == "9"
    assert render("{{ '09:15' | time.minute }}", coerce=True) == "15"
    assert render("{{ '90' | timedelta.total_seconds }}", coerce=True) == "90.0"
