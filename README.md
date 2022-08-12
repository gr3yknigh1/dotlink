# dotlink

Stow analog which written in python

## Installation

Currently project only avaible on *github*.

**from source**:

```shell
git clone https://github.com/gr3yknigh1/dotlink
pip install dotlink
```

## Terminology

- `package` - folder which structure represent where file's links must be placed in base directory

## Usage

Print usage:

```shell
dotlink --help
```

Link package:

```shell
dotlink <package-name>
```

Remove package:

`dotlink` by default will be try to search for packages in `~/.dotfiles`.

Override default package path:

```
dotlink -p <path-to-pkgs> <package-name>
```

Override default base path:

```shell
dotlink -b <path-to-base> <package-name>
```

For dry run add `-n` or `--dry-run` flag:

```
dotlink -n <package-name>
```

