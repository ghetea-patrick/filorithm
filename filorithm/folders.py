from datetime import datetime
from pathlib import Path
from re import Pattern, compile

from storage import copy_items, delete_items, move_items, sanitize_directory


class FilterFolders:
    def __init__(self, folders: tuple[Path, ...] | list[Path], overwrite: bool) -> None:
        self._folders = list(folders)
        self._overwrite = overwrite

    def _filter(self, predicate):
        self._folders = [folder for folder in self._folders if predicate(folder)]
        return self

    def has_prefix(self, prefix: str):
        return self._filter(lambda folder: folder.name.startswith(prefix))

    def has_suffix(self, suffix: str):
        return self._filter(lambda folder: folder.name.endswith(suffix))

    def first(self, count: int):
        self._folders = self._folders[:count]
        return self

    def last(self, count: int):
        self._folders = self._folders[-count:]
        return self

    def keep_only(self, foldernames: str | tuple[str, ...] | list[str]):
        names = (foldernames,) if isinstance(foldernames, str) else foldernames
        allowed = set(names)
        return self._filter(lambda folder: folder.name in allowed)

    def exclude(self, foldernames: str | tuple[str, ...] | list[str]):
        names = (foldernames,) if isinstance(foldernames, str) else foldernames
        banned = set(names)
        return self._filter(lambda folder: folder.name not in banned)

    def name_lacks(self, text: str):
        return self._filter(lambda folder: text not in folder.name)

    def name_contains(self, text: str):
        return self._filter(lambda folder: text in folder.name)

    def name_matches(self, regex: str | Pattern):
        pattern = compile(regex) if isinstance(regex, str) else regex
        return self._filter(lambda folder: bool(pattern.search(folder.name)))

    def modified_between(self, start: datetime, end: datetime):
        timestamp_start = start.timestamp()
        timestamp_end = end.timestamp()
        return self._filter(lambda folder: timestamp_start <= folder.stat().st_mtime <= timestamp_end)

    def modified_after(self, date: datetime):
        timestamp = date.timestamp()
        return self._filter(lambda folder: folder.stat().st_mtime > timestamp)

    def modified_before(self, date: datetime):
        timestamp = date.timestamp()
        return self._filter(lambda folder: folder.stat().st_mtime < timestamp)

    def collect(self) -> "Folders":
        return Folders("", overwrite=self._overwrite, raw=self._folders)


class Folders:
    def __init__(self, source: str | Path, overwrite: bool = False, raw: str | Path | tuple[Path, ...] | list[Path] | None = None) -> None:
        self._overwrite = overwrite

        if raw is not None:
            if isinstance(raw, (str, Path)):
                self._folders = [Path(raw)]
            else:
                self._folders = [Path(item) for item in raw]
        else:
            directory = sanitize_directory(source)
            self._folders = [folder for folder in directory.iterdir() if folder.is_dir()]

    def __iter__(self):
        return iter(self._folders)

    def __getitem__(self, index):
        return self._folders[index]

    def __len__(self) -> int:
        return len(self._folders)

    def __repr__(self) -> str:
        return f"<not implemented>"

    def __str__(self) -> str:
        return "not implemented"

    def __rshift__(self, destination: str | Path) -> None:
        directory = sanitize_directory(destination)
        move_items(self._folders, directory, self._overwrite)

    def __matmul__(self, destination: str | Path) -> None:
        directory = sanitize_directory(destination)
        copy_items(self._folders, directory, self._overwrite)

    def __invert__(self) -> None:
        delete_items(self._folders)

    def collect(self) -> list[Path]:
        return self._folders

    def filter(self) -> FilterFolders:
        return FilterFolders(self._folders, self._overwrite)
