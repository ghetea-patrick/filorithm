# Filorithm

**Pick the files. Make the move.**

Filorithm gives everyday file chores a short, chainable Python interface. Select files or folders, narrow the list by name, size, extension, or date, then copy, move, or delete the result. Your Downloads folder has had a good run as an archaeological site.

[What it does](#what-it-does) · [Get started](#get-started) · [A quick example](#a-quick-example) · [How it fits together](#how-it-fits-together) · [Reference](#reference) · [Good to know](#good-to-know)

## What it does

- Collects the immediate files or folders inside a directory.
- Chains filters for names, extensions, sizes, and modification dates.
- Copies with `@`, moves with `>>`, and deletes with `~`.
- Includes reusable extension groups for images, documents, code, and more.
- Refuses existing destination names by default, unless you enable overwriting.

## Get started

> [!NOTE]
> Use **Python 3.10+**. Filorithm uses only the standard library.

Keep the project modules together on your Python import path:

| Module | What lives there |
| --- | --- |
| `files.py` | `Files` and its filter builder. |
| `families.py` | `Folders` and its filter builder. |
| `file_types.py` | Named extension groups, such as `IMAGES` and `DOCUMENTS`. |
| `storage.py` | Shared file operations and size conversion. |

```python
from files import Files
from families import Folders
from file_types import IMAGES
```

## A quick example

With an existing `downloads` directory, copy its image files into an image backup:

```python
from pathlib import Path
from files import Files
from file_types import IMAGES

backup = Path("image_backup")
backup.mkdir(exist_ok=True)

images = Files("downloads").filter().with_extensions(IMAGES).collect()

print([path.name for path in images])
images @ backup
```

The list shows the selected filenames before the copy. The source files stay where they are. Running the copy again raises `FileExistsError` if those destination names already exist.

## How it fits together

### Select, filter, collect, act

```python
from files import Files

reports = (
    Files("downloads")
    .filter()
    .with_extensions(("pdf", "csv"))
    .name_contains("report")
    .bigger_than(10, "kb")
    .collect()
)
```

`Files(...)` captures the directory's immediate files. `.filter()` starts a filter builder, each filter narrows its selection, and the builder's `.collect()` returns a new `Files` collection.

Folders follow the same pattern:

```python
from families import Folders

projects = Folders("workspace").filter().has_prefix("project_").collect()
print([path.name for path in projects])
```

### Choose an operation

| Expression | Action |
| --- | --- |
| `selection @ destination` | Copy each selected item into an existing directory. |
| `selection >> destination` | Move each selected item into an existing directory. |
| `~selection` | Delete each selected item; selected folders are removed recursively. |

The same operators work on `Files` and `Folders`. Each operation returns `None`.

> [!TIP]
> Inspect a selection before acting on it: iterate over it, check `len(selection)`, or print its `repr()`. Filtering alone does not copy, move, or delete anything.

### Work with paths directly

```python
from pathlib import Path
from files import Files

chosen = Files("", raw=[Path("notes.txt"), Path("summary.pdf")])
print(chosen[0])
print(len(chosen))
```

`raw=` accepts one path or a list or tuple of paths. It bypasses directory scanning; those paths need to exist when you perform an operation.

### Two kinds of collect

| Where you call it | What comes back |
| --- | --- |
| On a filter builder | A `Files` or `Folders` collection ready for an operation. |
| On a `Files` or `Folders` collection | Its underlying `list[Path]`. |

The list returned by a collection is the actual backing list. Make a copy if you want to edit it independently.

## Reference

### Filters shared by files and folders

| Filter | Keeps |
| --- | --- |
| `has_prefix(text)`, `has_suffix(text)` | Names beginning or ending with the text. |
| `name_contains(text)`, `name_lacks(text)` | Names containing or excluding the text. |
| `name_matches(regex)` | Names with a regex match; accepts a pattern string or compiled pattern. |
| `keep_only(names)`, `exclude(names)` | Exact names to keep or remove; accepts one name or a list or tuple. |
| `first(count)`, `last(count)` | A slice of the current selection. |
| `modified_between(start, end)` | Modification timestamps inside the inclusive range. |
| `modified_after(date)`, `modified_before(date)` | Modification timestamps strictly after or before a `datetime`. |

Name matching is case-sensitive. Regex filtering uses a search, so add anchors when you want a whole-name match.

### File-only filters

| Filter | Keeps |
| --- | --- |
| `with_extensions(exts)`, `without_extensions(exts)` | Files matching or excluding one extension or a list or tuple of extensions. |
| `bigger_than(size, unit)` | Files strictly larger than the limit. |
| `smaller_than(size, unit)` | Files strictly smaller than the limit. |
| `between_sizes(min_size, min_unit, max_size, max_unit)` | Files inside the inclusive size range. |
| `largest(count)`, `smallest(count)` | The requested number of files, ordered by size. |

Extensions are case-insensitive and may include a leading dot: `".PNG"` and `"png"` match the same suffix. Matching uses the final suffix, so `archive.tar.gz` has extension `gz`.

Size units are lowercase `"kb"`, `"mb"`, `"gb"`, and `"tb"`, using powers of 1024.

### Extension groups

Import these tuples from `file_types.py` and pass them straight into an extension filter:

| Group | Constants |
| --- | --- |
| Media | `AUDIO`, `IMAGES`, `VIDEOS`, `FONTS` |
| Documents and data | `DOCUMENTS`, `PRESENTATIONS`, `SPREADSHEETS`, `DATA` |
| Code | `CODE_ASSEMBLY`, `CODE_COMPILED`, `CODE_INTERPRETED`, `WEB` |
| Storage and system files | `ARCHIVES`, `EXECUTABLES`, `SYSTEM` |

### Existing destination names

Both collection constructors accept `overwrite=False`. The setting carries through filtering and applies to copy and move operations.

With `overwrite=True`, an existing destination item is removed before its replacement is copied or moved. For folders, replacement means replacing the destination tree, rather than merging it.

## Good to know

> [!CAUTION]
> `~selection` deletes directly, without a trash step or undo. `overwrite=True` can also remove an existing destination file or directory tree. Check the selected paths and destination before either operation.

- Source and destination directories must already exist. Filorithm does not create them automatically.
- Directory scanning is shallow. Selecting a folder and copying, moving, or deleting it operates on its whole tree.
- Directory iteration has no guaranteed sort order. `first()` and `last()` use the current order; `largest()` and `smallest()` explicitly sort by size.
- Operations process items in sequence. If a later item fails, earlier work is not rolled back.
- Collections store paths as a snapshot. After a move or deletion, create a fresh collection before doing more work with the changed locations.

