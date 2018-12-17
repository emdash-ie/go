from typing import Dict, Union, Any, List, Set, Optional
from dataclasses import dataclass

class DefaultPath(object):
    pass

class PathLookupError(Exception):
    pass

class AmbiguousPrefixError(PathLookupError):
    def __init__(self, matches: Dict[str, str], prefix: str):
        self.matches = matches
        self.prefix = prefix

class NoMatchError(PathLookupError):
    def __init__(self, names: Dict[str, str], prefix: str):
        self.names = names
        self.prefix = prefix

def prefix_match(ns: Dict[str, str], p: str) -> Union[str, PathLookupError]:
    """Finds a single value in ns of which p is a prefix.

    Returns an error if p is a prefix of multiple values in ns.
    """
    matches = {k: v for k, v in ns.items() if k.startswith(p)}
    if len(matches) == 0:
        return NoMatchError(ns, p)
    elif len(matches) > 1:
        return AmbiguousPrefixError(matches, p)
    else:
        return matches.popitem()[1]

class Store(object):
    SubStore = Dict[str, 'Store']
    children: SubStore
    path: Optional[str]

    def __init__(self, children: SubStore = {}, path: str = None):
        self.children = children
        self.path = path

    def lookup(self, keys: List[str]) -> str:
        if keys == []:
            if self.path is None:
                raise NonExistingKeyError(keys, self.children)
            else:
                return self.path
        elif keys[0] not in self.children:
            raise NonExistingKeyError(keys, self.children)
        else:
            return self.children[keys[0]].lookup(keys[1:])

    def insert(self, keys: List[str], value: str) -> None:
        if keys == []:
            if self.path is None:
                self.path = value
            else:
                raise ExistingKeyError(self.children, keys)
        elif keys[0] in self.children:
            self.children[keys[0]].insert(keys[1:], value)
        else:
            store = Store()
            store.insert(keys[1:], value)
            self.children = self.children.copy()
            self.children[keys[0]] = store

    def remove(self, keys: List[str]) -> None:
        if keys == []:
            raise PathTooShortError(self.children, keys)
        elif keys[0] not in self.children:
            raise NonExistingKeyError(self.children, keys)
        elif len(keys) == 1:
            next = self.children[keys[0]]
            if next.children == {}:
                del self.children[keys[0]]
            else:
                next.path = None
        else:
            self.children[keys[0]].remove(keys[1:])

    def __str__(self) -> str:
        return str([f'({k}: {s.path}, {str(s)})' for k, s in self.children.items()])

    def __repr__(self) -> str:
        return f'Store(children={repr(self.children)}, path={repr(self.path)})'

class StoreError(Exception):
    pass

class PathTooLongError(StoreError):
    pass

class PathTooShortError(StoreError):
    pass

class ExistingKeyError(StoreError):
    pass

class NonExistingKeyError(StoreError):
    pass

class KeyConflictError(StoreError):
    pass

@dataclass
class NameAndPath(object):
    name: str
    path: Union[DefaultPath, str]

    @classmethod
    def from_list(cls, l: Optional[List[str]]) -> Optional["NameAndPath"]:
        if l is None:
            return None
        elif len(l) == 0:
            return None
        elif len(l) == 1:
            return NameAndPath(name=l[0], path=DefaultPath())
        else:
            return NameAndPath(name=l[0], path=l[1])
