import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---- Centralized Exclusion Lists ----
# Folders commonly excluded from scans, copies, etc.
EXCLUDED_FOLDERS = {
    # Version Control
    ".git", ".svn", ".hg",
    # Python specific
    "__pycache__", "venv", ".venv", "*.egg-info", ".pytest_cache", ".mypy_cache", ".tox", "site-packages",
    # Node.js specific
    "node_modules",
    # Build artifacts / Distributables
    "build", "dist", "target", "bin", "obj", "out", "builds",
    # IDE / Editor specific
    ".vscode", ".idea", ".project", ".settings",
    # OS specific / Temporary
    ".DS_Store", # Technically a file, but often acts like a folder artifact
    ".cache",
    # Common project structures
    "uploads", "logs", "data", "instance", "temp", "tmp",
    # Specific frameworks/tools
    "coverage", # Coverage reports
    "static", # Often contains collected static files, duplicates
    "media",  # Often contains user-uploaded large files
}

# File extensions commonly excluded (binaries, data, logs, configs, media, archives)
# Use lowercase for case-insensitive matching
EXCLUDED_EXTENSIONS = {
    # Databases
    ".db", ".sqlite", ".sqlite3", ".mdb",
    # Logs
    ".log",
    # Security / Keys
    ".pem", ".key", ".crt", ".cer", ".p12", ".pfx",
    # Images
    ".ico", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg",
    # Executables / Compiled / Packages
    ".exe", ".dll", ".so", ".o", ".a", ".lib",
    ".pyc", ".pyo", ".pyd",
    ".class", ".jar",
    ".toc", ".pyz", ".spec", ".pkg",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    # Documents / Media (often large or irrelevant for code scanning)
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flv", ".wmv",
    # Font files
    ".ttf", ".otf", ".woff", ".woff2",
    # Other
    ".bak", ".swp", ".swo", # Backup/swap files
}

# Specific filenames to always exclude
EXCLUDED_FILES = {
    # OS specific
    ".DS_Store", "Thumbs.db",
    # Package manager lock files (often large/binary or change frequently)
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
    # Environment files (might contain secrets)
    ".env"
}

# ---- Folder Structure Scanner Functions ----
def scan_folder_structure(folder_path):
    """
    Scan the folder and return a list of lines representing the folder structure.
    Excludes specified folders, file types, and specific files.
    Uses a purely recursive approach.
    """
    structure_lines = [f"{os.path.basename(folder_path)}/"]

    def build_recursive(current_path, indent=""):
        """Recursively builds the structure lines."""
        nonlocal structure_lines
        try:
            # List entries, handling potential permission errors
            entries = sorted(os.listdir(current_path))
        except PermissionError:
            # Add a note if a directory can't be accessed
            structure_lines.append(f"{indent}└── [Permission Denied]")
            return # Stop recursion for this path

        filtered_entries = []
        # Filter entries based on exclusion lists
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                # Keep directory if not excluded
                if entry not in EXCLUDED_FOLDERS:
                    filtered_entries.append({"name": entry, "type": "dir", "path": full_path})
            elif os.path.isfile(full_path):
                # Keep file if not excluded by name or extension
                if entry not in EXCLUDED_FILES and \
                   os.path.splitext(entry)[1].lower() not in EXCLUDED_EXTENSIONS:
                    filtered_entries.append({"name": entry, "type": "file", "path": full_path})

        # Process the filtered entries
        for i, item in enumerate(filtered_entries):
            is_last = (i == len(filtered_entries) - 1)
            prefix = "└──" if is_last else "├──"
            # The indent for children depends on whether the current item is the last one
            child_indent = indent + ("    " if is_last else "│   ")

            if item["type"] == "dir":
                structure_lines.append(f"{indent}{prefix} {item['name']}/")
                # Recurse into the subdirectory with the calculated child indent
                build_recursive(item['path'], child_indent)
            else: # type == "file"
                structure_lines.append(f"{indent}{prefix} {item['name']}")

    # --- Main execution ---
    # Start the recursion from the root folder_path.
    # The initial indent passed to the recursive function should be empty "",
    # because the prefixes (├──, └──) are added relative to the current level's indent.
    build_recursive(folder_path, "")

    return structure_lines


# ---- General Utility Functions ----
def browse_source_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        source_var.set(folder_selected)

def browse_dest_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        dest_var.set(folder_selected)

def get_unique_dest_path(dest_path):
    if not os.path.exists(dest_path):
        return dest_path
    base, ext = os.path.splitext(dest_path)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

