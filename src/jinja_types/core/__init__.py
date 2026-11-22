"""The registry core: specs, collections, the registry, the invoker and the catalog."""

from .catalog import Catalog, CatalogEntry
from .collection import Collection, build_spec, type_repr
from .errors import BuiltinClashError, DuplicateMemberError, JinjaTypesError, RegistryError
from .invoker import Invoker
from .namespace import Namespace
from .options import Options, OptionsKwargs
from .plugins import PLUGIN_GROUP, load_plugins
from .registry import Conflict, Registry
from .spec import Example, Kind, MemberSpec, Param

__all__ = [
    "PLUGIN_GROUP",
    "BuiltinClashError",
    "Catalog",
    "CatalogEntry",
    "Collection",
    "Conflict",
    "DuplicateMemberError",
    "Example",
    "Invoker",
    "JinjaTypesError",
    "Kind",
    "MemberSpec",
    "Namespace",
    "Options",
    "OptionsKwargs",
    "Param",
    "Registry",
    "RegistryError",
    "build_spec",
    "load_plugins",
    "type_repr",
]
