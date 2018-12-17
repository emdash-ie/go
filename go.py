#!/usr/bin/env python3.7
import sys
import shelve
from shelve import Shelf
from sys import argv, exit
from os import environ, getcwd
from argparse import ArgumentParser, Action, Namespace
from typing import List, Any, Dict, Union, Tuple
from pathlib import Path
from model import (
    DefaultPath,
    Store,
    PathLookupError,
    NoMatchError,
    AmbiguousPrefixError,
    prefix_match,
    NameAndPath
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

def lookup(locations: Dict[str, str], name: str) -> Union[str, PathLookupError]:
    return prefix_match(locations, name)

def add(locations: Dict[str, str], name: str, path: Union[str, DefaultPath]) -> Dict[str, str]:
    if isinstance(path, DefaultPath):
        path = getcwd()
    locations[name] = use_tilde(path)
    return locations

def remove(locations: Dict[str, str], name: str, path: Union[str, DefaultPath]) -> Dict[str, str]:
    if isinstance(path, DefaultPath) or locations[name] == path:
        del locations[name]
    return locations

def rename(locations: Dict[str, str], old_name: str, new_name: str) -> Dict[str, str]:
    p = locations.get(old_name)
    if p is not None:
        del locations[old_name]
        locations[new_name] = p
    return locations

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

def go_file() -> str:
    return environ["HOME"] + "/.go/go-file"

def locations() -> Dict[str, str]:
    with shelve.open(go_file()) as db:
        return db["locations"]

def store(locations: Dict[str, str]) -> None:
    with shelve.open(go_file()) as db:
        db["locations"] = locations

def expand(s: str) -> str:
    return s.replace("~", environ["HOME"])

def use_tilde(s: str) -> str:
    if s.startswith(environ["HOME"]):
        return s.replace(environ["HOME"], "~", 1)
    else:
        return s

def parse_arguments(arguments: List[str]) -> Namespace:
    parser = ArgumentParser(description="Use and manage filesystem shortcuts.")
    parser.add_argument("-a", "--add", nargs="+")
    parser.add_argument("-x", "--remove", nargs="+")
    parser.add_argument("-r", "--rename", nargs=2)
    parser.add_argument("name", nargs="?", default=None)
    return parser.parse_args(arguments)

if __name__ == "__main__":
    main()
