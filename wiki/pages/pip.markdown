##  Guide: Installing and managing Python library versions with `pip`:

### Make sure Python is installed

- `python --version` #Find out what major Python version is installed. 3.5, 3.6, 3.7, etc and where it is located.
    - `where python` #Windows.
    - `which python` #Linux.
        - If `python` is a symlink, as is the norm, then follow it to the target:
        - `ls -la /usr/bin/python` #Use the path specified in the previous command.

### Update pip

- `pip --version`
- `python -m pip install --upgrade pip` 
- `pip --version`

### Managing library versions

- `pip install -r requirements.txt` #Use this syntax to install a predefined list of libraries from a file. Alternatively:
- `pip install <libraryName>` #Examples:
    - `pip install openpyxl`
- `pip index versions <libraryName>`  #Use this syntax to list available versions for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions openpyxl`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install openpyxl==3.1.2`
    - `pip uninstall torch torchvision torchaudio`

## Additional resources

- Python's [official documentation](//docs.python.org/3/installing/index.html)
- `pip install --help`      #For additional confusion.
