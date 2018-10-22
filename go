#!/usr/bin/env python3
import sys
import shelve
from shelve import Shelf
from sys import argv, exit
from os import environ
from argparse import ArgumentParser
from typing import List, Any, Dict, Union
from model import DefaultPath

def main(output=print) -> None:
    args = parse_arguments(argv[1:])
    if args.add:
        store(add(locations(), args.name, args.path))
        output(bullet(options(locations())))
        exit(3)
    elif args.remove:
        store(remove(locations(), args.name, args.path))
        output(bullet(options(locations())))
        exit(2)
    elif args.name is None:
        output('Available locations:')
        output(bullet(options(locations())))
        exit(1)
    else:
        try:
            output(lookup(locations(), args.name))
            exit(0)
        except KeyError:
            output(f'Couldn’t find {args.name} – available locations are:')
            output(bullet(options(locations())))
            exit(1)

def lookup(locations: Dict[str, str], name: str) -> str:
    return expand(locations[name])

def add(locations: Dict[str, str], name: str, path: Union[str, DefaultPath]) -> Dict[str, str]:
    if isinstance(path, DefaultPath):
        locations[name] = '.'
    else:
        locations[name] = path
    return locations

def remove(locations: Dict[str, str], name: str, path: Union[str, DefaultPath]) -> Dict[str, str]:
    if isinstance(path, DefaultPath) or locations[name] == path:
        del locations[name]
    return locations

def options(locations: Dict[str, str]) -> List[str]:
    return [f'{n} ({p})' for n, p in sorted(locations.items(), key=lambda t: t[1])]

def bullet(lines: List[str]) -> str:
    return '\n'.join(f'- {l}' for l in lines)

def locations() -> Dict[str, str]:
    with shelve.open('/Users/Noel/.go/go-file') as db:
        return db['locations']

def store(locations: Dict[str, str]) -> None:
    with shelve.open('/Users/Noel/.go/go-file') as db:
        db['locations'] = locations

def expand(s: str) -> str:
    return s.replace('~', environ['HOME'])

def parse_arguments(arguments: List[str]) -> Any:
    parser = ArgumentParser(description='Use and manage filesystem shortcuts.')
    parser.add_argument('--add', '-a', action='store_true')
    parser.add_argument('--remove', '-x', action='store_true')
    parser.add_argument('name', nargs='?', default=None)
    parser.add_argument('path', nargs='?', default=DefaultPath())
    return parser.parse_args(arguments)

if __name__ == '__main__':
    main()
