# py3TranslateLLM.py

This Python program is a CLI wrapper for the following translation engines:

- KoboldCPP API [Large Language Model (LLM) -  Wiki](//en.wikipedia.org/wiki/Large_language_model).
- DeepL API (Free): [Neural net Machine Translation (NMT) - Wiki](//en.wikipedia.org/wiki/Neural_machine_translation).

And provides interoperability for the following formats:

- Comma separated value text documents (.csv).
- Microsoft excel document (.xlsx).
- KAG3 used in the kirikiri game engine (.ks).
- Random text files (.txt).

The focus is the spreadsheet formats, but a built in customizable parser supports inputs and replacements into arbitrary text files.

## Support is planned for:

- DeepL API (Pro), NMT.
- DeepL (Web hook), NMT.
- Sugoi Offline Translator, NMT.
- Open document spreadsheet (.ods).
- Microsoft excel document (.xls).
- KAG3 used in Tyrano script (.ts ?).

Not Planned:

- JSON. Does anyone want this? Open a feature request if so.
- OpenAI's GPT 3.5/4+.
    - For OpenAI's LLM, consider:
    - [DazedMTL](//github.com/dazedanon/DazedMTLTool)
        - Supports both 3.5 and 4.0 models.

## What are the best LLM models available?

- Guide: huggingface's [chatbot-arena-leaderboard](//huggingface.co/spaces/lmsys/chatbot-arena-leaderboard)
- Example: [Mixtral 8x7b v0.1](//huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF).
    - Pick a non-K_M version.
    - The size of the model is also the RAM requirements to load it into memory.
    - The more it fits into GPU memory (VRAM), the better the performance.
- Not all the models are compatible with KoboldCPP. See their [documentation]() for compatible model formats.

## Installation guide

`Current version: 0.1 - 2024Jan16`

Warning: py3TranslateLLM is currently undergoing active development but the project in the pre-alpha stages. Do not attempt to use it yet. This notice will be removed when when core functionality can been fully implemented.

1. Open an administrative command prompt.
2. Navigate to a directory that supports downloading and arbitrary file execution.
3. `git clone []`   #Requires `git` to be installed.
4. `cd py3TranslateLLM`
5. `python --version` #Check to make sure Python 3.7+ is installed.
6. `pip install -r requirements.txt`
7. `python py3TranslateLLM.py --help`

- DeepL:
    - [DeepL API](//www.deepl.com/pro?cta=header-pro) support is implemented using their Python library which is installed with:
        - `pip install -r requirements.txt` but it can be installed separately with:
        - `pip install DeepL`
        - Usage of the DeepL API, both Free and Pro, requires an [account](//www.deepl.com/login) and credit card verification.
    - [DeepL Web](//www.deepl.com/translator) and DeepL's [native clients](//www.deepl.com/en/app) do not seem to have usage limits, and the Windows client at least does not require an account. They might do IP bans after a while.
    - All usage of DeepL's translation services and is governed by their [Terms of Use](//www.deepl.com/en/pro-license).    
- LLM support is currently implemented using the KoboldCPP's API which requires KoboldCPP:
    - CPU/Nvidia GPUs: [KoboldCPP](//github.com/LostRuins/koboldcpp), [FAQ](//github.com/LostRuins/koboldcpp/wiki).
    - AMD GPUs: [KoboldCPP-ROCM](//github.com/YellowRoseCx/koboldcpp-rocm).
    - Developed and tested using `KoboldCPP_nocuda.exe` v1.53 which implements KoboldCPP API v1.
- Sugoi NMT requires [Sugoi Translator](//sugoitoolkit.com/). Tested using Sugoi Offline Translator 4.0 (part of Sugoi Toolkit 6.0).
    - DL: [here](//www.patreon.com/mingshiba/about) or [here](//archive.org/search?query=Sugoi+Translator+Toolkit).
    - Reccomended: Update the base [model](//www.kecl.ntt.co.jp/icl/lirg/jparacrawl).
        - Download -> NMT Models (based on v3.0) -> Direction -> Japanese-to-English -> big -> Download
        - Move `big.pretrain.pt`, `dict.en.txt`, and `dict.ja.txt` to: `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\offlineTranslation\fairseq\japaneseModel`

## Usage:

```
python py3TranslateLLM.py -h
py3TranslateLLM.py koboldcpp --address=http://192.168.1.100 --port=5001
py3TranslateLLM.py deepl_api_free [options]
py3TranslateLLM.py deepl_api_pro [options]
py3TranslateLLM.py deepl_web [options]
py3TranslateLLM.py sugoi [options]
```

## Notes:

- For the spreadsheet formats (.csv, xlsx, .xls, .ods):
    - The first row is reserved for headers and is always ignored for data processing otherwise.
    - The first column must be the raw text. Multiple lines within a cell, called 'paragraphs,' are allowed and will be preserved in the output cell.
    - The second column is reserved for metadata that py3TranslateLLM requires. Do not modify.
    - The columns after the second column are used for KoboldCPP and DeepL output based on the first column.
        - The order to the columns after the second one matters only in the following situation:
        - The column furthest to the right will be preferred when writing back to files (.ks, .ts).
    - .csv files:
        - Must use a comma `,` as a delimiter.
        - Entries containing:
            - new line character(s) `\n`, `\r\n` 
            - comma(s) `,`
            - must be quoted using two double quotes `"` like so: `"Hello, world!"`
        - Single quotes `'` are not good enough. Use double quotes `"`
        - Entries containing double quotes `"` within the entry must escape those quotes using a backlash `\` like: `Hel\"lo` and `"\"Hello, world!\""`
- For the text formats used for input (.txt, .ks), the inbuilt parser will use the user provided settings to parse the file.
    - If one is not specified, the user will be prompted to use one.
    - Examples of text file parsing templates can also be found under `resources/templates/`.
- The text formats used for templates and settings (.txt) have their own syntax:
    - `#` indicates that line is a comment.
    - Values are specified by using `Item=Value` Example:
        - `paragraphDelimiter=emptyLine`
    - Empty lines are ignored.
- If interrupted, use one of the backup files created under backups/[date] to continue with minimal loss of data. Resuming from save data in this folder after being interrupted is not automatic. `resume` (`-r`) technically exists, but can be overly picky.
- In addition to the libraries listed below, py3TranslateLLM also uses several libraries from the Python standard library. See source code for an enumeration of those.

### Notes about encodings:

- Computers only understand 1's and 0's. The letter `A` is ultimately a series of 1's and 0's. How does a computer know to display `A`, `a`, `à`, or `あ`? By using a standardized encoding schema.
- Due to various horrible and historical reasons, there is no way for computers to deterministically detect arbitrary character encodings from files. Automatic encoding detection is a lie. Those just use heuristics which can and will fail catastrophically eventually.
- Thus, the encodings for the text files and the console must be specified at runtime, or something might break.
- For the supported encodings see: [standard-encodings](//docs.python.org/3.7/library/codecs.html#standard-encodings).  Common encodings:
    - `utf-8` - If at all possible, please only use `utf-8`, and use it for absolutely everything.
        - py3TranslateLLM uses `utf-8` as the default encoding for everything except kirikiri.
    - `shift-jis` - Required by the kirikiri game engine and many Japanese visual novels/games/media.
    - `utf-16-le` - a.k.a. `ucs2-bom-le`. Alternative encoding used by the kirikiri game engine. Todo: Double check this.
    - `cp437` - This is the old IBM/DOS code page for English that Windows with an English locale often uses by default. Thus, this is very often the encoding used by `cmd.exe`.
    - `cp1252` - This is the code page for western european languages that Windows with an English locale often uses by default. Thus, this is very often the encoding used by `cmd.exe`.
- Windows specific notes:
    - On newer versions of Windows (~Win 10 1809+), consider changing the console encoding to native `utf-8`. There is a checkbox for it in the change locale window.
    - Historically, setting the Windows command prompt to ~utf-8 will reliably make it crash which makes having to deal with `cp437` and `cp1252` inevitable.
    - To print the currently active code page on Windows, open a command prompt and type `chcp`
        - To change the code page for that session type `chcp <codepage #>` as in: `chcp 1252`
- Some character encodings cannot be converted to other encodings. When such errors occur, use the following error handling options:
    - [docs.python.org/3.7/library/codecs.html#error-handlers](//docs.python.org/3.7/library/codecs.html#error-handlers), and [More Examples](//www.w3schools.com/python/ref_string_encode.asp).
    - The default error handler for input files is `strict` which means 'crash the program if the encoding specified does not match the file perfectly'.
    - The default error handler for the output file is `namereplace`.  This obnoxious error handler:
        - Makes it obvious that there were conversion errors.
        - Does not crash the program catastrophically.
        - Makes it easy to do ctrl+f replacements to fix any problems.
    - If there are more than one or two such conversion errors per file, then the chosen file encoding settings are probably incorrect.
- If the `chardet` library is available, it will be used to try to detect the character encoding of files via heuristics. While this imperfect solution is obviously very error prone, it is still better to have it than not.
    - To make it available: `pip install chardet`
    - If it is not available, then everything is assumed to be `utf-8`.

### Notes about languages:

- The list of supported languages can be found at `resources/languageCodes.csv`.
- If using an LLM for translation that utilizes a language not listed in `languageCodes.csv`, then add that language as a new row to make py3TranslateLLM aware of it.
- The default supported languages list is based on DeepL's [supported languages list](//support.deepl.com/hc/en-us/articles/360019925219-Languages-included-in-DeepL-Pro), excluding the addition of `Chinese (traditional)`.
- py3TranslateLLM uses mappings based upon [this](//www.loc.gov/standards/iso639-2/php/code_list.php) table and supports any of the following when specifying a language:
    1. the full language. Examples: `English`, `German`, `Spanish`, `Russian`.
    2. the 2 letter language code. Examples: `en-us`, `de`, `es`, `ru`.
    3. the 3 letter language code. Examples: `eng`, `deu`, `spa`, `rus`.
    4. Entries are case insensitive. Example: Both `lav` and `LAV` will work.
- DeepL only supports 2 letter language codes which creates some ambiguity regarding conversion to 3 letter language codes.
- Note these quirks and 3 letter language code collisions:
    - `English` has a collision in the 3 letter code `Eng` between `English (American)` and `English (British)`.
        - Selecting the three letter language code of `Eng` will default to `English (American)`, `En-US`.
        - To select `English (British)` as a 3 letter language code, use `Eng-GB`.
        - `English` is also mapped to `English (American)` by default.
            - To select `English (British)`, enter `English (British)` or a language code.
        - The above distinction between the two dialects only applies to selecting English as the target language. If selecting English as a source language, `English` is sufficent and will be used regardless.
    - `Chinese (traditional)`:
        - This is not yet supported by DeepL as a target language.
        - There is a collission when using `Chinese (traditional)` with the `Chinese (simplified)` 2 letter language code.
            - If using the 2 letter language code `ZH`, `Chinese (simplified)` will be selected.
            - To select `Chinese (traditional)` as a 2 letter language code use `ZH-ZH`.
        - The above distinction between the two dialects only applies to selecting Chinese as the target language. If selecting Chinese as a source language, `Chinese` is sufficent and will be used regardless.
            - DeepL supports both `Chinese (traditional)` and `Chinese (simplified)` as the source language using automatic character detection.
    - `Czech` might be CZE (B), or CES (T). It is unclear what DeepL supports. The 3 letter language code of `CES` is used.
    - `Dutch` might be DUT (B), or NLD (T). It is unclear what DeepL supports. The 3 letter language code of `NLD` is used.
    - `French` can be FRE (B), or FRA (T). It is unclear what DeepL supports. The more common `FRA` is used.
        - Aside: French also some very old unused dialects from the middle ages: FRM, FRO.
    - `German` has GER (B), DEU (T). It is unclear what DeepL supports. The 3 letter language code of `DEU` is used.
        - Aside: German has some archaic ones too.
    - Modern `Greek` has GRE (B) and ELL (T). It is unclear what DeepL supports. The 3 letter language code of `ELL` is used.
    - Portuguese has collission in the 3 letter code `POR` between `Portuguese (European)` and `Portuguese (Brazillian)`.
        - Selecting the three letter language code of `POR` will default to `Portuguese (European)`, `PT-PT`.
        - To select `Portuguese (Brazillian)` as a 3 letter language code, use `POR-BRA`.
        - The above distinction between the two dialects only applies to selecting Portuguese as the target language. If selecting Portuguese as a source language, `Portuguese` is sufficent and will be used regardless.
    - `Romanian` has both RUM (B) and RON (T). It is unclear what DeepL supports. The 3 letter language code of `RON` is used.
    - `Spanish` has an alias of `Castilian`.
 
## Parameters

`partial list:`

parameter | value or description | example (partial)
--- | --- | ---
[engine] | deepl_api_free, deepl_api_pro, deepl_web, sugoi | `deepl_api_free`
address | a valid network address including the protocol but not the port number | `--address=http://192.168.1.100`
port | a valid port number | `--port=5001`, `--port=8080`, `--port=443`

## Regarding python libraries:

- Different libraries are not all forward/backwards compatible with all major python versions or compatible with this or that version of (various) libraries they import, but they still have to somehow all work together with matching versions on a wide variety of different computers. Does that sound like hell? Well, welcome to software development. So anyway, below are the versions that were tested and developed while using Python 3.7.6. The user's local enviornment may differ leading to undefined behavior. Have fun.
- It is not necessarily clear what versions work with what other versions, so just install whatever and hope it works:

Library Name | Req, Recc, or Opt | Description | Install command | Version used to develop py3TranslateLLM
--- | --- | --- | --- | ---
[openpyxl](//pypi.python.org/pypi/openpyxl) | Required. | Used for main data structure and xlsx support. | `pip install openpyxl` | 3.1.2
dealWithEncoding | Required. | Handles text codecs and implements `chardet`. | Included with py3TranslateLLM. | Unversioned.
[requests](//pypi.org/project/requests) | Required. | Used for HTTP get/post requests. Required by both py3TranslateLLM and DeepL. | `pip install requests`, `pip install deepL` | 2.31.0
[chardet](//pypi.org/project/chardet) | Reccomended. | Improves text codec handling. | `pip install chardet` | 5.2.0
[DeepL-python](//github.com/DeepLcom/deepl-python) | Reccomended. | Used for DeepL NMT, optional otherwise. | `pip install deepl` | 1.16.1
[odfpy](//pypi.org/project/odfpy) | Optional. | Provides interoperability for Open Document Spreadsheet (.ods). | `pip install odfpy` | 1.4.1
[xlrd](//pypi.org/project/xlrd/) | Optional | Provides reading from Microsoft Excel Document (.xls). | `pip install xlrd` | 2.0.1
[xlwt](//pypi.org/project/xlwt/) | Optional | Provides writing to Microsoft Excel Document (.xls). | `pip install xlwt` | 1.3.0

### Installing and managing python library versions with `pip`:

- `python --version` #Find out what major python version is installed. 3.5, 3.6, 3.7, etc
- `python -m pip install --upgrade pip` #Update pip.
- `pip --version`
- `pip install -r requirements.txt` #Use this command to install a predefined list of libraries. Alternatively:
- `pip install <libraryName>` #Examples:
    - `pip install openpyxl`
- `pip index versions <libraryName>`  #Use this command to list what versions are available for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions openpyxl`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install openpyxl==3.1.2`
- `pip install --help`      #For additional confusion.


`pip index versions pandas` #search different versions
- `pip install python3-pandas` #LinuxOnly
- [pandas](//pandas.pydata.org). Used as UI for xls/xlsx/ods/csv conversions. `pip install pandas==1.3.5` Developed and tested using version 1.3.5.
    - For Linux use `python3-pandas`
- numpy - Core pandas dependency. Installed automatically by pip. Developed and tested using version `numpy-1.21.6`
- python-dateutil - Core pandas dependency. Installed automatically by pip. Developed and tested using version `dateutil-2.8.2`
- pytz - Core pandas dependency. Installed automatically by pip. Developed and tested using version `pytz-2023.3.post1`
- xlsxwriter - Provides engine services to pandas. `pip install xlsxwriter` Developed and tested using version `xlsxwriter-3.1.9`

## Licenses:

- Python standard library's [license](//docs.python.org/3/license.html).
- [openpyxl](//pypi.python.org/pypi/openpyxl)'s [license](//foss.heptapod.net/openpyxl/openpyxl/-/blob/3.1.2/LICENCE.rst) and [source code](//foss.heptapod.net/openpyxl/openpyxl).
- [chardet](//pypi.org/project/chardet)'s license is [LGPL v2+](//github.com/chardet/chardet/blob/main/LICENSE). [Source code](//github.com/chardet/chardet).
- [odfpy](//pypi.org/project/odfpy)'s, license is [GPL v2](//github.com/eea/odfpy/blob/master/GPL-LICENSE-2.txt). [Source code](//github.com/eea/odfpy).
- [xlrd](//pypi.org/project/xlrd)'s [license](//github.com/python-excel/xlrd/blob/master/LICENSE) and [source code](//github.com/python-excel/xlrd).
- [xlwt](//pypi.org/project/xlwt/)'s [license](//github.com/python-excel/xlwt/blob/master/LICENSE) and [source code](//github.com/python-excel).
- [KoboldCPP](//github.com/LostRuins/koboldcpp) is [AGPL v3](//github.com/LostRuins/koboldcpp/blob/concedo/LICENSE.md). The GGML library and llama.cpp part of KoboldCPP has this [license](//github.com/LostRuins/koboldcpp/blob/concedo/MIT_LICENSE_GGML_LLAMACPP_ONLY).
- DeepL's [various plans](//www.deepl.com/pro) and [Terms of Use](//www.deepl.com/en/pro-license). DeepL's [python library](//github.com/DeepLcom/deepl-python) for their API has this [license](//github.com/DeepLcom/deepl-python/blob/main/LICENSE).
- [Sugoi](//sugoitoolkit.com) and [source code](//github.com/leminhyen2/Sugoi-Japanese-Translator). The pretrained model for Sugoi NMT has its own non-commericial [license](//www.kecl.ntt.co.jp/icl/lirg/jparacrawl). 'Sugoi NMT' is a wrapper for [fairsequence](//github.com/facebookresearch/fairseq), [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE), which, along with the pretrained model, does the heavy lifting for 'Sugoi NMT'.
    - Sugoi NMT is one part of the 'Sugoi Translator Toolkit' which is itself part of the free-as-in-free-beer distributed 'Sugoi Toolkit' which contains other projects like manga translation and upscaling.
    - The use of Github to post source code for Sugoi Toolkit suggests intent to keep the wrapper code under a permissive license. A more concrete license may be available on discord.
- p3yTranslateLLM is [GNU Affero GPL v3](//www.gnu.org/licenses/agpl-3.0.html).
    - Feel free to use it, modify it, and distribute it to an unlimited extent, but if you distribute binary files of this program outside of your organization, then please make the source code for those binaries available. The imperative to make source code available also applies if using this program as part of a server if that server is publically accessible.
