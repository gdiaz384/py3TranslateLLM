# py3TranslateLLM.py

This Python program is a CLI wrapper for the following translation engines:

- KoboldCPP API, [Large Language Model (LLM) -  Wiki](//en.wikipedia.org/wiki/Large_language_model).
- DeepL API (Free), [Neural net Machine Translation (NMT) - Wiki](//en.wikipedia.org/wiki/Neural_machine_translation).

And provides interoperability for the following formats:

- Comma separated value text documents (.csv).
- Microsoft Excel document (.xlsx).
- KAG3 used in the kirikiri game engine (.ks).
- Random text files (.txt).

The focus is the spreadsheet formats, but a built in customizable parser supports inputs and replacements into arbitrary text files.

## Support is planned for:

- DeepL API (Pro), NMT.
- DeepL (Web hook), NMT.
- fairseq/Sugoi Offline Translator, NMT.
- OpenDocument spreadsheet (.ods).
- Microsoft Excel document (.xls).
- KAG3 used in Tyrano script (.ks/.ts?).
- .JSON (Very limited support).
    - To process additional types of JSON, open an issue and provide an `example.json`.

Not Planned:

- OpenAI's GPT. Instead consider:
    - [DazedMTL](//github.com/dazedanon/DazedMTLTool) - Supports both v3.5 and v4.0 LLM models.
- Sugoi Translator Premium/Papago/DeepL.
- Most other translation engines, like Google Translate, Google Cloud NMT, Bing Translate, Microsoft Azure NMT, Yandrex, etc.
    - Use [Translator++](//dreamsavior.net/download) for those.

## What are the best LLM models available?

- Guide: huggingface's [chatbot-arena-leaderboard](//huggingface.co/spaces/lmsys/chatbot-arena-leaderboard). Examples:
    - [Mixtral 8x7b v0.1](//huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF).
    - [Tulu-2-DPO](//huggingface.co/TheBloke/tulu-2-dpo-70B-GGUF).
- Notes:
    - The size of the model is also the RAM requirements to load it into memory.
    - The more it fits into GPU memory (VRAM), the better the performance.
    - Not all models listed on leaderboard are compatible with KoboldCPP. See KoboldCPP's [documentation](//github.com/LostRuins/koboldcpp/wiki) for compatible model formats.

## Installation guide

`Current version: 0.1 - 2024Jan20 pre-alpha`

Warning: py3TranslateLLM is currently undergoing active development but the project in the pre-alpha stages. Do not attempt to use it yet. This notice will be removed when core functionality has been implemented and the project has entered 'beta' development.

1. Install [Python 3.7+](//www.python.org/downloads). For Windows 7, use [this repository](//github.com/adang1345/PythonWin7/).
    - Make sure `Add to Path` is checked/selected.
    - Open an command prompt.
    - `python --version` #Check to make sure Python 3.7+ is installed.
    - #Optional but reccomended. Update python's package manager program.
1. Download py3TranslateLLM using one of the following methods:
    1. Git:  #Requires `git` to be installed.
        1. Open an administrative command prompt.
        2. Navigate to a directory that supports downloading and arbitrary file execution.
        3. `git clone https://github.com/gdiaz384/py3TranslateLLM`
    1. Download the latest project archive:
        - Click on the green `< > Code` button at the top -> Download ZIP.
    1. Download from last stable release:
        - Click on on "Releases" at the side (desktop), or bottom (mobile), or [here](//github.com/gdiaz384/py3TranslateLLM/releases).
        - Download either of the archive formats (.zip or .tar.gz).
1. If applicable, extract py3TranslateLLM to a directory that supports arbitrary file execution.
1. Open an administrative command prompt.
1. `cd /d py3TranslateLLM`  #change directory to enter the `py3TranslateLLM` folder.
6. `pip install -r requirements.txt`
7. `python py3TranslateLLM.py --help`

Install/configure these other projects as needed:
- DeepL:
    - [DeepL API](//www.deepl.com/pro?cta=header-pro) support is implemented using their [Python library](//pypi.org/project/deepl) which was installed with:
        - `pip install -r requirements.txt` but it can be installed separately with:
        - `pip install DeepL`
        - Usage of the DeepL API, both Free and Pro, requires an [account](//www.deepl.com/login) and credit card verification.
    - [DeepL Web](//www.deepl.com/translator) and DeepL's [native clients](//www.deepl.com/en/app) do not seem to have usage limits, and the Windows client at least does not require an account. They might do IP bans after a while.
    - All usage of DeepL's translation services and is governed by their [Terms of Use](//www.deepl.com/en/pro-license).
    - For the DeepL API, an API key is needed. It must be in one of the following places:
        - TODO: Put stuff here.
- LLM support is currently implemented using the KoboldCPP's API which requires KoboldCPP:
    - CPU/Nvidia GPUs: [KoboldCPP](//github.com/LostRuins/koboldcpp), [FAQ](//github.com/LostRuins/koboldcpp/wiki).
    - AMD GPUs: [KoboldCPP-ROCM](//github.com/YellowRoseCx/koboldcpp-rocm).
    - Developed and tested using `KoboldCPP_nocuda.exe` v1.53 which implements KoboldCPP API v1.
- [fairseq](//github.com/facebookresearch/fairseq) is a library released by Facebook/Meta for data training.
    - Sugoi NMT is a wrapper for fairseq that comes preconfigured with a Japanese->English dictionary.
    - To install and use fairseq outside of Jpn->Eng translation, refer to fairseq's [documentation](//fairseq.readthedocs.io/en/latest) and obtain an appropriately trained model.
- Sugoi NMT, a wrapper for fairseq that only does Jpn->Eng translation, requires Sugoi Translator which is part of the [Sugoi Toolkit](//sugoitoolkit.com).
    - DL: [here](//www.patreon.com/mingshiba/about) or [here](//archive.org/search?query=Sugoi+Translator+Toolkit).
    - Reccomended: Update the base [model](//www.kecl.ntt.co.jp/icl/lirg/jparacrawl).
        - Download -> NMT Models (based on v3.0) -> Direction -> Japanese-to-English -> big -> Download
        - Move `big.pretrain.pt`, `dict.en.txt`, and `dict.ja.txt` to: `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\offlineTranslation\fairseq\japaneseModel`
    - Reccomended: Remove some of the included spyware.
        - Open: `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\main.js`
        - Comment out `/*  */` or delete the analytics.
    - Tested using Sugoi Offline Translator 4.0 which is part of Sugoi Toolkit 6.0/7.0.

## Usage:

`TODO:`
```
python py3TranslateLLM.py -h
py3TranslateLLM.py koboldcpp --address=http://192.168.1.100 --port=5001
py3TranslateLLM.py deepl_api_free [options]
py3TranslateLLM.py deepl_api_pro [options]
py3TranslateLLM.py deepl_web [options]
py3TranslateLLM.py sugoi [options] #sugoi is an alias for fairseq
py3TranslateLLM.py fairseq [options]
```

## Notes:

- Concept art:
    - The design concept behind pyTranslateLLM is to produce the highest quality machine and AI translations possible for dialogue and narration by providing LLM/NMT models the information they need to translate to the best of their ability. This includes but is not limited to:
        - Bunding the source language strings into paragraphs to increase context.
        - For LLMs and DeepL, providing them with the history of previously translated text to ensure proper flow of dialogue.
        - For LLMs, identifying any speakers by name, sex and optionally other metrics like age and occupation.
        - Removing and/or substituting strings that should not be translated prior to forming paragraphs and prior to submitting text for translation, examples of removed or altered text: [＠クロエ] [r] [repage] [heart].
            - This should help the LLM/NMT understand the submitted text as contiguous 'paragraphs' better.
    - In addition, substution dictionaries are supported at every step of the translation workflow to fine tune input and output and deal with common mistakes. This should result in a further boost in translation quality.
    - Other translation techniques omit one or all of the above. Providing this information _should_ dramatically increase the translation quality when translating context heavy languages, like Japanese.
    - **If translating from context heavy languages, like English, there should not be any or only small differences in translation quality**. Just use G-Translate instead for such languages.
    - The intent is to help translators by cutting down on the most time consuming aspect of creating quality dialogue translations, the editing phase, and to have a program that complements other automated parsing and script extraction programs.
    - Other programs can be used to find and parse small bits of untranslated text in text files and images. This program focuses on dialogue.
    - While it is not the emphasis of this program, there is some code to help extract dialogue from certain common formats and then reinsert it automatically after translation including automatic handling of word wrap.
- For the spreadsheet formats (.csv, xlsx, .xls, .ods):
    - The first row is reserved for headers and is always ignored for data processing otherwise.
    - The first column must be the raw text. Multiple lines within a cell, called 'paragraphs,' are allowed.
        - Paragraph spacing will not be preserved in the output cell, but will instead be regenerated dynamically when writting to the output files based upon the configurable word wrap settings.
            - This behavior can be disabled by setting paragraphDelimiter=newLine or enabling --lineByLineMode (-lbl) mode at runtime.
    - The second column is reserved for metadata used by py3TranslateLLM and always ignored otherwise.
        - Do not modify the metadata column.
    - The third column and columns after it are used for the translation engines (KoboldCPP/modelName, DeepL API, DeepL (Web), Sugoi, fairseq).
        - One translation engine per column. If the current translation engine does not exist as a column, it will be added dynamically.
            - KoboldCPP translation engines are in the format `koboldcpp/[modelName]`, therefore changing the model mid-translation will result in a completely new column because different models produce different output.
        - The source content for the translation engine columns is always based on the first column.
        - The order of the translation engine columns (3+) only matters in the following situation:
            - The column furthest to the right will be preferred when writing back to files (.ks, .ts).
    - .csv files:
        - Must use a comma `,` as a delimiter.
        - Entries containing:
            - new line character(s) `\n`, `\r\n` 
            - comma(s) `,`
            - must be quoted using two double quotes `"`. Example: `"Hello, world!"`
        - Single quotes `'` are not good enough. Use double quotes `"`
        - Entries containing more than one double quote `"` within the entry must escape those quotes using a backlash `\` like: `"\"Hello, world!\""`
        - Whitespace is ignored for `languageCodes.csv`.
        - Whitespace is preserved for all of the dictionaries.
- For the text formats used for input (.txt, .ks, .ts), the inbuilt parser will use the user provided settings file to parse the file.
    - A settings file is required when parsing such raw text files.
    - Examples of text file parsing templates can be found under `resources/templates/`.
- The text formats used for templates and settings (.txt) have their own syntax:
    - `#` indicates that line is a comment.
    - Values are specified by using `Item=Value` Example:
        - `paragraphDelimiter=emptyLine`
    - Empty lines are ignored.
- If interrupted, use one of the backup files created under backups/[date] to continue with minimal loss of data. Resuming from save data in this folder after being interrupted is not automatic. `--resume` (`-r`) technically exists, but can be overly picky.
- In addition to the libraries listed below, py3TranslateLLM also uses several libraries from the Python standard library. See source code for an enumeration of those.
- Settings can be specified at runtime from the command prompt or from `py3TranslateLLM.ini`.
    - Settings read from the command prompt take priority over the `.ini`.
    - Values are designated using the following syntax:
        - `commandLineOption=value`
        - The 'None' keyword for an option indicates no value. Example: `preTranslationDictionary=None`
        - Whitespace is ignored.
        - Lines with only whitespace are ignored.
        - Lines starting with `#` are ignored. In other words, `#` means a comment.
- Aside: LLaMA stands for Large Language Model Meta AI. [Wiki](//en.wikipedia.org/wiki/LLaMA).

### The following files are required:

Variable name | Description | Examples
--- | --- | ---
`fileToTranslate` | The file to translate. | `A01.ks`, `backup.2024Jan10.xlsx`
`parsingSettingsFile` | Defines how to read and write to `fileToTranslate`. Required if working from a text file or if outputting to one but not if only using spreadsheet formats. | `resources/ templates/ KAG3_kirikiri_parsingTemplate.txt`
`languageCodesFile` | Contains the list of supported languages. | `resources/ languageCodes.csv`

### The following files are optional:

Variable name | Description | Examples
--- | --- | ---
`py3TranslateLLM.ini` | This file may be used instead of the CLI to specifying input options. Keys in the key=value pairs are case sensitive. | `py3TranslateLLM.ini`, `renamedBinary.ini`
`parsingSettingsFile` | Defines how to read and write to `fileToTranslate`. Not required if working only with spreadsheet formats but required if reading from or writing to text files. | `resources/ templates/ KAG3_kirikiri_parsingTemplate.txt`
`outputFile` | The name and path of the file to use as output. Will be same as input if not specified. Specify a spreadsheet format to dump the raw data or a text file to output only the preferred translation. | `None`, `output.csv`, `myFolder/ output.xlsx`
`characterNamesDictionary` | Entries will be submitted to the translation engine but then replaced back to the original text after translation. | `resources/ templates/ characterNamesDictionary_example.csv`
`preTranslationDictionary` | Entries will be replaced prior to submission to the translation engine. | `preTranslationDictionary.csv`
`postTranslationDictionary` | Entries will be replaced after translation. | `postTranslationDictionary.csv`
`postWritingToFileDictionary` | After the translated text has been written back to a text file, the file will be opened again to perform these replacements. | `postWritingToFileDictionary.csv`

### Notes about encodings:

- Computers only understand 1's and 0's. The letter `A` is ultimately a series of 1's and 0's. How does a computer know to display `A`, `a`, `à`, or `あ`? By using a standardized encoding schema.
- Due to various horrible and historical reasons, there is no way for computers to deterministically detect arbitrary character encodings from files. Automatic encoding detection is a lie. Those just use heuristics which can and will fail catastrophically eventually.
- Thus, the encodings for the text files and the console must be specified at runtime, or something might break.
- For the supported encodings see: [standard-encodings](//docs.python.org/3.7/library/codecs.html#standard-encodings).  Common encodings:
    - `utf-8` - If at all possible, please only use `utf-8`, and use it for absolutely everything.
        - py3TranslateLLM uses `utf-8` as the default encoding for everything except kirikiri.
    - `shift-jis` - Required by the kirikiri game engine and many Japanese visual novels, games, programs, and media in general.
    - `utf-16-le` - a.k.a. `ucs2-bom-le`. Alternative encoding used by the kirikiri game engine. TODO: Double check this.
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
            - Alternatively, use `postWritingToFileDictionary` to automate ctrl+f replacements.
    - If there are more than one or two such conversion errors per file, then the chosen file encoding settings are probably incorrect.
- If the `chardet` library is available, it will be used to try to detect the character encoding of files via heuristics. While this imperfect solution is obviously very error prone, it is still better to have it than not.
    - To make it available: `pip install chardet`
    - If it is not available, then everything is assumed to be `utf-8`.

### Notes about languages:

- The list of supported languages can be found at `resources/languageCodes.csv`.
- If using an LLM for translation that utilizes a language not listed in `languageCodes.csv`, then add that language as a new row to make py3TranslateLLM aware of it.
- The default supported languages list is based on DeepL's [supported languages list](//support.deepl.com/hc/en-us/articles/360019925219-Languages-included-in-DeepL-Pro) and their [openapi.yaml](//www.deepl.com/docs-api/api-access/openapi) specification, excluding the addition of `Chinese (traditional)`.
    - Note that DeepL has a few quirks, like being picky about the target English dialect based upon the source language.
- py3TranslateLLM uses mappings based upon [this](//www.loc.gov/standards/iso639-2/php/code_list.php) table and supports any of the following when specifying a language:
    1. The full language: `English`, `German`, `Spanish`, `Russian`.
    2. The 2 letter language code: `en-us`, `de`, `es`, `ru`.
    3. The 3 letter language code: `eng`, `deu`, `spa`, `rus`.
    4. Entries are case insensitive. Both `lav` and `LAV` will work.
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

Parameter | Description | Example(s)
--- | --- | ---
`-mode`, `--translationEngine` | The engine used for translation. Use `parseOnly` to read from source files but not translate them. | `parseOnly`, `koboldcpp`, `deepl-api-free`, `deepl-api-pro`, `deepl-web`, `fairseq`, `sugoi`
`-a`, `--address` | A valid network address including the protocol but not the port number. | `--address=http://192.168.1.100`, `--address=http://localhost`
`-p`, `--port` | The port number associated with the `--address` listed above. | `--port=5001`, `--port=8080`, `--p=443`

## Regarding Python libraries:

- Different libraries are not all forward/backwards compatible with all major Python versions or compatible with this or that version of (various) libraries they import, but they still have to somehow all work together with compatible versions on a wide variety of different computers. Does that sound like hell? Well, welcome to software development. So anyway, below are the versions that were tested and developed while using Python 3.7.6. The user's local enviornment may differ leading to undefined behavior. Have fun.
- It is not necessarily clear what versions work with what other versions, so just install whatever and hope it works:

Library name | Required, Reccomended, or Optional | Description | Install command | Version used to develop py3TranslateLLM
--- | --- | --- | --- | ---
[openpyxl](//pypi.python.org/pypi/openpyxl) | Required. | Used for main data structure and Microsoft Excel Document (.xlsx) support. | `pip install openpyxl` | 3.1.2
openpyxlHelpers | Required. | Has various functions to manage using openpyxl as a data structure. | Included with py3TranslateLLM. | Unversioned.
dealWithEncoding | Required. | Handles text codecs and implements `chardet`. | Included with py3TranslateLLM. | 0.1 2024Jan19.
[requests](//pypi.org/project/requests) | Required. | Used for HTTP get/post requests. Required by both py3TranslateLLM and DeepL. | `pip install requests` | 2.31.0
[chardet](//pypi.org/project/chardet) | Reccomended. | Improves text codec handling. | `pip install chardet` | 5.2.0
[DeepL-python](//github.com/DeepLcom/deepl-python) | Reccomended. | Used for DeepL NMT, optional otherwise. | `pip install deepl` | 1.16.1
[xlrd](//pypi.org/project/xlrd/) | Optional. | Provides reading from Microsoft Excel Document (.xls). | `pip install xlrd` | 2.0.1
[xlwt](//pypi.org/project/xlwt/) | Optional. | Provides writing to Microsoft Excel Document (.xls). | `pip install xlwt` | 1.3.0
[odfpy](//pypi.org/project/odfpy) | Optional. | Provides interoperability for Open Document Spreadsheet (.ods). | `pip install odfpy` | 1.4.1

###  Guide: Installing and managing Python library versions with `pip`:

- `python --version` #Find out what major Python version is installed. 3.5, 3.6, 3.7, etc and where it is located.
    - `where python` #Windows.
    - `which python` #Linux.
        - If `python` is a symlink, as is the norm, then follow it to the target:
        - `ls -la /usr/bin/python` #Use the path specified in the previous command.
- `python -m pip install --upgrade pip` #Update pip.
- `pip --version`
- `pip install -r requirements.txt` #Use this syntax to install a predefined list of libraries from a file. Alternatively:
- `pip install <libraryName>` #Examples:
    - `pip install openpyxl`
- `pip index versions <libraryName>`  #Use this syntax to list available versions for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions openpyxl`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install openpyxl==3.1.2`
- `pip install --help`      #For additional confusion.

## Licenses:

- Python standard library's [license](//docs.python.org/3/license.html).
- [openpyxl](//pypi.python.org/pypi/openpyxl)'s [license](//foss.heptapod.net/openpyxl/openpyxl/-/blob/3.1.2/LICENCE.rst) and [source code](//foss.heptapod.net/openpyxl/openpyxl).
- [chardet](//pypi.org/project/chardet)'s license is [LGPL v2+](//github.com/chardet/chardet/blob/main/LICENSE). [Source code](//github.com/chardet/chardet).
- [odfpy](//pypi.org/project/odfpy)'s, license is [GPL v2](//github.com/eea/odfpy/blob/master/GPL-LICENSE-2.txt). [Source code](//github.com/eea/odfpy).
- [xlrd](//pypi.org/project/xlrd)'s [license](//github.com/python-excel/xlrd/blob/master/LICENSE) and [source code](//github.com/python-excel/xlrd).
- [xlwt](//pypi.org/project/xlwt/)'s [license](//github.com/python-excel/xlwt/blob/master/LICENSE) and [source code](//github.com/python-excel).
- [KoboldCPP](//github.com/LostRuins/koboldcpp) is [AGPL v3](//github.com/LostRuins/koboldcpp/blob/concedo/LICENSE.md). The GGML library and llama.cpp part of KoboldCPP has this [license](//github.com/LostRuins/koboldcpp/blob/concedo/MIT_LICENSE_GGML_LLAMACPP_ONLY).
- DeepL's [various plans](//www.deepl.com/pro) and [Terms of Use](//www.deepl.com/en/pro-license). DeepL's [python library](//pypi.org/project/deepl) for their API has this [license](//github.com/DeepLcom/deepl-python/blob/main/LICENSE) and [source code](//github.com/DeepLcom/deepl-python).
- [fairseq](//github.com/facebookresearch/fairseq) and [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE).
- [Sugoi](//sugoitoolkit.com) and [source code](//github.com/leminhyen2/Sugoi-Japanese-Translator).
    - The pretrained model used in Sugoi NMT has its own non-commericial [license](//www.kecl.ntt.co.jp/icl/lirg/jparacrawl).
    - 'Sugoi NMT' is a wrapper for fairseq which, along with the pretrained model, does the heavy lifting for 'Sugoi NMT'.
    - Sugoi NMT is one part of the 'Sugoi Translator Toolkit' which is itself part of the free-as-in-free-beer distributed 'Sugoi Toolkit' which contains other projects like manga translation and upscaling.
    - The use of Github to post source code for Sugoi Toolkit suggests intent to keep the wrapper code under a permissive license. A more concrete license may be available on discord.
- py3TranslateLLM.py and the associated libraries under `resources/` are [GNU Affero GPL v3](//www.gnu.org/licenses/agpl-3.0.html).
    - Feel free to use it, modify it, and distribute it to an unlimited extent, but if you distribute binary files of this program outside of your organization, then please make the source code for those binaries available.
    - The imperative to make source code available also applies if using this program as part of a server if that server is publically accessible.
    - Binaries for py3TranslateLLM.py made with pyinstaller, or another program that can make binaries, also fall under GNU Affero GPL v3.
        - This assumes the licenses for projects used in the binary are compatible with one another. If the licenses used for a particular binary are not compatible with one another, then the resulting binary is not considered redistributable. Only lawyers can determine that, and also only lawyers need to worry about it.

