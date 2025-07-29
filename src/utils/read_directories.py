from os import *

def read_filenames_in_directory(directory: str) -> list:
    """
    Read all files in a directory and return a list of file paths.
    
    Args:
        directory (str): The path to the directory to read.
        
    Returns:
        list: A list of file paths in the directory.
    """
    if not path.isdir(directory):
        raise ValueError(f"The provided path '{directory}' is not a valid directory.")
    
    files = [path.join(directory, f) for f in listdir(directory) if path.isfile(path.join(directory, f))]
    return files

def read_directories_in_directory(directory: str) -> list:
    """
    Read all directories in a directory and return a list of directory paths.
    
    Args:
        directory (str): The path to the directory to read.
        
    Returns:
        list: A list of directory paths in the directory.
    """
    if not path.isdir(directory):
        raise ValueError(f"The provided path '{directory}' is not a valid directory.")
    
    directories = [path.join(directory, d) for d in listdir(directory) if path.isdir(path.join(directory, d))]
    return directories

if __name__ == "__main__":
    # Example usage
    directory_path = r"./data"
    dirs = read_directories_in_directory(directory_path)
    print("Directories in directory:", dirs)
    files = [read_filenames_in_directory(d) for d in dirs]
    print("Files in directory:", files)