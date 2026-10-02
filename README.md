# Filorithm

### A Python file utility with slightly fewer file-system-related inconveniences.

Welcome to **Filorithm**, a lightweight Python utility for working with files, directories, filtering, and batch storage operations.

Filorithm is built on top of Python's standard `pathlib` and `shutil` modules while providing a simpler and more expressive interface for common file system operations.

Filorithm provides several conveniences:

- **Predefined file type collections** for archives, audio, code, data, documents, executables, fonts, images, and videos.
- **Chainable filtering interfaces** for finding files and folders by name, size, extension, and modification date.
- **Readable size constructors** for kilobytes, megabytes, gigabytes, and terabytes.
- **Operator-overloaded batch operations** for copying, moving, and deleting items.
- **Automatic path resolution and directory sanitization.**
- **Unified handling** of single files, multiple files, and entire directories.
- **Direct integration** with standard Python `datetime` objects for time-based filtering.

Filorithm intentionally keeps its implementation small while making common file operations easier to express.

It is designed for programmers who want to manipulate files without repeatedly writing nested for-loops and calling `os.path.join()`.

Because apparently writing `os.remove(os.path.join(root, file))` inside a three-level `os.walk()` was considered a healthy way to spend an afternoon.

---

## 1. Installation

Filorithm uses Python's standard library and does not require external dependencies.

Import the required functions and classes from the Filorithm modules.

```python
from filorithm.files import Files
from filorithm.folders import Folders
from filorithm.file_types import IMAGES, VIDEOS
```

Replace `filorithm` with the module path used by your installation.

Filorithm is designed to work seamlessly with standard Python `Path` and `datetime` objects.

---

## 2. File Types

Filorithm provides predefined tuples of common file extensions grouped by category.

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

### Example

```python
from filorithm.file_types import IMAGES

print("png" in IMAGES)
```

These collections are incredibly useful when filtering directories for specific types of content without having to remember every variation of a JPEG extension.

---

## 3. The Files Class

The `Files` class provides the primary interface for collecting and manipulating files.

Instantiating the class reads the files in the specified directory.

```python
source_files = Files("/path/to/directory")
```

You can also pass raw paths directly:

```python
source_files = Files(
    "/path/to/directory",
    raw=["file1.txt", "file2.txt"]
)
```

Files behaves like an iterable collection, allowing you to access items by index or iterate over them directly.

```python
for file in source_files:
    print(file.name)
```

---

## 4. Filtering Files

The true power of the `Files` class comes from its `filter()` method, which returns a `FilterFiles` builder.

The builder provides chainable methods for narrowing down your file selection.

### 4.1 Extension Filtering

You can filter files by checking their extensions against a list or predefined tuple.

```python
images = Files("/downloads").filter().with_extensions(IMAGES).collect()
```

Or explicitly exclude them:

```python
safe_files = Files("/downloads").filter().without_extensions(EXECUTABLES).collect()
```

### 4.2 Name Filtering

Files can be filtered by prefix, suffix, regex, or simple text matching.

```python
reports = Files("/docs").filter().has_prefix("report_").collect()

old_files = Files("/docs").filter().name_contains("backup").collect()

specific = Files("/docs").filter().keep_only(["config.json"]).collect()
```

### 4.3 Date Filtering

File filtering integrates directly with Python's `datetime`.

```python
from datetime import datetime

cutoff = datetime(2026, 1, 1)

recent = Files("/docs").filter().modified_after(cutoff).collect()
```

### 4.4 Size Filtering

Filorithm supports filtering files based on their size on disk.

```python
from filorithm.storage import Unit

large = Files("/media").filter().bigger_than(500, "mb").collect()
```

You can also select the absolute largest or smallest files:

```python
top_ten = Files("/media").filter().largest(10).collect()
```

Remember to always call `collect()` at the end of a filter chain to return a new `Files` object containing the results.

---

## 5. The Folders Class

The `Folders` class works identically to `Files`, but it targets directories instead.

```python
folders = Folders("/var/log")
```

Folders also provides a `filter()` builder.

