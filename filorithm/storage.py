from pathlib import Path
from shutil import copy2, copytree, move, rmtree
from typing import Literal

Unit = Literal["kb", "mb", "gb", "tb"]

_MULTIPLIERS = {"kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}


def to_bytes(size: int, unit: Unit) -> int:
    return size * _MULTIPLIERS[unit]


def sanitize_directory(raw: str | Path) -> Path:
    path = Path(raw)

    if not path.exists():
        raise FileNotFoundError(f"No such directory: '{path}'")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: '{path}'")

    return path


def remove(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: '{path}'")

    if path.is_dir():
        rmtree(path)
    else:
        path.unlink()


def copy_items(items: tuple[Path, ...] | list[Path], destination: str | Path, overwrite: bool = False) -> None:
    directory = sanitize_directory(destination)

    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")

        target = directory / item.name

        if target.exists():
            if target.resolve() == item.resolve():
                continue
            if not overwrite:
                raise FileExistsError(f"Destination already exists: '{target}'")
            remove(target)

        if item.is_dir():
            copytree(item, target)
        else:
            copy2(item, target)


def move_items(items: tuple[Path, ...] | list[Path], destination: str | Path, overwrite: bool = False) -> None:
    directory = sanitize_directory(destination)

    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")

        target = directory / item.name

        if target.exists():
            if target.resolve() == item.resolve():
                continue
            if not overwrite:
                raise FileExistsError(f"Destination already exists: '{target}'")
            remove(target)

        move(str(item), str(target))


def delete_items(items: tuple[Path, ...] | list[Path]) -> None:
    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")
        remove(item)
