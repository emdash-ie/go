from typing import Dict

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
