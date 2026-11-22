"""The `bool` namespace.

`bool` has no members of its own: everything it has is inherited from `int`, and every
`int.*` member already accepts bools (`{{ true | int.real }}` gives `1`). The namespace is
registered so that `coerce=True` can parse strings with `to_bool`, and so error messages list
`int | bool` as the accepted types.
"""

from jinja_types.core import Collection
from jinja_types.helpers import PARSERS

collection = Collection("bool", bool, parse=PARSERS["bool"])
