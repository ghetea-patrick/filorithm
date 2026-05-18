from datetime import datetime
from pathlib import Path
from re import Pattern, compile
from typing import Sequence

from storage import (
    copy_items,
    delete_items,
    ensure_directory,
    move_items,
)


class FilterFolders:
    def __init__(self, folders: Sequence[Path], overwrite: bool) -> None:
        self._folders = list(folders)
        self._overwrite = overwrite

    def _filter(self, predicate):
        self._folders = [f for f in self._folders if predicate(f)]
        return self

    def exclude(self, names: Sequence[str]):
        banned = set(names)
        return self._filter(lambda f: f.name not in banned)

    def keep_only(self, names: Sequence[str]):
        allowed = set(names)
        return self._filter(lambda f: f.name in allowed)

    def last(self, count: int):
        self._folders = self._folders[-count:]
        return self

    def modified_after(self, dt: datetime):
        ts = dt.timestamp()
        return self._filter(lambda f: f.stat().st_mtime > ts)

    def modified_before(self, dt: datetime):
        ts = dt.timestamp()
        return self._filter(lambda f: f.stat().st_mtime < ts)

    def name_contains(self, text: str):
        return self._filter(lambda f: text in f.name)

    def name_endswith(self, suffix: str):
        return self._filter(lambda f: f.name.endswith(suffix))

    def name_matches(self, regex: str | Pattern):
        pattern = compile(regex) if isinstance(regex, str) else regex
        return self._filter(lambda f: bool(pattern.search(f.name)))

    def name_startswith(self, prefix: str):
        return self._filter(lambda f: f.name.startswith(prefix))

    def top(self, count: int):
        self._folders = self._folders[:count]
        return self

    def collect(self) -> "Folders":
        return Folders("", overwrite=self._overwrite, raw=self._folders)


class Folders:
    def __init__(
        self,
        directory: str | Path,
        *,
        overwrite: bool = False,
        raw: Sequence[Path] | None = None,
    ) -> None:
        self._overwrite = overwrite

        if raw is not None:
            self._folders = raw
        else:
            directory_path = ensure_directory(directory)
            self._folders = [
                f for f in directory_path.iterdir() if f.is_dir()
            ]

    def __iter__(self):
        return iter(self._folders)

    def __getitem__(self, index):
        return self._folders[index]

    def __repr__(self) -> str:
        return f"Folders({self._folders})"

    def __str__(self) -> str:
        return str(self._folders)

    def __rshift__(self, destination: str | Path) -> None:
        move_items(self._folders, destination, self._overwrite)

    def __matmul__(self, destination: str | Path) -> None:
        copy_items(self._folders, destination, self._overwrite)

    def __invert__(self) -> None:
        delete_items(self._folders)

    def collect(self) -> Sequence[Path]:
        return self._folders

    def filter(self) -> FilterFolders:
        return FilterFolders(self._folders, self._overwrite)