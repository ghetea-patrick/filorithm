# The Filorithm Developer Manual

# !!! WARNING !!!
Filorithm is currently mid-renovation. I am tearing down old method names, adding flexible single/multi-item parameter handling, and cleaning up internal logic.
If you see '...' placeholders or changing signatures, that's intentional.
## Please hold off on upgrading to this newer version until this notice is removed


Filorithm is an expressive Python embedded Domain Specific Language (eDSL) designed for high-level file and folder manipulation. By utilizing operator overloading and chainable filtering interfaces, Filorithm abstracts the verbose complexities of standard libraries like `os`, `shutil`, and `pathlib` into clean, intuitive pipeline operations.


## Abstract & Architecture

Filorithm operates on the concept of wrapping directory contents into managed collection objects (`Files` and `Folders`). Instead of executing procedural function calls, workflows are declared using fluent filter interfaces and completed using standard operators that mimic terminal actions. 

The framework is split into distinct components:
1. `storage.py`: The underlying engine handling safe path validation, file copy/move operations, and strict error handling.
2. `files.py` / `folders.py`: The user-facing API containing collection wrappers and the fluent filter classes (`FilterFiles`, `FilterFolders`).
3. `file_types.py`: Constant tuples grouping common extensions (e.g., CODE_INTERPRETED, DATA, IMAGES) for rapid batch processing.


## Syntax Rules & Operators

Filorithm overrides standard Python operators to execute file system tasks directly on collection objects or evaluated filters:

* `>>` (Right-shift): Moves items in the collection to a destination directory.
* `@` (Matmul): Copies items in the collection to a destination directory.
* `~` (Invert / Unary tilde): Deletes all items in the collection permanently.

### Pipeline Rules:
1. Instantiating `Files("dir")` or `Folders("dir")` gathers all immediate items inside that directory.
2. Invoking the `.filter()` method transitions the collection into an evaluation state.
3. Filtering methods can be chained infinitely (e.g., `.bigger_than().with_extensions()`).
4. The pipeline MUST be closed with `.collect()` before an operator (`>>`, `@`, `~`) can be applied to the filtered subset.
5. To directly inspect or iterate over the elements without executing a filesystem mutation (move, copy, or delete), access the raw contents via list iteration, index lookup, or by calling `.collect()`.


## API Reference & Filter Methods

### Collection Initializers
* `Files(directory: str | Path, *, overwrite: bool = False)`
* `Folders(directory: str | Path, *, overwrite: bool = False)`

If `overwrite=True`, any existing file or folder at the target destination with a conflicting name will be removed before the copy or move operation executes.

### Chainable Filter Pipeline
Calling `.filter()` exposes the following evaluation constraints:

* **Size Constraints:**
  * `.bigger_than(size: int, unit: SizeUnit)`
  * `.smaller_than(size: int, unit: SizeUnit)`
  * `.between_sizes(min_size: int, min_unit: SizeUnit, max_size: int, max_unit: SizeUnit)`
  * *Supported Units:* `"kb"`, `"mb"`, `"gb"`, `"tb"`

* **String Matching Constraints:**
  * `.name_startswith(prefix: str)`
  * `.name_endswith(suffix: str)`
  * `.name_contains(text: str)`
  * `.name_matches(regex: str | Pattern)`

* **Metadata & Quantity Constraints:**
  * `.modified_after(dt: datetime)`
  * `.modified_before(dt: datetime)`
  * `.largest(count: int)`
  * `.smallest(count: int)`
  * `.top(count: int)`
  * `.last(count: int)`

* **Extension Specifics (Files Only):**
  * `.with_extensions(extensions: Sequence[str])`
  * `.without_extensions(extensions: Sequence[str])`


## Examples

```
from datetime import datetime
from filorithm.files import Files
from filorithm.folders import Folders
from filorithm.file_types import CODE_INTERPRETED, IMAGES, DOCUMENTS

# ==============================================================================
# EXAMPLE 1: Basic File Migration
# ==============================================================================
# Instantly move all files out of a raw data staging folder directly into a 
# processing directory using the right-shift (>>) syntax wrapper.

Files("staging_area") >> "processing_vault"


# ==============================================================================
# EXAMPLE 2: Size Filtering and Copying Assets
# ==============================================================================
# Target a downloads folder, chain a filter to isolate only massive media files 
# exceeding 500 Megabytes, collect the result, and duplicate them using matmul (@).

Files("downloads").filter().bigger_than(500, "mb").collect() @ "external_media_drive"


# ==============================================================================
# EXAMPLE 3: Ecosystem-Driven Script and Document Sorting
# ==============================================================================
# Organize a cluttered workspace directory by routing interpreted scripts 
# (py, js, rb) to a dedicated scripts path, and documents (pdf, docx, txt) to docs.

# A. Pipeline for code scripts
Files("workspace").filter().with_extensions(CODE_INTERPRETED).collect() >> "development/scripts"

# B. Pipeline for documentation
Files("workspace").filter().with_extensions(DOCUMENTS).collect() >> "development/documentation"


# ==============================================================================
# EXAMPLE 4: In-Memory Inspection (Passive Elements Viewing)
# ==============================================================================
# Inspect metadata properties, parse index elements, or count specific assets 
# without mutating, moving, or modifying any actual items on the filesystem storage.
print("\nExecuting Example 4: Passive viewing and collection inspection...")

# Initialize target snapshot
asset_collection = Files("project_assets")

# A. String representation showing discovered files
print(f"Current collection array: {asset_collection}")

# B. Positional index access
if len(asset_collection) > 0:
    first_asset = asset_collection[0]
    print(f"Primary asset tracking path: {first_asset}")

# C. Native iteration loop
for file_item in asset_collection:
    print(f"Scanning asset metadata: {file_item.name} | Size: {file_item.stat().st_size} bytes")

# D. Compound filtered view count without execution
target_date = datetime(2026, 1, 1)
outdated_images = Files("gallery").filter().with_extensions(IMAGES).modified_before(target_date).collect()
print(f"Total legacy images matching parameters: {len(outdated_images)}")


# ==============================================================================
# EXAMPLE 5: Destructive Temporary Cache and Directory Purging
# ==============================================================================
# Safely wipe out local transient build artifact directories or old testing data 
# recursively using the unary invert (~) shortcut operator.

~Folders("local_test_environment/build_caches")
```
