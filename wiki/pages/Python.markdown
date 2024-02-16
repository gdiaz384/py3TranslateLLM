##  Python Resources:

### Make sure Python is installed

- `python --version` #Find out what major Python version is installed. 3.5, 3.6, 3.7, etc and where it is located.
    - `where python` #Windows.
    - `which python` #Linux.
        - If `python` is a symlink, as is the norm, then follow it to the target:
        - `ls -la /usr/bin/python` #Use the path specified in the previous command.

### Documentation:

- Python's official documentation: https://www.python.org/doc
- Overview: https://wiki.python.org/moin/BeginnersGuide/Overview
- FAQ: https://docs.python.org/3/faq/general.html
- Tutorial: https://docs.python.org/3/tutorial/index.html
- Glossary and introduction to pip: https://docs.python.org/3/installing/index.html

### To create a portable instance of Python

1. Install Python somewhere.
2. Use archiving software like [7-Zip](https://7-zip.org/) to create an archive from the contents.
3. Uninstall Python.
4. Extract the archive.
5. That should create a Python instance that is not in `%path%`/`$Path` and that the base OS does not understand is installed. The archive can also be moved to other systems of the same OS (Windows, Linux, OSX) and architecture (AMD64, arm) and extracted as-is, ready to use.

### Other Notes:

- If intending to use Python as a portable version, install it to a random location not in %path%/$PATH, then use the `-s` `-E` `-P` `-I` command line switches to manage keeping it isolated.
- Command line switch documentation: https://docs.python.org/3/using/cmdline.html

