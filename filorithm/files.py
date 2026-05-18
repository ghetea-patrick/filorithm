from datetime import datetime
from pathlib import Path
from re import Pattern, compile
from typing import Sequence

from storage import (
    SizeUnit,
    copy_items,
    delete_items,
    ensure_directory,
    move_items,
    to_bytes,
)


class FilterFiles:
    def __init__(self, files: Sequence[Path], overwrite: bool) -> None:
        self._files = list(files)
        self._overwrite = overwrite

    def _filter(self, predicate):
        self._files = [f for f in self._files if predicate(f)]
        return self

    def between_sizes(
        self,
        min_size: int,
        min_unit: SizeUnit,
        max_size: int,
        max_unit: SizeUnit,
    ):
        lower = to_bytes(min_size, min_unit)
        upper = to_bytes(max_size, max_unit)
        return self._filter(
            lambda f: lower <= f.stat().st_size <= upper
        )

    def bigger_than(self, size: int, unit: SizeUnit):
        limit = to_bytes(size, unit)
        return self._filter(lambda f: f.stat().st_size > limit)

    def exclude(self, filenames: Sequence[str]):
        banned = set(filenames)
        return self._filter(lambda f: f.name not in banned)

    def keep_only(self, filenames: Sequence[str]):
        allowed = set(filenames)
        return self._filter(lambda f: f.name in allowed)

    def largest(self, count: int):
        self._files = sorted(
            self._files,
            key=lambda f: f.stat().st_size,
            reverse=True,
        )[:count]
        return self

    def last(self, count: int):
        self._files = self._files[-count:]
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

    def smallest(self, count: int):
        self._files = sorted(
            self._files,
            key=lambda f: f.stat().st_size,
        )[:count]
        return self

    def smaller_than(self, size: int, unit: SizeUnit):
        limit = to_bytes(size, unit)
        return self._filter(lambda f: f.stat().st_size < limit)

    def top(self, count: int):
        self._files = self._files[:count]
        return self

    def with_extensions(self, extensions: Sequence[str]):
        norm = {e.lower().lstrip(".") for e in extensions}
        return self._filter(
            lambda f: f.suffix.lower().lstrip(".") in norm
        )

    def without_extensions(self, extensions: Sequence[str]):
        norm = {e.lower().lstrip(".") for e in extensions}
        return self._filter(
            lambda f: f.suffix.lower().lstrip(".") not in norm
        )

    def collect(self) -> "Files":
        return Files("", overwrite=self._overwrite, raw=self._files)


class Files:
    def __init__(
        self,
        directory: str | Path,
        *,
        overwrite: bool = False,
        raw: Sequence[Path] | None = None,
    ) -> None:
        self._overwrite = overwrite

        if raw is not None:
            self._files = raw
        else:
            directory_path = ensure_directory(directory)
            self._files = [
                f for f in directory_path.iterdir() if f.is_file()
            ]

    def __iter__(self):
        return iter(self._files)

    def __getitem__(self, index):
        return self._files[index]

    def __repr__(self) -> str:
        return f"Files({self._files})"

    def __str__(self) -> str:
        return str(self._files)

    def __rshift__(self, destination: str | Path) -> None:
        move_items(self._files, destination, self._overwrite)

    def __matmul__(self, destination: str | Path) -> None:
        copy_items(self._files, destination, self._overwrite)

    def __invert__(self) -> None:
        delete_items(self._files)

    def collect(self) -> Sequence[Path]:
        return self._files

    def filter(self) -> FilterFiles:
        return FilterFiles(self._files, self._overwrite)