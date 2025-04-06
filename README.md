# File Tools

A simple yet powerful utility for file management, scanning, and structure visualization.

## Features

### 1. Copy Files
- Copy files from a source folder to a destination folder
- Option to use the full path in the filename to prevent naming conflicts
- Automatically skips common build folders and non-relevant files
- Handles duplicate filenames by creating numbered copies

### 2. Empty File Checker
- Scan a folder to find all empty files
- Excludes common system and build directories
- Generates a detailed log file of all empty files found
- Optional destination folder for the log output

### 3. Folder Structure Generator
- Create a visual text representation of your folder structure
- Shows the hierarchy with tree-like formatting
- Intelligently skips system folders, build directories, and binary files
- Optional destination folder for the output file

## Installation

1. Make sure you have Python 3.x installed
2. Download the `file_tools.py` file
3. No external dependencies required - uses only Python standard library

## Usage

Run the program:
```
python file_tools.py
```

### General Steps:
1. Select your source folder (required for all operations)
2. Select a destination folder (required for Copy Files, optional for others)
3. Select the appropriate action button:
   - **Copy Files**: Copies all files from source to destination
   - **Check Empty Files**: Generates a log of all empty files
   - **Generate Folder Structure**: Creates a text visualization of your folder structure

### Notes
- When the destination folder is not specified for checking empty files or generating structure, the output files will be saved in the same directory as the program.
- The "Use full path in filename" option only applies to the Copy Files operation.

## Excluded Items

The tool automatically skips the following items:

### Excluded Folders:
- .git, .svn, .hg (Version Control)
- __pycache__, venv, .venv, *.egg-info, .pytest_cache, .mypy_cache, .tox, site-packages (Python)
- node_modules (Node.js)
- build, dist, target, bin, obj, out, builds (Build Artifacts)
- .vscode, .idea, .project, .settings (IDE/Editor Config)
- .cache, temp, tmp (Cache/Temporary)
- uploads, logs, data, instance (Common App Folders)
- coverage (Test Coverage Reports)
- static, media (Collected static/media files)

### Excluded File Extensions (Case-Insensitive):
- .db, .sqlite, .sqlite3, .mdb (Databases)
- .log (Logs)
- .pem, .key, .crt, .cer, .p12, .pfx (Security/Keys)
- .ico, .png, .jpg, .jpeg, .gif, .bmp, .tiff, .svg (Images)
- .exe, .dll, .so, .o, .a, .lib, .pyc, .pyo, .pyd, .class, .jar, .toc, .pyz, .spec, .pkg (Executables/Compiled/Packages)
- .zip, .tar, .gz, .bz2, .7z, .rar (Archives)
- .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx (Documents)
- .mp3, .mp4, .avi, .mov, .wav, .flv, .wmv (Audio/Video)
- .ttf, .otf, .woff, .woff2 (Fonts)
- .bak, .swp, .swo (Backup/Swap Files)

### Excluded Specific Files:
- .DS_Store, Thumbs.db (OS-specific metadata)
- package-lock.json, yarn.lock, pnpm-lock.yaml, poetry.lock, Pipfile.lock (Package Manager Lock Files)
- .env (Environment Variables - potentially sensitive)

## Example Output

### Folder Structure Example:
```
ProjectFolder/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.js
│   │   │   └── Footer.js
│   │   └── pages/
│   │       ├── Home.js
│   │       └── About.js
│   ├── tests/
│   │   └── app.test.js
│   └── README.md
```


### Empty Files Log Example (empty_files_log.txt):
```
Empty files found (excluding common build/binary/temporary files):
============================================================
  src/utils/placeholder.js
  docs/upcoming_feature.md
  config/empty_settings.json
============================================================

Total empty files found: 3
```

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
