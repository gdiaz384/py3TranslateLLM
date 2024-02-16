##  Guide: Installing and managing Python library versions with `pip`:

[pip](//pypi.org/project/pip) is the package installer for Python. pip can be used to install packages from the Python Package Index, [PyPi.org](//pypi.org), and other indexes. Starting with Python 3.4, pip comes bundled with Python.

Official docs:
- https://pip.pypa.io/en/stable/installation
- https://pip.pypa.io/en/stable

### Make sure Python and pip are installed

- `python --version` #Find out what major Python version is installed. 3.5, 3.6, 3.7, etc 
    - Linux users may have to use `python3 --version`.
- Find out where `python.exe` is located.
    - `where python` #Windows.
    - `which python` #Linux.
        - If `python` is a symlink, as is the norm on Linux, then follow it to the target:
        - `ls -la /usr/bin/python` #Use the path specified in the previous command.
- `pip --version`
    - Linux users may have to use `pip3 --version`.
- Find out where pip is located.
    - `where pip` #Windows.
    - `which pip` #Linux.
    - `which pip3` #Linux.

### Update pip

- `pip --version`
- `python -m pip install --upgrade pip` 
- `pip --version`

### Install libraries

- `pip install -r requirements.txt` #Use this syntax to install a predefined list of libraries from a file. Alternatively:
- `pip install <libraryName>` #Example:
    - `pip install openpyxl`
    - `pip install fairseq`
    - `pip install tornado`

### Managing library versions

- `pip list`  #Show all available libraries, their versions, and any non-standard locations.
- `pip index versions <libraryName>`  #Use this syntax to list available versions for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions openpyxl`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install openpyxl==3.1.2`
    - `pip uninstall torch torchvision torchaudio`

### Update every Python library

- `pip freeze > knownWorking.txt`
- `python -m pip install --upgrade -r knownWorking.txt`
    - This will probably break everything because software tends to require specific versions of libraries.
    - Updating stuff just to update it is never a good idea. At least make sure everything is compatible first.
- If the above command left the system still operational, then enter the following for maxium breakage:
    - `python -m pip install --upgrade --no-deps --force-reinstall -r knownWorking.txt`

### Uninstall every Python library

- `pip freeze > knownWorking.txt`
- `python -m pip uninstall -y -r knownWorking.txt`
    - Omit the -y to require confirmation before completely clobbering the local Python environment.

### Install specific versions of specific Python libraries

- `pip install -r knownWorking.txt`
- `pip install -r requirements.txt`
- `pip install -r optional.txt`

### Dealing with portable versions of Python 3

- Invoking a particular python.exe will load the environment for that Python binary.
    - Example: `Python310\python.exe Python310\Scripts\pip.exe install tornado`
- The above command would invoke the local environment under Python310 and pip would install `tornado` to `Python310\Lib\site-packages`.

### Dealing with venv in Python 3

- TODO: Put stuff here.

### pip, self-updates, and Python modules

- `pip` can be invoked both as both a python module by using `python -m pip` and externally as `pip.exe` or `pip3.exe`. Examples:
    - `pip.exe install  sentencepiece`
    - `pip3.exe install  sentencepiece`
    - `python.exe pip.exe install  sentencepiece`
    - `python.exe pip3.exe install  sentencepiece`
    - `python.exe -m pip install  sentencepiece`
- The file system version, `pip.exe`, cannot cannot be used to update itself since the file is locked while in use. The following will fail:
    - `python pip.exe install --upgrade pip`
- The alternative 'invoke as module' syntax is used instead.
- `python.exe -m` means 'start python and immediately invoke the following module'.
    - `python.exe -m pip` means 'start python and invoke the pip module'.
    - `python.exe -m PyInstaller` means 'start python and invoke the PyInstaller module'.
- The command to update pip starts with `python -m pip` which invokes pip as a python module in order to update the `pip.exe` executable file on the file system. 
- In other words, `pip.exe` is not actually needed to manage Python library versions because the module version is always available as `python -m pip`.
- This can simplify commands like the above example: 
    - From: `Python310\python.exe Python310\Scripts\pip.exe install tornado`
    - To: `Python310\python.exe -m pip install tornado`
- Sometimes, the pip developers threaten to clobber half of all Python installations worldwide, see #[12063](//github.com/pypa/pip/issues/12063). When that occasionally happens, try updating pip to a known working version by mixing in the library managing syntax.
    - `python -m pip install --upgrade pip==24.0`

## Additional resources

- Python's [official documentation](//docs.python.org/3/installing/index.html)
- `pip install --help`      #For additional confusion.
