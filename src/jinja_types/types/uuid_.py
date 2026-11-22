"""The `uuid` namespace: the read-only attributes of `uuid.UUID`."""

from uuid import UUID, SafeUUID

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("uuid", UUID, parse=PARSERS["uuid"])

U = {"u": UUID("c232ab00-9414-11ec-b3c8-9f6bdeced846")}


@collection.attribute(
    member="hex", examples=[("{{ u | uuid.hex }}", U, "c232ab00941411ecb3c89f6bdeced846")]
)
def hex_(value: UUID, /) -> str:
    """The 32 hex digits, without dashes."""
    return value.hex


@collection.attribute(
    member="int", examples=[("{{ u | uuid.int }}", U, "258133314363070689776975542038781941830")]
)
def int_(value: UUID, /) -> int:
    """The UUID as a 128-bit integer."""
    return value.int


@collection.attribute(member="bytes", examples=[("{{ u | uuid.bytes | list | first }}", U, "194")])
def bytes_(value: UUID, /) -> bytes:
    """The 16 bytes, big-endian."""
    return value.bytes


@collection.attribute(examples=[("{{ u | uuid.bytes_le | list | first }}", U, "0")])
def bytes_le(value: UUID, /) -> bytes:
    """The 16 bytes, with the first three fields little-endian."""
    return value.bytes_le


@collection.attribute(
    examples=[("{{ u | uuid.urn }}", U, "urn:uuid:c232ab00-9414-11ec-b3c8-9f6bdeced846")]
)
def urn(value: UUID, /) -> str:
    """The UUID as a URN."""
    return value.urn


@collection.attribute(examples=[("{{ u | uuid.version }}", U, "1")])
def version(value: UUID, /) -> int | None:
    """The version number (1 to 8), or None if the variant is not RFC 4122."""
    return value.version


@collection.attribute(examples=[("{{ u | uuid.variant }}", U, "specified in RFC 4122")])
def variant(value: UUID, /) -> str:
    """The variant, as one of the `uuid.RESERVED_*` / `uuid.RFC_4122` strings."""
    return value.variant


@collection.attribute(
    examples=[
        (
            "{{ u | uuid.fields | join('|') }}",
            U,
            "3258100480|37908|4588|179|200|175285648414790",
        )
    ]
)
def fields(value: UUID, /) -> tuple[int, int, int, int, int, int]:
    """The six integer fields."""
    return value.fields


@collection.attribute(examples=[("{{ u | uuid.time }}", U, "138648505420000000")])
def time(value: UUID, /) -> int:
    """The 60-bit timestamp (meaningful for version 1)."""
    return value.time


@collection.attribute(examples=[("{{ u | uuid.node }}", U, "175285648414790")])
def node(value: UUID, /) -> int:
    """The 48-bit node id (meaningful for version 1)."""
    return value.node


@collection.attribute(examples=[("{{ u | uuid.clock_seq }}", U, "13256")])
def clock_seq(value: UUID, /) -> int:
    """The 14-bit clock sequence."""
    return value.clock_seq


@collection.attribute(examples=[("{{ u | uuid.clock_seq_hi_variant }}", U, "179")])
def clock_seq_hi_variant(value: UUID, /) -> int:
    """The high byte of the clock sequence, with the variant bits."""
    return value.clock_seq_hi_variant


@collection.attribute(examples=[("{{ u | uuid.clock_seq_low }}", U, "200")])
def clock_seq_low(value: UUID, /) -> int:
    """The low byte of the clock sequence."""
    return value.clock_seq_low


@collection.attribute(examples=[("{{ u | uuid.time_low }}", U, "3258100480")])
def time_low(value: UUID, /) -> int:
    """The first 32 bits of the UUID."""
    return value.time_low


@collection.attribute(examples=[("{{ u | uuid.time_mid }}", U, "37908")])
def time_mid(value: UUID, /) -> int:
    """The next 16 bits of the UUID."""
    return value.time_mid


@collection.attribute(examples=[("{{ u | uuid.time_hi_version }}", U, "4588")])
def time_hi_version(value: UUID, /) -> int:
    """The next 16 bits, with the version bits."""
    return value.time_hi_version


@collection.attribute(examples=[("{{ u | uuid.is_safe }}", U, "SafeUUID.unknown")])
def is_safe(value: UUID, /) -> SafeUUID:
    """Whether the UUID was generated in a multiprocessing-safe way."""
    return value.is_safe
