# Filorithm

**Find the files. Do the thing. Retire a few nested loops.**

Filorithm is a lightweight Python utility for files, directories, filtering, and batch storage operations. It builds on `pathlib` and `shutil`, giving you a readable way to select items and then copy, move, or delete them together.

If a simple file task keeps turning into three loops and an `os.path.join()` expedition, this is the shorter route through the same filesystem.

[What it does](#what-it-does) · [Get started](#get-started) · [A quick example](#a-quick-example) · [How it fits together](#how-it-fits-together) · [Reference](#reference) · [Examples](#examples) · [Good to know](#good-to-know) · [Design notes](#design-notes)

> [!IMPORTANT]
> The file-family module has been renamed from **`file_types.py`** to **`families.py`** as part of the project's cleanup and standardization. The examples in this README use `filorithm.families`. Update older imports that still point to `filorithm.file_types`.

## What it does

- Supplies predefined extension families for archives, media, code, data, documents, executables, fonts, presentations, spreadsheets, system files, and web files.
- Collects files with `Files` and directories with `Folders`.
- Builds chainable filters for names, prefixes, suffixes, regex patterns, and modification dates, with extension and size filtering for files.
- Supports readable size amounts and units, including kilobytes, megabytes, gigabytes, and terabytes.
- Copies, moves, and deletes selected items through the `@`, `>>`, and `~` operators.
- Resolves paths and sanitizes directory inputs automatically.
- Handles individual files, multiple files, and entire directories through the collection and storage interfaces.
- Works with standard Python `Path` and `datetime` objects.

## Get started

> [!NOTE]
> Filorithm uses only Python's standard library. Replace `filorithm` in the imports if your installation uses another package path.

```python
from filorithm.files import Files
from filorithm.folders import Folders
from filorithm.families import IMAGES, VIDEOS
```

For an older checkout, the relevant import change is:

| Older path | Current path |
| --- | --- |
| `filorithm.file_types` | `filorithm.families` |

The examples use ordinary filesystem paths. Replace the sample paths with directories appropriate to your own environment.

## A quick example

Collect interpreted-code files and copy them to a backup directory:

```python
from filorithm.files import Files
from filorithm.families import CODE_INTERPRETED

scripts = Files("/scripts").filter().with_extensions(CODE_INTERPRETED).collect()

scripts @ "/backup/scripts"
```

`Files("/scripts")` selects the source directory. `filter()` starts a builder, `with_extensions()` narrows the selection, and `collect()` returns a new `Files` collection. The `@` operator then copies that selection.

No matrix algebra is involved. Python simply lent the operator to another department.

## How it fits together

### Collect files

Constructing `Files` reads the files in the specified directory:

```python
source_files = Files("/path/to/directory")
```

You can also supply raw paths directly:

```python
source_files = Files(
    "/path/to/directory",
    raw=["file1.txt", "file2.txt"]
)
```

The collection is iterable and supports indexing. For example, iterate over it to inspect each filename:

```python
for file in source_files:
    print(file.name)
```

### Build a file filter

`Files.filter()` returns a `FilterFiles` builder. Chain criteria to narrow your selection, then collect the results.

#### Include or exclude extensions

Use a list or a predefined extension tuple:

```python
images = Files("/downloads").filter().with_extensions(IMAGES).collect()
```

To exclude a family, import that family and use `without_extensions()`:

```python
from filorithm.families import EXECUTABLES
```

```python
safe_files = Files("/downloads").filter().without_extensions(EXECUTABLES).collect()
```

The variable name `safe_files` here only describes the extension-based selection. The filter excludes the listed executable extensions; it does not inspect file contents.

#### Match names

Name filters support prefixes, suffixes, regex patterns, and text matching. These examples show prefix matching, substring matching, and keeping an explicit filename:

```python
reports = Files("/docs").filter().has_prefix("report_").collect()

old_files = Files("/docs").filter().name_contains("backup").collect()

specific = Files("/docs").filter().keep_only(["config.json"]).collect()
```

`has_prefix("report_")` keeps names beginning with `report_`. `name_contains("backup")` keeps names containing that text, and `keep_only(["config.json"])` restricts the selection to the given name.

#### Filter by modification date

Date filtering accepts standard Python `datetime` values:

```python
from datetime import datetime

cutoff = datetime(2026, 1, 1)

recent = Files("/docs").filter().modified_after(cutoff).collect()
```

Here, `modified_after(cutoff)` selects files modified after January 1, 2026. `modified_before(cutoff)` is used in the complete example below to select older files.

#### Filter by size

You can filter by size on disk using an amount and unit:

```python
from filorithm.storage import Unit

large = Files("/media").filter().bigger_than(500, "mb").collect()
```

This selects files bigger than 500 MB. `Unit` is available from the storage module; the example passes the unit as the string `"mb"` and does not need to reference `Unit` directly.

You can also select the largest or smallest files. For example, collect the ten largest:

```python
top_ten = Files("/media").filter().largest(10).collect()
```

> [!IMPORTANT]
> Finish a filter chain with **`collect()`**. The chain builds conditions; `collect()` returns a new `Files` object containing the selected results.

### Collect and filter folders

`Folders` follows the same collection pattern, targeting directories instead of files:

```python
folders = Folders("/var/log")
```

Its `filter()` method returns a `FilterFolders` builder:

```python
backups = Folders("/var/log").filter().name_contains("backup").collect()
```

Folder filtering supports prefixes, suffixes, name content, regex patterns, and modification dates. Use `collect()` to finish the selection here too.

### Apply a batch operation

The same storage operators work with both `Files` and `Folders`:

| Operator | Action | Example form |
| --- | --- | --- |
| `>>` | Move the collected items to a destination directory. | `items >> "/destination"` |
| `@` | Copy the collected items to a destination directory. | `items @ "/destination"` |
| `~` | Delete the collected items from disk. | `~items` |

#### Move items with `>>`

```python
images = Files("/downloads").filter().with_extensions(IMAGES).collect()

images >> "/pictures/memes"
```

All selected images move into the memes directory. Their journey is your business; Filorithm handles the moving.

#### Copy items with `@`

```python
documents = Files("/work")

documents @ "/backup/work"
```

This copies the files collected from `/work` into `/backup/work`. The collection determines the scope of the operation.

#### Delete items with `~`

> [!CAUTION]
> **`~items` permanently removes the selected files or folders from disk.** Inspect the selection before applying it. This is a filesystem deletion, not a move to a recycle bin.

```python
temp_files = Files("/tmp").filter().name_contains("cache").collect()

~temp_files
```

In this example, the deletion applies to files in `/tmp` whose names contain `cache`.

#### Choose overwrite behavior explicitly

By default, a storage operation raises `FileExistsError` when a destination file already exists. Enable overwriting when constructing the collection if that is the behavior you intend:

```python
Files("/downloads", overwrite=True) >> "/pictures"
```

> [!WARNING]
> `overwrite=True` opts into replacing existing destination files. Choose the destination and collection deliberately; the default protection is there for a reason.

## Reference

### File families

The family constants are tuples of common filename extensions, grouped by category. The examples in the table describe their contents; entries followed by “etc.” are representative rather than exhaustive lists of tuple members.

| Category | Contains |
|---|---|
| `ARCHIVES` | 7z, zip, tar, gz, rar, etc. |
| `AUDIO` | mp3, wav, flac, ogg, etc. |
| `CODE_ASSEMBLY` | asm, s, nasm, etc. |
| `CODE_COMPILED` | c, cpp, java, rs, go, etc. |
| `CODE_INTERPRETED` | py, js, php, rb, ts, etc. |
| `DATA` | json, csv, xml, yaml, sql, etc. |
| `DOCUMENTS` | pdf, docx, txt, md, epub, etc. |
| `EXECUTABLES` | exe, sh, bat, apk, bin, etc. |
| `FONTS` | ttf, otf, woff, etc. |
| `IMAGES` | png, jpg, jpeg, svg, gif, etc. |
| `PRESENTATIONS` | pptx, key, odp, etc. |
| `SPREADSHEETS` | xlsx, csv, ods, etc. |
| `SYSTEM` | dll, sys, log, ini, etc. |
| `VIDEOS` | mp4, mkv, avi, mov, etc. |
| `WEB` | html, css, jsx, wasm, etc. |

For example:

```python
from filorithm.families import IMAGES

print("png" in IMAGES)
```

The membership check shows the documented extension form: `"png"` appears without a leading dot. These collections let you reuse a family instead of remembering every spelling variation of a JPEG extension.

### Collections and filter methods

| Interface | Purpose |
| --- | --- |
| `Files(path)` | Collect files from the source directory. |
| `Files(path, raw=[...])` | Construct a file collection using supplied raw paths. |
| `Folders(path)` | Collect directories from the source directory. |
| `.filter()` | Start a `FilterFiles` or `FilterFolders` builder. |
| `.collect()` | Finish the builder and return a new collection containing the results. |
| `.with_extensions(extensions)` | Keep files whose extensions belong to the supplied collection. |
| `.without_extensions(extensions)` | Exclude files whose extensions belong to the supplied collection. |
| `.has_prefix(text)` | Filter names by prefix. |
| `.name_contains(text)` | Filter names by included text. |
| `.keep_only(names)` | Restrict the selection to the supplied names. |
| `.modified_after(date)` | Filter by modification time after a `datetime` cutoff. |
| `.modified_before(date)` | Filter by modification time before a `datetime` cutoff. |
| `.bigger_than(amount, unit)` | Filter files by size on disk. |
| `.largest(count)` | Keep the requested number of largest files. |

Additional supported filter categories include suffix matching, regex matching, and selecting the smallest files.

### Standalone storage functions

If you prefer calling functions directly, import the storage utilities:

```python
from filorithm.storage import (
    to_bytes,
    remove,
    copy_items,
    move_items,
    delete_items,
)
```

`to_bytes()` converts a readable amount and unit into bytes:

```python
bytes = to_bytes(5, "gb")
```

For manual batch work, supply a list or tuple of `pathlib.Path` objects. First import `Path`:

```python
from pathlib import Path
```

Then call the batch functions as needed:

```python
paths = [Path("file1.txt"), Path("file2.txt")]

copy_items(paths, "/destination")
move_items(paths, "/destination")
delete_items(paths)
```

The snippet shows the call shapes for `copy_items()`, `move_items()`, and `delete_items()`. Choose the operation you need; running all three sequentially against the same paths changes which source paths still exist.

These functions supply the storage mechanics used by `Files` and `Folders`. The module also exposes `remove`, as shown in the import list above.

## Examples

### Select large videos and old images

> [!CAUTION]
> This example performs real changes: it enables overwriting, moves selected videos, and permanently deletes selected images. Read through the filters and replace the paths before running it.

```python
from datetime import datetime
from filorithm.files import Files
from filorithm.families import VIDEOS, IMAGES

# Define a cutoff date
cutoff = datetime(2026, 1, 1)

# Collect all files in the downloads folder
downloads = Files("/users/home/downloads", overwrite=True)

# Find large videos
large_videos = (
    downloads.filter()
    .with_extensions(VIDEOS)
    .bigger_than(1, "gb")
    .collect()
)

# Find old images
old_images = (
    downloads.filter()
    .with_extensions(IMAGES)
    .modified_before(cutoff)
    .collect()
)

# Move the videos to an external drive
large_videos >> "/media/external/movies"

# Delete the old images
~old_images
```

The workflow has three steps:

1. Target the downloads directory with `Files`.
2. Build separate selections: videos bigger than 1 GB, and images modified before January 1, 2026.
3. Move the video selection to an external drive and delete the old-image selection.

The two collections let you express different criteria and actions from the same starting directory without writing the traversal and batch loops yourself.

## Good to know

Filorithm stays close to Python's standard filesystem utilities. The current implementation does not provide:

- Asynchronous file operations.
- A toggle for automatic symlink resolution.
- Deep recursive filtering through the filter interface, equivalent to an `os.walk()` traversal.
- File-content inspection.
- Advanced permission management through `chmod` or `chown`.
- Archiving or unzipping directly from `Files`.

> [!NOTE]
> Both `Files` and `Folders` implement `__str__()` and `__repr__()` to provide readable collection output.

Use `print()` to display the collection's string representation:

```python
files = Files("/path/to/files")
folders = Folders("/path/to/folders")

print(files)
print(folders)
```

`__str__()` returns the string representation of the underlying list of `Path` objects. The output includes their paths.

Use `repr()` to display a shorter summary of the collection:

```python
print(repr(files))
print(repr(folders))
```

`__repr__()` displays the collection's class name, total item count, and item names. It shows up to five names; when the collection contains more than five items, the remaining count is shown instead.

For example, on a POSIX system:

```text
[PosixPath('/path/to/files/report.txt'), PosixPath('/path/to/files/data.csv')]
<Files count=2 items=['report.txt', 'data.csv']>

[PosixPath('/path/to/folders/archive'), PosixPath('/path/to/folders/images')]
<Folders count=2 items=['archive', 'images']>
```

The path representation may differ between operating systems. The collection summary, however, keeps the same format.

## Design notes

Filorithm puts a readable interface over the standard `os`, `shutil`, and `pathlib` operations. The work is split into three explicit stages:

1. **Select a source:** `Files` or `Folders` collects the items.
2. **Build conditions:** `FilterFiles` or `FilterFolders` narrows the collection.
3. **Execute an action:** storage operators or standalone functions perform the operation.

The overloaded operators make batch actions concise and visually distinct from normal method calls. The underlying filesystem and storage behavior remain ordinary Python operations; Filorithm handles the orchestration. If you have been repeating `shutil.move()` or `os.remove(os.path.join(root, file))` inside traversal loops, this gives that work a common interface. Fewer nested loops, same files, slightly more afternoon left.
