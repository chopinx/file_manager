# File Manager

Simple Python utilities for indexing files and removing duplicates.

## Features
- Compute MD5 checksums for files and directories
- Export directory listings to CSV files
- Detect and remove duplicate files
- Remove empty directories

## Installation
Clone this repository and ensure Python 3.6+ is available.

```bash
git clone https://github.com/yourname/file_manager.git
```

## Usage
Run the helper functions from `file_manager.utils`.

Example: scan a path and generate `dirs.csv` and `files.csv`:

```bash
python -c "from file_manager import utils; utils.scan_path_to_csv('/path/to/scan')"
```

Remove files in new locations that already exist under a base path:

```bash
python -c "from file_manager import utils; utils.remove_dup_2('E:/base', ['F:/videos', 'F:/backup'])"
```

## Contributing
Contributions are welcome. Feel free to submit pull requests or open issues.

## License
Apache-2.0. See [LICENSE](LICENSE) for details.