```python
backups = Folders("/var/log").filter().name_contains("backup").collect()
```

You can filter folders by prefix, suffix, name content, regex, and modification date.

---

## 6. Storage Operations

Filorithm overloads standard Python operators to provide an intuitive interface for copying, moving, and deleting items.

These operations apply to both `Files` and `Folders`.

### 6.1 Moving Items (`>>` operator)

The right-shift operator moves files or folders to a destination directory.

```python
images = Files("/downloads").filter().with_extensions(IMAGES).collect()

images >> "/pictures/memes"
```

This moves all filtered images to the memes directory.

### 6.2 Copying Items (`@` operator)

The matrix-multiplication operator copies files or folders to a destination directory.

```python
documents = Files("/work")

documents @ "/backup/work"
```

This copies everything. No matrix algebra required.

### 6.3 Deleting Items (`~` operator)

The bitwise-invert operator deletes the collected files or folders.

```python
temp_files = Files("/tmp").filter().name_contains("cache").collect()

~temp_files
```

This permanently removes the files from the disk. Use with caution.

### 6.4 Overwrite Protection

By default, storage operations will raise a `FileExistsError` if the destination file already exists.

You can override this by explicitly enabling overwrite when instantiating the class.

```python
Files("/downloads", overwrite=True) >> "/pictures"
```

Files are innocent. Only overwrite them if you mean it.

---

## 7. Standalone Storage Functions

If you prefer not to use the class abstractions, Filorithm provides raw utility functions in the storage module.

```python
from filorithm.storage import (
    to_bytes,
    remove,
    copy_items,
    move_items,
    delete_items,
)
```

### Size Conversion

```python
bytes = to_bytes(5, "gb")
```

### Manual Batch Operations

These functions take a list or tuple of `pathlib.Path` objects.

```python
paths = [Path("file1.txt"), Path("file2.txt")]

copy_items(paths, "/destination")
move_items(paths, "/destination")
delete_items(paths)
```

These are the underlying mechanics that the `Files` and `Folders` classes call automatically.

---

## 8. Complete Example

The following example demonstrates filtering files by size, date, and extension, followed by batch operations.

```python
from datetime import datetime
from filorithm.files import Files
from filorithm.file_types import VIDEOS, IMAGES

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

The script demonstrates the basic Filorithm workflow:

1. Target a directory.
2. Filter the contents based on criteria.
3. Apply a batch file-system operation.

---

## 9. Design Philosophy

Filorithm is designed to provide a readable Python interface over standard `os`, `shutil`, and `pathlib` operations.

The library deliberately embraces operator overloading (`>>`, `@`, `~`) to make batch operations concise and visually distinct from standard method calls.

The architecture separates responsibilities into logical steps:

1. **Target acquisition:** `Files` or `Folders`.
2. **Condition building:** `FilterFiles` or `FilterFolders`.
3. **Action execution:** Overloaded operators or storage functions.

Filorithm does not attempt to replace the file system or implement its own storage engine.

It simply makes the existing file-system operations less tedious to orchestrate.

Because apparently `shutil.move()` needed a map, a compass, and three nested loops to find its destination.

---

## 10. Limitations

Filorithm intentionally remains a lightweight wrapper around Python's standard file utilities.

The current implementation does not provide:

- Asynchronous file operations.
- Automatic symlink resolution toggling.
- Deep recursive filtering (`os.walk` equivalent through the filter interface).
- File content inspection.
- Advanced permission (`chmod`/`chown`) management.
- File archiving or unzipping directly from the `Files` class.

The current `__str__()` and `__repr__()` methods are placeholders and return:

```text
not implemented
```

and:

```text
<not implemented>
```

respectively.

These are implementation placeholders rather than formatted representations of the collections.

---

## 11. Final Example

A compact Filorithm program can therefore look like this:

```python
from filorithm.files import Files
from filorithm.file_types import CODE_INTERPRETED

scripts = Files("/scripts").filter().with_extensions(CODE_INTERPRETED).collect()

scripts @ "/backup/scripts"
```

A small interface for doing the things file systems have spent decades making unnecessarily verbose.
