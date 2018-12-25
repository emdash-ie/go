from typing import Dict, Union, Any, List, Set, Optional
from dataclasses import dataclass
import shelve
from os import environ, getcwd
from errors import *

class DefaultPath(object):
    pass

def locations() -> Dict[str, str]:
    with shelve.open(go_file()) as db:
        return db["locations"]

def store(locations: Dict[str, str]) -> None:
    with shelve.open(go_file()) as db:
        db["locations"] = locations

def go_file() -> str:
    return environ["HOME"] + "/.go/go-file"

def lookup(locations: Dict[str, str], name: str) -> Union[str, PathLookupError]:
    return prefix_match(locations, name)

def add(locations: Dict[str, str], name: str, path: Union[str, DefaultPath]) -> Dict[str, str]:
    if isinstance(path, DefaultPath):
        path = getcwd()
    locations[name] = use_tilde(path)
    return locations

def use_tilde(s: str) -> str:
    if s.startswith(environ["HOME"]):
        return s.replace(environ["HOME"], "~", 1)
    else:
        return s

def remove(locations: Dict[str, str], name: str) -> Dict[str, str]:
    if name in locations:
        del locations[name]
    return locations

def rename(locations: Dict[str, str], old_name: str, new_name: str) -> Dict[str, str]:
    p = locations.get(old_name)
    if p is not None:
        del locations[old_name]
        locations[new_name] = p
    return locations

def duplicate(locations: Dict[str, str], old_name: str, new_name: str) -> Dict[str, str]:
    p = locations.get(old_name)
    if p is not None:
        locations[new_name] = p
    return locations

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

@dataclass
class TwoNames(object):
    old_name: str
    new_name: str
