## Text Encoding

### Theory

- Computers only understand 1's and 0's. The letter `A` is ultimately a series of 1's and 0's. How does a computer know to display `A`, `a`, `à`, or `あ`? By using a standardized encoding schema.
- Due to various horrible and historical reasons, there is no way for computers to deterministically detect arbitrary character encodings from files. Automatic encoding detection is a lie. Those just use heuristics which can and will fail catastrophically eventually.
- Thus, the encodings for the text files and the console must be specified at runtime, or something might break.

### Common and Standard Encodings

- For the supported encodings see: [standard-encodings](//docs.python.org/3.7/library/codecs.html#standard-encodings).  Common encodings:
    - `utf-8` - If at all possible, please only use `utf-8`, and use it for absolutely everything.
        - py3TranslateLLM uses `utf-8` as the default encoding for everything except kirikiri.
    - `shift-jis` - Required by the kirikiri game engine and many Japanese visual novels, games, programs, and media in general.
    - `utf-16-le` - a.k.a. `ucs2-bom-le`. Alternative encoding used by the kirikiri game engine. TODO: Double check this.
    - `cp437` - This is the old IBM/DOS code page for English that Windows with an English locale often uses by default. Thus, this is very often the encoding used by `cmd.exe`.
    - `cp1252` - This is the code page for western european languages that Windows with an English locale often uses by default. Thus, this is very often the encoding used by `cmd.exe`.

### Windows specific notes

- On newer versions of Windows (~Win 10 1809+), consider changing the console encoding to native `utf-8`. There is a checkbox for it in the change locale window.
- Historically, setting the Windows command prompt to ~utf-8 will reliably make it crash which makes having to deal with `cp437` and `cp1252` inevitable.
- To print the currently active code page on Windows, open a command prompt and type `chcp`
    - To change the code page for that session type `chcp <codepage #>` as in: `chcp 1252`

### Text Encoding and py3TranslateLLM

- Tip: Use `py3TranslateLLM.ini` to specify the encoding for text files used with `py3TranslateLLM.py` .
- For compatability reasons, everything gets converted to binary strings for stdout which can result in the console sometimes showing utf-8 hexadecimal (hex) encoded unicode characters, like `\xe3\x82\xaf\xe3\x83\xad\xe3\x82\xa8`, especially with `debug` enabled. To convert them back to non-ascii chararacters, like `クロエ`, dump them into a hex to unicode converter.
    - Example: [www.coderstool.com/unicode-text-converter](//www.coderstool.com/unicode-text-converter)
- Some character encodings cannot be converted to other encodings. When such errors occur, use the following error handling options:
    - [docs.python.org/3.7/library/codecs.html#error-handlers](//docs.python.org/3.7/library/codecs.html#error-handlers), and [More Examples](//www.w3schools.com/python/ref_string_encode.asp) -> Run example.
    - The default error handler for input files is `strict` which means 'crash the program if the encoding specified does not match the file perfectly'.
    - On Python >= 3.5, the default error handler for the output file is `namereplace`.  This obnoxious error handler:
        - Makes it obvious that there were conversion errors.
        - Does not crash the program catastrophically.
        - Makes it easy to do ctrl+f replacements to fix any problems.
            - Tip: Use `postWritingToFileDictionary` or [py3stringReplace](//github.com/gdiaz384/py3stringReplace) to automate these ctrl+f replacements.
    - If there are more than one or two such conversion errors per file, then the chosen file encoding settings are probably incorrect.
- If the `chardet` library is available, it will be used to try to detect the character encoding of files via heuristics. While this imperfect solution is obviously very error prone, it is still better to have it than not.
    - To make it available: `pip install chardet`
    - If it is not available, then everything is assumed to be `utf-8` unless otherwise specified.
