from typing import Dict, Union, Any, List

class DefaultPath(object):
    pass

class Store(object):
    SubStore = Dict[str, Union[str, 'Store']]
    paths: SubStore

    def __init__(self, ps: SubStore):
        self.paths = ps

    def lookup(self, key: List[str]) -> str:
        next_level = self.paths[key[0]]
        if isinstance(next_level, str):
            if len(key) == 1:
                return next_level
            else:
                raise PathTooLongError(next_level, key)
        else:
            if len(key) == 1:
                raise PathTooShortError(self.paths, key)
            else:
                return next_level.lookup(key[1:])

    def insert(self, key: List[str], value: str) -> None:
        if key == []:
            raise PathTooShortError(self.paths, key)
        elif len(key) == 1:
            if key[0] in self.paths:
                raise ExistingKey(self.paths, key)
            else:
                self.paths[key[0]] = value
        else:
            next = self.paths[key[0]]
            if isinstance(next, str):
                raise KeyConflictError(self.paths, key)
            else:
                next.insert(key[1:], value)

    def remove(self, key: List[str]) -> None:
        if key == []:
            raise PathTooShortError(self.paths, key)
        elif key[0] not in self.paths:
            raise NonExistingKeyError(self.paths, key)
        else:
            if len(key) == 1:
                del self.paths[key[0]]
            elif isinstance(self.paths[key[0]], str):
                raise PathTooLongError(self.paths, key)
            else:
                self.paths[key[0]].remove(key[1:])

    def __str__(self) -> str:
        return str(self.paths)

class StoreError(Exception):
    pass

class PathTooLongError(StoreError):
    pass

class PathTooShortError(StoreError):
    pass

class ExistingKey(StoreError):
    pass

class NonExistingKeyError(StoreError):
    pass

class KeyConflictError(StoreError):
    pass

def test_lookup(ns: str) -> str:
    return test_store().lookup(ns.split())

def test_insert(key: str, value: str) -> Store:
    s = test_store()
    s.insert(key.split(), value)
    if s.lookup(key.split()) == value:
        print('Lookup after insertion returns inserted value')
    else:
        print('Lookup after insertion does not return inserted value')
    return s

def test_store() -> Store:
    return Store(
        {'labs': Store(
            {'ai': '/path/to/ai/labs/', 'compiler': '/path/to/compiler/labs/'}),
        'lectures': Store(
            {'ai': '/path/to/ai/lectures/', 'compiler': '/path/to/compiler/lectures/'})})