# ---- Action Functions ----
def copy_files():
    """Copy files from source to destination folder, respecting exclusions."""
    source = source_var.get()
    dest = dest_var.get()

    if not source or not os.path.isdir(source):
        messagebox.showerror("Error", "Please select a valid source folder.")
        return
    if not dest:
        messagebox.showerror("Error", "Please select a destination folder for copying files.")
        return
    if not os.path.exists(dest):
        try:
            os.makedirs(dest)
        except OSError as e:
             messagebox.showerror("Error", f"Could not create destination folder: {e}")
             return
    if not os.path.isdir(dest):
        messagebox.showerror("Error", "Destination path exists but is not a folder.")
        return


    try:
        status_var.set("Copying files...")
        main_frame.update()
        copied_count = 0

        for root_dir, dirs, files in os.walk(source, topdown=True):
            # Prune traversal by removing excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]

            for file in files:
                # Check excluded files and extensions
                if file in EXCLUDED_FILES or os.path.splitext(file)[1].lower() in EXCLUDED_EXTENSIONS:
                    continue

                full_path = os.path.join(root_dir, file)

                # Skip empty files if desired (optional, currently copying non-empty)
                try:
                     if os.path.getsize(full_path) == 0:
                         continue # Skip empty files
                except OSError:
                    continue # Skip files we can't access size for

                # Determine destination name and path
                if path_name_var.get():
                    relative_path = os.path.relpath(full_path, source)
                    # Sanitize relative path for use as filename
                    new_name = relative_path.replace(os.sep, "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
                else:
                    new_name = file

                dest_path = os.path.join(dest, new_name)
                unique_dest_path = get_unique_dest_path(dest_path)

                # Perform the copy
                try:
                    shutil.copy2(full_path, unique_dest_path) # copy2 preserves metadata
                    copied_count += 1
                except Exception as copy_e:
                    print(f"Warning: Could not copy file {full_path}: {copy_e}") # Log to console maybe?


        status_var.set(f"Files copied successfully! ({copied_count} files)")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during copy: {str(e)}")
        status_var.set(f"Error occurred: {str(e)}")

def run_check():
    """Check for empty files in the specified folder, respecting exclusions."""
    source = source_var.get()

    if not source or not os.path.isdir(source):
        messagebox.showerror("Error", "Please select a valid source folder to check.")
        return

    try:
        status_var.set("Scanning for empty files...")
        main_frame.update()

        empty_files = set()

        for root_dir, dirs, files in os.walk(source, topdown=True):
            # Prune traversal
            dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]

            for file in files:
                # Check exclusions
                if file in EXCLUDED_FILES or os.path.splitext(file)[1].lower() in EXCLUDED_EXTENSIONS:
                    continue

                full_path = os.path.join(root_dir, file)
                try:
                    if os.path.getsize(full_path) == 0:
                        rel_path = os.path.relpath(full_path, source)
                        empty_files.add(rel_path.replace('\\', '/')) # Normalize path separators
                except OSError:
                    continue # Skip files we can't access

        # Determine output location
        output_dir = dest_var.get() if dest_var.get() and os.path.isdir(dest_var.get()) else os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(output_dir, 'empty_files_log.txt')

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Empty files found (excluding common build/binary/temporary files):\n")
            if empty_files:
                f.write("=" * 60 + "\n")
                for file in sorted(list(empty_files)):
                    f.write(f"  {file}\n")
                f.write("=" * 60 + "\n")
                f.write(f"\nTotal empty files found: {len(empty_files)}\n")
            else:
                f.write("\n  No empty files found matching the criteria.\n")

        status_var.set(f"Empty file check complete. Log saved to: {log_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while scanning for empty files: {str(e)}")
        status_var.set(f"Error occurred: {str(e)}")


def run_scan():
    """Scan the selected folder and generate a structure file, respecting exclusions."""
    source = source_var.get()

    if not source or not os.path.isdir(source):
        messagebox.showerror("Error", "Please select a valid source folder to scan.")
        return

    try:
        status_var.set("Generating folder structure...")
        main_frame.update()

        # Get the folder structure using the refined function
        structure_lines = scan_folder_structure(source)

        # Determine output location
        output_dir = dest_var.get() if dest_var.get() and os.path.isdir(dest_var.get()) else os.path.dirname(os.path.abspath(__file__))
        structure_path = os.path.join(output_dir, 'folder_structure.txt')

        # Write to output file
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(structure_lines))

        status_var.set(f"Folder structure generated: {structure_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating structure: {str(e)}")
        status_var.set(f"Error occurred: {str(e)}")

# ---- Main GUI Setup ----
if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Tools v1.1") # Added version

    # Create main frame
    main_frame = ttk.Frame(root, padding="10 10 10 10") # Adjusted padding
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)) # Use grid and sticky

    # Variables
    source_var = tk.StringVar()
    dest_var = tk.StringVar()
    status_var = tk.StringVar(value="Status: Idle") # Initial status
    path_name_var = tk.BooleanVar(value=True)  # Default to using path name

    # Configure grid weights for resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1) # Allow entry widget to expand

    # Source folder selection
    ttk.Label(main_frame, text="Source Folder:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
    source_entry = ttk.Entry(main_frame, textvariable=source_var, width=60) # Increased width
    source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
    ttk.Button(main_frame, text="Browse...", command=browse_source_folder).grid(row=0, column=2, padx=5, pady=5)

    # Destination folder selection
    ttk.Label(main_frame, text="Destination Folder:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
    dest_entry = ttk.Entry(main_frame, textvariable=dest_var, width=60) # Increased width
    dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
    ttk.Button(main_frame, text="Browse...", command=browse_dest_folder).grid(row=1, column=2, padx=5, pady=5)

    # Note about destination folder
    ttk.Label(main_frame, text="* Destination required for 'Copy Files'. Optional for others (defaults to script location).", font=('TkDefaultFont', 9)).grid(
        row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=(0, 10))

    # Path name checkbox (only for file copy)
    path_name_frame = ttk.Frame(main_frame)
    path_name_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(5, 10))

    ttk.Checkbutton(path_name_frame, text="Use full relative path in copied filename", variable=path_name_var).pack(side=tk.LEFT)
    ttk.Label(path_name_frame, text="(applies to 'Copy Files' only)", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(5, 0))

    # Create a frame for the action buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=3, pady=10)

    # Add action buttons - Use consistent width or packing
    copy_button = ttk.Button(button_frame, text="Copy Files", command=copy_files, width=22)
    copy_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    check_button = ttk.Button(button_frame, text="Check Empty Files", command=run_check, width=22)
    check_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    scan_button = ttk.Button(button_frame, text="Generate Folder Structure", command=run_scan, width=25)
    scan_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # Status label
    status_label = ttk.Label(main_frame, textvariable=status_var, wraplength=550, anchor=tk.W, justify=tk.LEFT) # Improved wrapping and alignment
    status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)

    # Add padding to all widgets in main_frame for better spacing
    for child in main_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    # Start the GUI event loop
    root.mainloop()