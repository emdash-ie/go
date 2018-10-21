from typing import Dict, Union, Any, List

class DefaultPath(object):
    pass

class Store(object):
    SubStore = Dict[str, Union[str, 'Store']]
    paths: SubStore

    def __init__(self, ps: SubStore):
        self.paths = ps

    def lookup(self, ns: List[str]) -> str:
        next_level = self.paths[ns[0]]
        if isinstance(next_level, str):
            if len(ns) == 1:
                return next_level
            else:
                raise PathTooLongError(next_level, ns)
        else:
            if len(ns) == 1:
                raise PathTooShortError(self.paths, ns)
            else:
                return next_level.lookup(ns[1:])

    def __str__(self) -> str:
        return str(self.paths)

class StoreError(Exception):
    pass

class PathTooLongError(StoreError):
    pass

class PathTooShortError(StoreError):
    pass

def test_lookup(ns: str) -> str:
    d: Dict[str, Union[Store, str]] = {'labs': Store({'ai': '/path/to/ai/labs/',
            'compiler': '/path/to/compiler/labs/'}),
        'lectures': Store({'ai': '/path/to/ai/lectures/',
            'compiler': '/path/to/compiler/lectures/'})}
    g = Store(d)
    return g.lookup(ns.split())
