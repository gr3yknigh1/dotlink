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
    ActionFnc: TypeAlias = Callable[[str, str], None]
import pprint
import os
import os.path
import argparse


HOME_DIR = os.path.expanduser("~")
DOTFILES = os.path.join(HOME_DIR, ".dotfiles")
DOTFOLDERNAME = ".dotfolder"


def remove_link(target: str) -> None:
    if not os.path.islink(target):
        raise TypeError("Target must be link")
    os.unlink(target)


def link(src: str, dst: str, is_force: bool) -> None:
    if os.path.exists(dst):
        if not is_force:
            raise Exception(f"Path already exists: '{dst}'")

        if os.path.isdir(dst):
            os.rmdir(dst)
        else:
            os.remove(dst)

    os.symlink(src, dst)


def link_package(
        package_name: str,
        package_base: str,
        base_dir: str,
        is_dry_run: bool,
        is_force: bool,
        do_remove: bool,
    ) -> None:

    package_path = os.path.join(package_base, package_name)
    package_path = package_path.removesuffix('/')

    for path in (package_base, base_dir, package_path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path doesn't exists: '{path}'")

    link_maps = []

    for dir_path, dir_paths, file_names in os.walk(package_path):
        if len(file_names) == 0:
            continue


        content_path = dir_path[len(package_path) + 1:]

        dest_path = os.path.join(
            base_dir,
            content_path
        ) if len(content_path) > 0 else base_dir

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        if DOTFOLDERNAME in file_names:
            link_maps.append({
                "src": dir_path,
                "dst": dest_path
            })
            continue

        for file_name in file_names:
            link_maps.append({
                "src": os.path.join(dir_path, file_name),
                "dst": os.path.join(dest_path, file_name)
            })

    # pprint.pprint(link_maps)

    action_fnc: ActionFnc
    if do_remove:
        action_fnc = lambda src, dst: remove_link(dst)
        action_fnc = action_fnc        \
                     if not is_dry_run \
                     else lambda src, dst: print(f"removing: {dst}")
    else:
        action_fnc = lambda src, dst: link(src, dst, is_force)
        action_fnc = action_fnc        \
                     if not is_dry_run \
                     else lambda src, dst: print(f"linking: {src} -> {dst}")


    for link_map in link_maps:
        action_fnc(**link_map)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument(
        "-b",
        default=HOME_DIR,
        dest="base_dir",
        help="Directory where will be placed all packages"
    )
    parser.add_argument(
        "-p",
        default=DOTFILES, dest="package_base",
        help="Path which used for package lookup"
    )
    parser.add_argument(
        "-n",
        action="store_true",
        dest="is_dry_run",
        default=False,
        help="Instead of doing something, just print which actions will be executed"
    )
    parser.add_argument(
        "-R",
        action="store_true",
        dest="do_remove",
        default=False,
        help="Remove package's links"
    )
    parser.add_argument(
        "-f",
        action="store_true",
        dest="is_force",
        default=False,
        help="Relink package If package already linked"
    )

    args = parser.parse_args()

    package_name = args.package
    package_base = args.package_base
    base_dir = args.base_dir
    is_dry_run = args.is_dry_run
    do_remove = args.do_remove
    is_force = args.is_force

    link_package(
        package_name,
        package_base,
        base_dir,
        is_dry_run,
        is_force,
        do_remove
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
