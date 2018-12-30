#!/usr/bin/env python3.7
import sys
from shelve import Shelf
from sys import argv, exit
from argparse import ArgumentParser, Action, Namespace
from typing import List, Any, Dict, Union, Tuple, Sequence, Optional, Callable
from pathlib import Path
from os import environ
from dataclasses import dataclass
import model as m

@dataclass
class Navigate:
    destination: str

@dataclass
class Display:
    message: str
    locations: Dict[str, str]
    exit: int

@dataclass
class Update:
    locations: Dict[str, str]

GoAction = Union[Navigate, Display, Update]

def main(output: Callable[[str], None]  = print) -> None:
    args = parse_arguments(argv[1:])
    action = take_action(m.locations(), args)
    if isinstance(action, Navigate):
        output("navigate")
        output(action.destination)
        exit(0)
    elif isinstance(action, Update):
        m.store(action.locations)
        exit(0)
    elif isinstance(action, Display):
        output("display")
        output(
            "\n".join([
                action.message,
                bullet(options(use_prefixes(action.locations)))
            ])
        )
        exit(action.exit)

def take_action(locations: Dict[str, str], args: Namespace) -> GoAction:
    if args.new:
        return Update(m.new(locations, args.new.name, args.new.path))
    elif args.delete:
        return Update(m.delete(locations, args.delete))
    elif args.rename:
        return Update(m.rename(locations, args.rename.old_name, args.rename.new_name))
    elif args.copy:
        return Update(m.copy(locations, args.copy.old_name, args.copy.new_name))
    elif args.name is None:
        return Display("Available locations:", locations, 0)
    else:
        p = m.lookup(locations, args.name)
        if isinstance(p, str):
            return Navigate(expand(p))
        elif isinstance(p, m.NoMatchError):
            return Display(
                f"Couldn’t find {args.name} – available locations are:",
                locations,
                1
            )
        elif isinstance(p, m.AmbiguousPrefixError):
            if args.name in p.matches:
                return Navigate(expand(p.matches[args.name]))
            else:
                return Display(
                    f"Got more than one match for {args.name}:",
                    p.matches,
                    2
                )
        else:
            return Display("Got an unknown error.", {}, 3)

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
    parser.add_argument("-n", "--new", action=NameAndPathAction)
    parser.add_argument("-d", "--delete")
    parser.add_argument("-r", "--rename", action=TwoNamesAction)
    parser.add_argument("-c", "--copy", action=TwoNamesAction)
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
        path: Union[m.DefaultPath, str] = (
            m.DefaultPath() if len(values) == 1 else values[1]
        )
        np = m.NameAndPath(name, path)
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
        ns = m.TwoNames(old_name=values[0], new_name=values[1])
        setattr(namespace, self.dest, ns)

if __name__ == "__main__":
    main()
