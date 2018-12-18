#!/usr/bin/env python3.7
import sys
from shelve import Shelf
from sys import argv, exit
from argparse import ArgumentParser, Action, Namespace
from typing import List, Any, Dict, Union, Tuple, Sequence, Optional
from pathlib import Path
from os import environ
from model import (
    DefaultPath,
    Store,
    PathLookupError,
    NoMatchError,
    AmbiguousPrefixError,
    prefix_match,
    NameAndPath,
    store,
    add,
    locations,
    remove,
    rename,
    lookup,
    TwoNames
)

def main(output=print) -> None:
    args = parse_arguments(argv[1:])
    if args.add:
        store(add(locations(), args.add.name, args.add.path))
        exit(2)
    elif args.remove:
        store(remove(locations(), args.remove))
        exit(2)
    elif args.rename:
        store(rename(locations(), args.rename.old_name, args.rename.new_name))
        exit(2)
    elif args.name is None:
        output("Available locations:")
        output(bullet(options(use_prefixes(locations()))))
        exit(1)
    else:
        p = lookup(locations(), args.name)
        if isinstance(p, str):
            output(expand(p))
            exit(0)
        elif isinstance(p, NoMatchError):
            output(f"Couldn’t find {args.name} – available locations are:")
            output(bullet(options(locations())))
            exit(1)
        elif isinstance(p, AmbiguousPrefixError):
            if args.name in p.matches:
                output(expand(p.matches[args.name]))
                exit(0)
            else:
                output(f"Got more than one match for {args.name}:")
                output(bullet(options(use_prefixes(p.matches))))
                exit(1)

def options(locations: Dict[str, str]) -> List[str]:
    shortcuts = locations.items()
    max_path_length = max(map(lambda s: len(s[0]), shortcuts))
    return [f"{n:<{max_path_length}} ({p})" for n, p in sorted(shortcuts, key=lambda t: t[0])]

def use_prefixes(locations: Dict[str, str]) -> Dict[str, str]:
    tuples = (use_prefix(locations, (n, p)) for n, p in locations.items())
    return {n: p for n, p in tuples}

def use_prefix(
        locations: Dict[str, str],
        location: Tuple[str, str]) -> Tuple[str, str]:
    n1, p1 = location
    prefixes = [
        (n, p) for n, p in locations.items()
        if p != p1 and p1.startswith(p)
    ]
    if prefixes == []:
        return n1, p1
    else:
        n2, p2 = max(
            prefixes,
            key = lambda t: len(t[1])
        )
        if len(p2) < 3:
            return n1, p1
        return n1, p1.replace(f"{p2}/", f"{n2} -> ")


def bullet(lines: List[str]) -> str:
    return "\n".join(f"- {l}" for l in lines)

def expand(s: str) -> str:
    return s.replace("~", environ["HOME"])

def parse_arguments(arguments: List[str]) -> Namespace:
    parser = ArgumentParser(description="Use and manage filesystem shortcuts.")
    parser.add_argument("-a", "--add", action=NameAndPathAction)
    parser.add_argument("-x", "--remove")
    parser.add_argument("-r", "--rename", action=TwoNamesAction)
    parser.add_argument("name", nargs="?", default=None)
    return parser.parse_args(arguments)

class NameAndPathAction(Action):
    def __init__(self, *args,  **kwargs):
        super().__init__(nargs="+", *args, **kwargs)
    def __call__( # type: ignore
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: List[str],
        option_string: str,
    ) -> None:
        name = values[0]
        path: Union[DefaultPath, str] = (
            DefaultPath() if len(values) == 1 else values[1]
        )
        np = NameAndPath(name, path)
        setattr(namespace, self.dest, np)

class TwoNamesAction(Action):
    def __init__(self, *args,  **kwargs):
        super().__init__(nargs=2, *args, **kwargs)
    def __call__( # type: ignore
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: List[str],
        option_string: str,
    ) -> None:
        ns = TwoNames(old_name=values[0], new_name=values[1])
        setattr(namespace, self.dest, ns)

if __name__ == "__main__":
    main()
