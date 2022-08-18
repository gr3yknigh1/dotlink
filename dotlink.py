#!/usr/bin/env python
"""
Stow analog which written in python

TODO:
    - [ ] Add config file support
    - [X] Add option for linking directories
    - [ ] Add support for package mapping
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from typing import TypeAlias

    Action: TypeAlias = Callable[[Link], None]
import os
import os.path
import argparse
import dataclasses


__version__ = "0.3"


HOME_DIR = os.path.expanduser("~")
DOTFILES = os.path.join(HOME_DIR, ".dotfiles")
DOTFOLDERNAME = ".dotfolder"


@dataclasses.dataclass
class Link:
    dst: str
    src: str


def make_link(link: Link, is_force: bool) -> None:
    if os.path.exists(link.dst):
        if not is_force:
            raise Exception(f"Path already exists: '{link.dst}'")

        if os.path.isdir(link.dst):
            os.rmdir(link.dst)
        else:
            os.remove(link.dst)

    os.symlink(link.src, link.dst)


def process_link(link: Link, action: Action) -> None:
    action(link)


def link_package(
    package_name: str,
    package_base: str,
    base_dir: str,
    is_dry_run: bool,
    is_force: bool,
    do_remove: bool,
) -> None:

    package_path = os.path.join(package_base, package_name)
    package_path = package_path.removesuffix("/")

    for path in (package_base, base_dir, package_path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path doesn't exists: '{path}'")

    links: list[Link] = []

    dotfolder_paths: list[str] = []

    for dir_path, dir_paths, file_names in os.walk(package_path):

        content_path = dir_path[len(package_path) + 1:]

        dest_path = (
            os.path.join(
                base_dir,
                content_path
            ) if len(content_path) > 0 else base_dir
        )

        if DOTFOLDERNAME in file_names:
            dotfolder_paths.append(dest_path)
            links.append(Link(dest_path, dir_path))

        if (
            len(dotfolder_paths) > 0
            and dest_path.removeprefix(dotfolder_paths[-1]) != dest_path
        ):
            continue

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        for file_name in file_names:
            links.append(
                Link(
                    src=os.path.join(dir_path, file_name),
                    dst=os.path.join(dest_path, file_name),
                )
            )

    action: Action

    if do_remove:
        if is_dry_run:
            action = lambda link: print(f"removing: {link.dst}")
        else:
            action = lambda link: os.unlink(link.dst)
    else:
        if is_dry_run:
            action = lambda link: print(f"linking: {link.src} -> {link.dst}")
        else:
            action = lambda link: make_link(link, is_force)

    for link in links[::-1]:
        process_link(link, action)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument(
        "-b",
        default=HOME_DIR,
        dest="base_dir",
        help="Directory where will be placed all packages",
    )
    parser.add_argument(
        "-p",
        default=DOTFILES,
        dest="package_base",
        help="Path which used for package lookup",
    )
    parser.add_argument(
        "-n",
        action="store_true",
        dest="is_dry_run",
        default=False,
        help="Instead of doing something, \
                just print which actions will be executed",
    )
    parser.add_argument(
        "-R",
        action="store_true",
        dest="do_remove",
        default=False,
        help="Remove package's links",
    )
    parser.add_argument(
        "-f",
        action="store_true",
        dest="is_force",
        default=False,
        help="Relink package If package already linked",
    )

    args = parser.parse_args()

    package_name = args.package
    package_base = args.package_base
    base_dir = args.base_dir
    is_dry_run = args.is_dry_run
    do_remove = args.do_remove
    is_force = args.is_force

    link_package(
        package_name=package_name,
        package_base=package_base,
        base_dir=base_dir,
        is_dry_run=is_dry_run,
        is_force=is_force,
        do_remove=do_remove,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
