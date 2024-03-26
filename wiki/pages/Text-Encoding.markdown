## Text Encoding

### Theory

- Computers only understand 1's and 0's. The letter `A` is ultimately a series of 1's and 0's. How does a computer know to display `A`, `a`, `à`, or `あ`? By using a standardized encoding schema.
- Due to various horrible and historical reasons, there is no way for computers to deterministically detect arbitrary character encodings from files.
- Automatic encoding detection is a lie. Those just use heuristics which can and will fail catastrophically eventually.
- Thus, the encodings for text files and the console must be specified at runtime, or something might break.

### Common and Standard Encodings

- For all Python supported encodings see: [standard-encodings](//docs.python.org/3.7/library/codecs.html#standard-encodings). Common encodings:
    - [`utf-8`](https://www.ietf.org/rfc/rfc3629.txt) - If at all possible, please only use `utf-8`, and use it for absolutely everything.
        - py3TranslateLLM uses `utf-8` as the default encoding for everything except kirikiri.
    - `shift-jis` - Required by the kirikiri game engine and many Japanese visual novels, games, programs, media, and text files in general.
    - `utf-16-le` - a.k.a. `ucs2-bom-le`. Alternative encoding used by the kirikiri game engine. TODO: Double check this.
    - `cp437` - This is the old IBM/DOS code page for English that Windows with an English locale often uses by default. 
    - `cp1252` - This is the code page for western european languages that Windows with an English locale often uses by default.
- [Error handlers](//docs.python.org/3.7/library/codecs.html#error-handlers) can be used to handle conversion errors from one type of encoding to another.

### Windows Specific Notes

- Due to English locales being very common on Windows, both `cp437` and `cp1252` are very often the encoding used by `cmd.exe`.
- On newer versions of Windows (~Win 10 1809+), consider changing the console encoding to native `utf-8`.
    - There is a checkbox for it in the change locale window. Check it and restart the PC for changes to take effect.
    - After restarting, set the command prompt to use a font that can display utf-8 glyphs correctly, like MS Gothic.
- Historically, setting the Windows command prompt to ~utf-8 will reliably make it crash which makes having to deal with `cp437` and `cp1252` inevitable.
- To print the currently active code page on Windows, open a command prompt and type `chcp`
    - To change the code page for that session type `chcp <codepage #>` as in: `chcp 1252`
- [Windows CLI](https://devblogs.microsoft.com/commandline/windows-command-line-unicode-and-utf-8-output-text-buffer/) update to utf-8 in Windows 10 1809.

### More Information For Software Developers

- [The Absolute Minimum Every Software Developer Must Know about Unicode and Character Sets](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/).
- https://docs.python.org/3/howto/unicode.html
- https://docs.python.org/3/library/codecs.html#encodings-and-unicode
