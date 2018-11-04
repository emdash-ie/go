from typing import Dict, Union, Any, List, Set, Optional

class DefaultPath(object):
    pass

class AmbiguousPrefixError(Exception):
    def __init__(self, matches: Set[str], prefix: str):
        self.matches = matches
        self.prefix = prefix

class NoMatchError(Exception):
    def __init__(self, names: Set[str], prefix: str):
        self.names = names
        self.prefix = prefix

def prefix_match(ns: Set[str], p: str) -> Union[str, AmbiguousPrefixError, NoMatchError]:
    """Finds a single value in ns of which p is a prefix.

    Returns an error if p is a prefix of multiple values in ns.
    """
    matches = {n for n in ns if n.startswith(p)}
    if len(matches) == 0:
        return NoMatchError(ns, p)
    elif len(matches) > 1:
        return AmbiguousPrefixError(matches, p)
    else:
        return matches.pop()

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

# def test_lookup(ns: str) -> str:
#     return test_store().lookup(ns.split())
#
# def test_insert(key: str, value: str) -> Store:
#     s = test_store()
#     s.insert(key.split(), value)
#     if s.lookup(key.split()) == value:
#         print('Lookup after insertion returns inserted value')
#     else:
#         print('Lookup after insertion does not return inserted value')
#     return s
#
# def test_store() -> Store:
#     return Store(
#         {'labs': Store(
#             {'ai': '/path/to/ai/labs/', 'compiler': '/path/to/compiler/labs/'}),
#         'lectures': Store(
#             {'ai': '/path/to/ai/lectures/', 'compiler': '/path/to/compiler/lectures/'})})
