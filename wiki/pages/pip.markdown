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

### Install libraries

- `pip install -r requirements.txt` #Use this syntax to install a predefined list of libraries from a file. Alternatively:
- `pip install <libraryName>` #Example:
    - `pip install openpyxl`
    - `pip install fairseq`
    - `pip install tornado`

### Managing library versions

- `pip index versions <libraryName>`  #Use this syntax to list available versions for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions openpyxl`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install openpyxl==3.1.2`
    - `pip uninstall torch torchvision torchaudio`

### Dealing with portable versions of Python 3

- Invoking a particular python.exe will load the environment for that Python binary.
- Examples: `Python310\python.exe Python310\Scripts\pip.exe install tornado`
- The above command would invoke the local environment under Python310 and pip would install `tornado` to `Lib\site-packages`

### Pip and self-updates

- `pip` can be invoked both as both a python module by using `python -m pip` and externally as `pip.exe` or `pip3.exe`. Examples:
    - `python.exe pip.exe install  sentencepiece`
    - `python.exe pip3.exe install  sentencepiece`
    - `python.exe -m pip install  sentencepiece`
- The command to update pip starts with `python -m pip` which invokes pip as a python module in order to update the `pip.exe` on the file system. However, the file system version, `pip.exe`, cannot cannot be used to update itself since the file is locked while in use. The following will fail:
    - `python pip.exe install --upgrade pip`  
- In other words, `pip.exe` is not actually needed to manage Python library versions because the module version is always available as `python -m pip` or  to manage 

## Additional resources

- Python's [official documentation](//docs.python.org/3/installing/index.html)
- `pip install --help`      #For additional confusion.
