#!/usr/bin/env python3.7
import sys
from shelve import Shelf
from sys import argv, exit
from argparse import ArgumentParser, Action, Namespace
from typing import List, Any, Dict, Union, Tuple
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
    lookup
)

def main(output=print) -> None:
    args = parse_arguments(argv[1:])
    to_add = NameAndPath.from_list(args.add)
    to_remove = NameAndPath.from_list(args.remove)
    if to_add:
        store(add(locations(), to_add.name, to_add.path))
        exit(2)
    elif to_remove:
        store(remove(locations(), to_remove.name, to_remove.path))
        exit(2)
    elif args.rename is not None:
        old_name, new_name = args.rename
        store(rename(locations(), old_name, new_name))
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
    parser.add_argument("-a", "--add", nargs="+")
    parser.add_argument("-x", "--remove", nargs="+")
    parser.add_argument("-r", "--rename", nargs=2)
    parser.add_argument("name", nargs="?", default=None)
    return parser.parse_args(arguments)

if __name__ == "__main__":
    main()
