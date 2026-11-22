"""The `path` namespace: `PurePath` members only, so nothing here touches the disk.

`to_path` gives the platform's pure path (`PureWindowsPath` on Windows); use `path.as_posix` for
output that looks the same everywhere. Not exposed: the deprecated `is_reserved` and the
`with_segments` factory. `full_match` exists on Python 3.13+ only.
"""

import sys
from collections.abc import Sequence
from pathlib import PurePath, PurePosixPath, PureWindowsPath

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("path", PurePath, parse=PARSERS["path"])

P = {"p": PurePosixPath("/srv/docs/report.tar.gz")}
W = {"w": PureWindowsPath("C:/Users/sara/notes.txt")}
POSIX = " | path.as_posix }}"


@collection.attribute(examples=[("{{ p | path.name }}", P, "report.tar.gz")])
def name(value: PurePath, /) -> str:
    """The final component."""
    return value.name


@collection.attribute(examples=[("{{ p | path.stem }}", P, "report.tar")])
def stem(value: PurePath, /) -> str:
    """The final component without its last suffix."""
    return value.stem


@collection.attribute(examples=[("{{ p | path.suffix }}", P, ".gz")])
def suffix(value: PurePath, /) -> str:
    """The last suffix of the final component, with the dot."""
    return value.suffix


@collection.attribute(examples=[("{{ p | path.suffixes | join }}", P, ".tar.gz")])
def suffixes(value: PurePath, /) -> list[str]:
    """Every suffix of the final component."""
    return value.suffixes


@collection.attribute(examples=[("{{ p | path.parent" + POSIX, P, "/srv/docs")])
def parent(value: PurePath, /) -> PurePath:
    """The logical parent."""
    return value.parent


@collection.attribute(
    examples=[("{{ p | path.parents | map('path.as_posix') | join('|') }}", P, "/srv/docs|/srv|/")]
)
def parents(value: PurePath, /) -> Sequence[PurePath]:
    """Every logical ancestor, nearest first."""
    return value.parents


@collection.attribute(
    examples=[("{{ p | path.parts | join('|') }}", P, "/|srv|docs|report.tar.gz")]
)
def parts(value: PurePath, /) -> tuple[str, ...]:
    """The components, as a tuple."""
    return value.parts


@collection.attribute(examples=[("{{ w | path.anchor }}", W, "C:\\")])
def anchor(value: PurePath, /) -> str:
    """The drive and root together."""
    return value.anchor


@collection.attribute(examples=[("{{ w | path.drive }}", W, "C:")])
def drive(value: PurePath, /) -> str:
    """The drive letter or UNC share (empty on POSIX)."""
    return value.drive


@collection.attribute(examples=[("{{ p | path.root }}", P, "/")])
def root(value: PurePath, /) -> str:
    """The root separator, if any."""
    return value.root


@collection.filter(examples=[("{{ w | path.as_posix }}", W, "C:/Users/sara/notes.txt")])
def as_posix(value: PurePath, /) -> str:
    """Return the path with forward slashes."""
    return value.as_posix()


@collection.filter(
    examples=[
        ("{{ x | path.as_uri }}", {"x": PurePosixPath("/srv/a b.txt")}, "file:///srv/a%20b.txt")
    ]
)
def as_uri(value: PurePath, /) -> str:
    """Return a `file:` URI. The path must be absolute."""
    return value.as_uri()


@collection.filter(
    examples=[("{{ p | path.with_name('data.csv')" + POSIX, P, "/srv/docs/data.csv")]
)
def with_name(value: PurePath, name: str, /) -> PurePath:
    """Return the path with the final component replaced."""
    return value.with_name(name)


@collection.filter(examples=[("{{ p | path.with_stem('old')" + POSIX, P, "/srv/docs/old.gz")])
def with_stem(value: PurePath, stem: str, /) -> PurePath:
    """Return the path with the stem replaced."""
    return value.with_stem(stem)


@collection.filter(
    examples=[
        ("{{ p | path.with_suffix('.zip')" + POSIX, P, "/srv/docs/report.tar.zip"),
        ("{{ p | path.with_suffix('')" + POSIX, P, "/srv/docs/report.tar"),
    ]
)
def with_suffix(value: PurePath, suffix: str, /) -> PurePath:
    """Return the path with the last suffix replaced (or removed with `''`)."""
    return value.with_suffix(suffix)


@collection.filter(
    examples=[("{{ p | path.parent | path.joinpath('a', 'b.txt')" + POSIX, P, "/srv/docs/a/b.txt")]
)
def joinpath(value: PurePath, /, *pathsegments: str | PurePath) -> PurePath:
    """Return the path with the segments appended."""
    return value.joinpath(*pathsegments)


@collection.filter(
    examples=[
        ("{{ p | path.relative_to('/srv')" + POSIX, P, "docs/report.tar.gz"),
        ("{{ p | path.relative_to('/srv/web', walk_up=true)" + POSIX, P, "../docs/report.tar.gz"),
    ]
)
def relative_to(value: PurePath, other: str | PurePath, /, *, walk_up: bool = False) -> PurePath:
    """Return the path relative to `other`. Raises if it is not under it (unless `walk_up`)."""
    return value.relative_to(other, walk_up=walk_up)


@collection.filter(
    examples=[
        ("{{ p | path.is_relative_to('/srv') }}", P, "True"),
        ("{{ p is path.is_relative_to('/etc') }}", P, "False"),
    ]
)
def is_relative_to(value: PurePath, other: str | PurePath, /) -> bool:
    """Return True if the path is under `other`."""
    return value.is_relative_to(other)


@collection.filter(
    examples=[
        ("{{ p | path.is_absolute }}", P, "True"),
        ("{{ x is path.is_absolute }}", {"x": PurePosixPath("a/b")}, "False"),
    ]
)
def is_absolute(value: PurePath, /) -> bool:
    """Return True if the path has a root (and a drive, on Windows)."""
    return value.is_absolute()


@collection.filter(
    examples=[
        ("{{ p | path.match('*.gz') }}", P, "True"),
        ("{{ p is path.match('docs/*.gz') }}", P, "True"),
        ("{{ p is path.match('/docs/*') }}", P, "False"),
    ]
)
def match(value: PurePath, path_pattern: str, /, *, case_sensitive: bool | None = None) -> bool:
    """Return True if the path matches the glob pattern, matched from the right."""
    return value.match(path_pattern, case_sensitive=case_sensitive)


if sys.version_info >= (3, 13):

    @collection.filter(
        examples=[
            ("{{ p | path.full_match('/srv/**/*.gz') }}", P, "True"),
            ("{{ p is path.full_match('*.gz') }}", P, "False"),
        ]
    )
    def full_match(value: PurePath, pattern: str, /, *, case_sensitive: bool | None = None) -> bool:
        """Return True if the whole path matches the glob pattern (`**` allowed)."""
        return value.full_match(pattern, case_sensitive=case_sensitive)
