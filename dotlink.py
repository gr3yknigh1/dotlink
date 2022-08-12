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


def remove(target: str, is_not_link_ok = True) -> None:
    if not os.path.islink(target):
        if not is_not_link_ok:
            raise TypeError("Target must be link")
        return
    os.remove(target)


def link(src: str, dst: str, is_force: bool) -> None:
    if os.path.exists(dst):
        if not is_force:
            raise FileExistsError(f"File already exists: '{dst}'")
        remove(dst)
    os.symlink(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("-b", "--base-dir", default=HOME_DIR, dest="base_dir")
    parser.add_argument(
        "-p",
        "--pkg-base",
        default=DOTFILES, dest="package_base"
    )
    parser.add_argument(
        "--link-dirs",
        action="store_true",
        dest="link_dirs",
        default=False
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        dest="is_dry_run",
        default=False
    )
    parser.add_argument(
        "-R",
        "--remove",
        action="store_true",
        dest="do_remove",
        default=False
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="is_force",
        default=False
    )

    args = parser.parse_args()

    package_name = args.package
    package_base = args.package_base
    base_dir = args.base_dir
    link_dirs = args.link_dirs
    is_dry_run = args.is_dry_run
    do_remove = args.do_remove
    is_force = args.is_force

    if link_dirs:
        raise NotImplementedError


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

        for file_name in file_names:
            link_maps.append({
                "src": os.path.join(dir_path, file_name),
                "dst": os.path.join(dest_path, file_name)
            })

    # pprint.pprint(link_maps)

    action_fnc: ActionFnc
    if do_remove:
        action_fnc = lambda src, dst: remove(dst)
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

