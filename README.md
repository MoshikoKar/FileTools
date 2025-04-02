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

### Folders:
- node_modules
- __pycache__
- venv, .venv
- build, builds
- uploads
- .git
- logs
- data
- instance

### File Extensions:
- .db
- .ico, .png, .jpg (image files)
- .log
- .pem, .key, .crt, .cer (certificate files)
- .exe, .toc, .pyz, .spec, .pkg (executable/package files)
- .pyc, .zip (compiled/compressed files)

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

### Empty Files Log Example:
```
Empty files:
  src/placeholder.txt
  tests/fixtures/empty_test.json
  docs/coming_soon.md
```

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
