from pathlib import Path
from shutil import copy2, copytree, move, rmtree
from typing import Iterable, Literal


SizeUnit = Literal["kb", "mb", "gb", "tb"]


_MULTIPLIERS = {
    "kb": 1024,
    "mb": 1024**2,
    "gb": 1024**3,
    "tb": 1024**4,
}


def ensure_directory(path: str | Path) -> Path:
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"No such directory: '{p}'")
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: '{p}'")

    return p


def remove(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: '{path}'")

    if path.is_dir():
        rmtree(path)
    else:
        path.unlink()


def to_bytes(size: int, unit: SizeUnit) -> int:
    return size * _MULTIPLIERS[unit]


def copy_items(
    items: Iterable[Path],
    destination: str | Path,
    overwrite: bool = False,
) -> None:
    dest_dir = ensure_directory(destination)

    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")

        target = dest_dir / item.name

        if target.exists():
            if not overwrite:
                raise FileExistsError(f"Destination already exists: '{target}'")
            remove(target)

        if item.is_dir():
            copytree(item, target)
        else:
            copy2(item, target)


def move_items(
    items: Iterable[Path],
    destination: str | Path,
    overwrite: bool = False,
) -> None:
    dest_dir = ensure_directory(destination)

    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")

        target = dest_dir / item.name

        if target.exists():
            if not overwrite:
                raise FileExistsError(f"Destination already exists: '{target}'")
            remove(target)

        move(str(item), str(target))


def delete_items(items: Iterable[Path]) -> None:
    for item in items:
        if not item.exists():
            raise FileNotFoundError(f"No such file or directory: '{item}'")
        remove(item)