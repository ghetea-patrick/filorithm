from datetime import datetime
from pathlib import Path
from re import Pattern, compile

from storage import Unit, copy_items, delete_items, move_items, sanitize_directory, to_bytes


class FilterFiles:
    def __init__(self, files: tuple[Path, ...] | list[Path], overwrite: bool) -> None:
        self._files = list(files)
        self._overwrite = overwrite

    def _filter(self, predicate):
        self._files = [file for file in self._files if predicate(file)]
        return self

    def between_sizes(self, min_size: int, min_unit: Unit, max_size: int, max_unit: Unit):
        lower = to_bytes(min_size, min_unit)
        upper = to_bytes(max_size, max_unit)
        return self._filter(lambda file: lower <= file.stat().st_size <= upper)

    def bigger_than(self, size: int, unit: Unit):
        limit = to_bytes(size, unit)
        return self._filter(lambda file: file.stat().st_size > limit)

    def smaller_than(self, size: int, unit: Unit):
        limit = to_bytes(size, unit)
        return self._filter(lambda file: file.stat().st_size < limit)

    def largest(self, count: int):
        self._files = sorted(self._files, key=(lambda file: file.stat().st_size), reverse=True)[:count]
        return self

    def smallest(self, count: int):
        self._files = sorted(self._files, key=(lambda file: file.stat().st_size))[:count]
        return self

    def has_prefix(self, prefix: str):
        return self._filter(lambda file: file.name.startswith(prefix))

    def has_suffix(self, suffix: str):
        return self._filter(lambda file: file.name.endswith(suffix))

    def first(self, count: int):
        self._files = self._files[:count]
        return self

    def last(self, count: int):
        self._files = self._files[-count:]
        return self

    def keep_only(self, filenames: str | tuple[str, ...] | list[str]):
        names = (filenames,) if isinstance(filenames, str) else filenames
        allowed = set(names)
        return self._filter(lambda file: file.name in allowed)

    def exclude(self, filenames: str | tuple[str, ...] | list[str]):
        names = (filenames,) if isinstance(filenames, str) else filenames
        banned = set(names)
        return self._filter(lambda file: file.name not in banned)

    def with_extensions(self, extensions: str | tuple[str, ...] | list[str]):
        exts = (extensions,) if isinstance(extensions, str) else extensions
        normalized = {extension.lower().lstrip(".") for extension in exts}
        return self._filter(lambda file: file.suffix.lower().lstrip(".") in normalized)

    def without_extensions(self, extensions: str | tuple[str, ...] | list[str]):
        exts = (extensions,) if isinstance(extensions, str) else extensions
        normalized = {extension.lower().lstrip(".") for extension in exts}
        return self._filter(lambda file: file.suffix.lower().lstrip(".") not in normalized)

    def name_lacks(self, text: str):
        return self._filter(lambda file: text not in file.name)

    def name_contains(self, text: str):
        return self._filter(lambda file: text in file.name)

    def name_matches(self, regex: str | Pattern):
        pattern = compile(regex) if isinstance(regex, str) else regex
        return self._filter(lambda file: bool(pattern.search(file.name)))

    def modified_between(self, start: datetime, end: datetime):
        timestamp_start = start.timestamp()
        timestamp_end = end.timestamp()
        return self._filter(lambda file: timestamp_start <= file.stat().st_mtime <= timestamp_end)

    def modified_after(self, date: datetime):
        timestamp = date.timestamp()
        return self._filter(lambda file: file.stat().st_mtime > timestamp)

    def modified_before(self, date: datetime):
        timestamp = date.timestamp()
        return self._filter(lambda file: file.stat().st_mtime < timestamp)

    def collect(self) -> "Files":
        return Files("", overwrite=self._overwrite, raw=self._files)


class Files:
    def __init__(self, source: str | Path, overwrite: bool = False, raw: str | Path | tuple[Path, ...] | list[Path] | None = None) -> None:
        self._overwrite = overwrite

        if raw is not None:
            if isinstance(raw, (str, Path)):
                self._files = [Path(raw)]
            else:
                self._files = [Path(item) for item in raw]
        else:
            directory = sanitize_directory(source)
            self._files = [file for file in directory.iterdir() if file.is_file()]

    def __iter__(self):
        return iter(self._files)

    def __getitem__(self, index):
        return self._files[index]

    def __len__(self) -> int:
        return len(self._files)

    def __repr__(self) -> str:
        return f"<not implemented>"

    def __str__(self) -> str:
        return "not implemented"

    def __rshift__(self, destination: str | Path) -> None:
        directory = sanitize_directory(destination)
        move_items(self._files, directory, self._overwrite)

    def __matmul__(self, destination: str | Path) -> None:
        directory = sanitize_directory(destination)
        copy_items(self._files, directory, self._overwrite)

    def __invert__(self) -> None:
        delete_items(self._files)

    def collect(self) -> list[Path]:
        return self._files

    def filter(self) -> FilterFiles:
        return FilterFiles(self._files, self._overwrite)
