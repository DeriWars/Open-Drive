

def get_directory_content(directory_path: str) -> tuple:
    """
    Returns a list of all files and subdirectories in the given directory.
    
    Params:
        directory_path: The path to the directory to be scanned.
    
    Returns:
        tuple: A list of all subdirectories and files in the given directory.
    """
    
    from os import listdir
    from os.path import isdir, isfile, join
    
    directory_content = listdir(directory_path)
    directories = []
    files = []
    
    for content in directory_content:
        if isdir(join(directory_path, content)):
            directories.append(content)
        elif isfile(join(directory_path, content)):
            files.append(content)

    return directories, files
