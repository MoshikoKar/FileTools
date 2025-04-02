import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---- Folder Structure Scanner Functions ----
def scan_folder_structure(folder_path):
    """
    Scan the folder and return a list of lines representing the folder structure.
    Excludes specified folders and file types.
    """
    # Excluded folder names and file extensions
    excluded_folders = {"node_modules", "__pycache__", "venv", ".venv", "build", "uploads", ".git", "builds", "logs", "data", "instance"}
    excluded_extensions = {".db", ".ico", ".log", ".pem", ".key", ".png", ".jpg", ".crt", ".cer", ".exe", ".toc", ".pyz", ".spec", ".pkg", ".pyc", ".zip", ".cer"}
    
    structure_lines = [f"{os.path.basename(folder_path)}/"]
    
    def build_structure(root_dir, indent=""):
        nonlocal structure_lines
        # Get directories and files, excluding specified ones
        try:
            entries = os.listdir(root_dir)
        except PermissionError:
            return  # Skip directories we can't access
        
        dirs = []
        files = []
        for entry in entries:
            full_path = os.path.join(root_dir, entry)
            if os.path.isdir(full_path):
                if entry not in excluded_folders:
                    dirs.append(entry)
            elif os.path.isfile(full_path) and not any(entry.endswith(ext) for ext in excluded_extensions):
                files.append(entry)
        
        # Sort for consistent output
        dirs.sort()
        files.sort()
        
        # Process directories and files
        for i, dir_name in enumerate(dirs):
            is_last = (i == len(dirs) - 1 and not files)
            prefix = "└──" if is_last else "├──"
            structure_lines.append(f"{indent}{prefix} {dir_name}/")
            build_structure(os.path.join(root_dir, dir_name), indent + ("    " if is_last else "│   "))
        
        for i, file_name in enumerate(files):
            is_last = (i == len(files) - 1)
            prefix = "└──" if is_last else "├──"
            structure_lines.append(f"{indent}{prefix} {file_name}")
    
    # Start building from the root
    build_structure(folder_path, "│   ")
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
    """Copy files from source to destination folder"""
    source = source_var.get()
    dest = dest_var.get()
    
    # Validate input
    if not source:
        messagebox.showerror("Error", "Please select a source folder.")
        return
    if not dest:
        messagebox.showerror("Error", "Please select a destination folder for copying files.")
        return
    
    try:
        status_var.set("Copying files...")
        main_frame.update()
        
        for root_dir, dirs, files in os.walk(source):
            # Exclude directories and their contents
            dirs[:] = [d for d in dirs if d not in ["node_modules", "__pycache__", "venv", ".venv", "build", "uploads", ".git", "builds", "logs", "data", "instance"]]
            for file in files:
                if (os.path.basename(file) != "package-lock.json" and 
                    os.path.splitext(file)[1] not in [".db", ".ico"]):
                    full_path = os.path.join(root_dir, file)
                    if os.path.getsize(full_path) > 0:
                        if path_name_var.get():
                            relative_path = os.path.relpath(full_path, source)
                            new_name = relative_path.replace(os.sep, "_")
                        else:
                            new_name = os.path.basename(file)
                        dest_path = os.path.join(dest, new_name)
                        unique_dest_path = get_unique_dest_path(dest_path)
                        shutil.copy(full_path, unique_dest_path)
        
        status_var.set("Files copied successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_var.set(f"Error occurred: {str(e)}")

def run_check():
    """Check for empty files in the specified folder"""
    source = source_var.get()
    
    # Validate input
    if not source:
        messagebox.showerror("Error", "Please select a source folder to check for empty files.")
        return
    
    try:
        status_var.set("Scanning for empty files...")
        main_frame.update()
        
        empty_files = set()
        excluded_folders = {"node_modules", "__pycache__", "venv", ".venv", "build", "uploads", ".git", "builds", "logs", "data", "instance"}
        excluded_extensions = {".db", ".ico", ".log", ".pem", ".key", ".png", ".jpg", ".crt", ".cer", ".exe", ".toc", ".pyz", ".spec", ".pkg", ".pyc", ".zip", ".cer"}
        
        for root, dirs, files in os.walk(source, topdown=True):
            dirs[:] = [d for d in dirs if d not in excluded_folders]
            for file in files:
                if any(file.endswith(ext) for ext in excluded_extensions):
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), source)
                rel_path = rel_path.replace('\\', '/')
                full_path = os.path.join(root, file)
                if os.path.getsize(full_path) == 0:
                    empty_files.add(rel_path)
        
        # Determine output location
        output_dir = dest_var.get() if dest_var.get() else os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(output_dir, 'empty_files_log.txt')
        
        with open(log_path, 'w') as f:
            f.write("Empty files:\n")
            if empty_files:
                for file in sorted(empty_files):
                    f.write(f"  {file}\n")
            else:
                f.write("  No empty files found.\n")
        
        status_var.set(f"Log file generated: {log_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while scanning: {str(e)}")
        status_var.set(f"Error occurred: {str(e)}")

def run_scan():
    """Scan the selected folder and generate a structure file."""
    source = source_var.get()
    
    # Validate input
    if not source:
        messagebox.showerror("Error", "Please select a source folder to scan for structure.")
        return
    
    try:
        status_var.set("Generating folder structure...")
        main_frame.update()
        
        # Get the folder structure
        structure_lines = scan_folder_structure(source)
        
        # Determine output location
        output_dir = dest_var.get() if dest_var.get() else os.path.dirname(os.path.abspath(__file__))
        structure_path = os.path.join(output_dir, 'folder_structure.txt')
        
        # Write to output file
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(structure_lines))
        
        status_var.set(f"Folder structure generated: {structure_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while scanning: {str(e)}")
        status_var.set(f"Error occurred: {str(e)}")

# ---- Main GUI Setup ----
if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Tools")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Variables
    source_var = tk.StringVar()
    dest_var = tk.StringVar()
    status_var = tk.StringVar()
    path_name_var = tk.BooleanVar(value=True)  # Default to using path name
    
    # Source folder selection
    ttk.Label(main_frame, text="Source Folder:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
    ttk.Entry(main_frame, textvariable=source_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(main_frame, text="Browse", command=browse_source_folder).grid(row=0, column=2, padx=5, pady=5)
    
    # Destination folder selection
    ttk.Label(main_frame, text="Destination Folder:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
    ttk.Entry(main_frame, textvariable=dest_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(main_frame, text="Browse", command=browse_dest_folder).grid(row=1, column=2, padx=5, pady=5)
    
    # Note about destination folder
    ttk.Label(main_frame, text="* Required for Copy Files. Optional for other operations to specify output location.").grid(
        row=2, column=1, sticky=tk.W, padx=5, pady=(0, 10))
    
    # Path name checkbox (only for file copy)
    path_name_frame = ttk.Frame(main_frame)
    path_name_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(0, 10))
    
    ttk.Checkbutton(path_name_frame, text="Use full path in filename", variable=path_name_var).pack(side=tk.LEFT)
    ttk.Label(path_name_frame, text="(applies to Copy Files only)").pack(side=tk.LEFT, padx=(5, 0))
    
    # Create a frame for the action buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=3, pady=10)
    
    # Add action buttons
    ttk.Button(button_frame, text="Copy Files", command=copy_files, width=20).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Check Empty Files", command=run_check, width=20).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Generate Folder Structure", command=run_scan, width=25).pack(side=tk.LEFT, padx=5)
    
    # Status label
    ttk.Label(main_frame, textvariable=status_var, wraplength=500).grid(row=5, column=0, columnspan=3, pady=10)
    
    # Make window resizable
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Start the GUI event loop
    root.mainloop()