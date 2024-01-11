# py3TranslateLLM.py

This python program is a CLI wrapper for the following translation engines:

- KoboldCPP API, Large Language Model (LLM), [Wiki](//en.wikipedia.org/wiki/Large_language_model).
- DeepL API (Free), Neural net Machine Translation (NMT), [Wiki](//en.wikipedia.org/wiki/Neural_machine_translation).

And provides interoperability for the following formats:

- Comma separated value text documents (.csv).
- Microsoft excel document (.xls/xlsx).
- KAG3 used in the kirikiri game engine (.ks).
- Random text files (.txt).

The focus is the spreadsheet formats, but a built in customizable parser supports inputs and replacements into arbitrary text files.

## Support is planned for:

- DeepL API (Pro), NMT.
- DeepL (Web hook), NMT.
- Sugoi Offline Translator, NMT.
- Open document spreadsheet (.ods).
- KAG3 used in Tyrano script (.ts).

Not Planned:

- JSON. Does anyone want this? Open a feature request if so.
- OpenAI's GPT 3.5/4+.
    - For OpenAI's GPT LLM, consider:
    - [DazedMTL](//github.com/dazedanon/DazedMTLTool)
        - Supports both 3.5 and 4.0 models.

## What LLM model should I use with KoboldCPP?

- Guide: huggingface's [chatbot-arena-leaderboard](//huggingface.co/spaces/lmsys/chatbot-arena-leaderboard)
- Example: [Mixtral 8x7b v0.1](//huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF).
    - Pick a non-K_M version.
    - The size of the model is also the RAM requirements to load it into memory.

## Installation guide

1. Open an administrative command prompt.
2. Navigate to a directory that supports downloading and arbitrary file execution.
3. `git clone []`   #Requires `git` to be installed.
4. `cd py3TranslateLLM`
5. `python --version` #Check to make sure Python is installed.
6. `pip install -r requirements.txt`
7. `python py3TranslateLLM --help`

## Usage:

```
python py3TranslateLLM.py -h
py3TranslateLLM.py koboldcpp --address=http://192.168.1.100 --port=5001
py3TranslateLLM.py deepl_api_free
py3TranslateLLM.py deepl_api_pro
py3TranslateLLM.py deepl_web
py3TranslateLLM.py sugoi
```


## Notes:

- For the spreadsheet formats (.csv, .xls/xlsx, .ods):
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
- For the text formats (.txt, .ks), the inbuilt parser will be used using the user provided settings to parse the file.
    - If one is not specified, a template will be generated, and the user will be prompted to use it.
    - Examples of text file parsing templates can also be found under resources/templates/.
- If interrupted, use one of the backup files created under backups/date to continue with minimal loss of data. Resuming from save data in this folder after being interrupted is not automatic.

### Notes about encodings:

- Computers only understand 1's and 0's. The letter `A` is ultimately a series of 1's and 0's. How does a computer know to display `A`, `a`, `à`, or `あ`? By using a standardized encoding schema.
- Due to various horrible and historical reasons, there is no way for computers to deterministically detect arbitrary character encodings from files. Automatic encoding detection is a lie. Those just use heuristics which can and will fail catastrophically eventually.
- Thus, the encodings for the text files and the console must be specified at runtime, or something might break. For the supported encodings see: [standard-encodings](//docs.python.org/3.7/library/codecs.html#standard-encodings).  Common encodings:
    - `utf-8` - If at all possible, please only use `utf-8`, and use it for absolutely everything.
        - py3TranslateLLM assumes utf-8 encoding for everything except kirikiri.
    - `shift-jis` - Required by the kirikiri game engine and many Japanese visual novels/games/media.
    - `utf-16-le` - a.k.a. `ucs2-bom-le`. Alternative encoding used by the kirikiri game engine. Todo: Double check this.
    - `cp437` - This is the old IBM code page for English that Windows with an English locale often uses by default. Thus, this is very often the encoding used by cmd.
    - `cp1252` - This is the code page for western european languages that Windows with an English locale often uses by default. Thus, this is very often the encoding used by cmd.
- Historically, setting the Windows command prompt to ~utf-8 will reliably make it crash making having to deal with `cp437` and `cp1252` inevitable.

### Notes about languages:

- The list of supported languages can be found at resources/languageCodes.csv
- If using an LLM for translation that utilizes a language not listed in languageCodes.csv, then add that language as a new row to make py3TranslateLLM aware of it.
- The default supported languages list is based on DeepL's [supported languages list](//support.deepl.com/hc/en-us/articles/360019925219-Languages-included-in-DeepL-Pro), excluding the addition of `Chinese (traditional)`.
- py3TranslateLLM uses mappings based upon [this](//www.loc.gov/standards/iso639-2/php/code_list.php) table and supports any of the following when specifying a language:
    - 1) the full language,
    - 2) the 2 letter language code, or
    - 3) the 3 letter language code.
- DeepL only supports 2 letter language codes which creates some ambiguity regarding conversion to 3 letter language codes.
- Note these quirks and 3 letter language code collisions:
    - English has a collision in the 3 letter code `ENG` between `English (American)` and `English (British)`
        - Selecting the three letter language code of `ENG` will default to `English (American)`, `EN-US`.
        - To select `English (British)` as a 3 letter language code, use `ENG-GB`.
        - `English` is also mapped to `English (American)` by default.
            - To select `English (British)`, enter `English (British)` or a language code.
        - The above distinction between the two dialects only applies to selecting English as the target language. If selecting English as a source language, `English` is sufficent and will be used regardless.
    - Chinese (traditional):
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

parameter | value or description | example (partial)
--- | --- | ---
[engine] | deepl_api_free, deepl_api_pro, deepl_web, sugoi | `deepl_api_free`
address | a valid network address including the protocol but not the port number | `--address=http://192.168.1.100`
port | a valid port number | `--port=5001`, `--port=8080`, `--port=443`

## Requirements:

Regarding python libraries:
- Different libraries are not all forward/backwards compatible with all major python versions or compatible with this or that version of (various) libraries they import, but they still have to somehow all work together with matching versions on a wide variety of different computers. Does that sound like hell? Well, welcome to software development. So anyway, below are the versions that were tested and developed on while using Python 3.7.6. The user's local enviornment may differ leading to undefined behavior. Have fun.

### Installing and managing python library versions with `pip.exe`:

- `python --version` #Find out what major python version is installed. 3.5, 3.6, 3.7, etc
- `python -m pip install --upgrade pip` #Update pip.
- `pip --version`
- `pip install -r requirements.txt` #Use this command to install a predefined list of libraries. Alternatively:
- `pip install <libraryName>` #Examples:
    - `pip install python3-pandas` #LinuxOnly
    - `pip install openpyxl`
- `pip index versions <libraryName>`  #Use this command to list what versions are available for a library. Requires `pip >= 21.2`. Examples:
    - `pip index versions pandas`
    - `pip index versions deepl`
- `pip install <libraryName>=1.3` #Use this syntax to install a specific library version. Examples:
    - `pip install deepl==1.16.1`
    - `pip install r`
- `pip install --help` #For additional confusion.

Install these libraries. IDK what versions work with what other versions, so just install whatever and hope it works:

- [requests library](//pypi.org/project/requests). Used for HTTP get/post requests. Developed and tested using version: `requests 2.31.0`
- [pandas](//pandas.pydata.org). Used as UI for xls/xlsx/ods/csv conversions. `pip install pandas==1.3.5` Developed and tested using version 1.3.5.
    - For Linux use `python3-pandas`
- numpy - Core pandas dependency. Installed automatically by pip. Developed and tested using version `numpy-1.21.6`
- python-dateutil - Core pandas dependency. Installed automatically by pip. Developed and tested using version `dateutil-2.8.2`
- pytz - Core pandas dependency. Installed automatically by pip. Developed and tested using version `pytz-2023.3.post1`
- openpyxl - Provides engine services to pandas. `pip install openpyxl` Developed and tested using version `openpyxl-3.1.2`
- xlsxwriter - Provides engine services to pandas. `pip install xlsxwriter` Developed and tested using version `xlsxwriter-3.1.9`
- odfpy - Provides engine services to pandas. `pip install odfpy` Developed and tested using version `odfpy-1.4.1`
- DeepL's python library. Required for DeepL NMT. `pip install deepl` Developed and tested using version: `deepl-1.16.1`

### Not python libraries:

- KoboldCPP API requires:
    - CPU/Nvidia GPUs: [KoboldCPP]
    - AMD GPUs: [KoboldCPP-ML]
    - Developed and tested using KoboldCPP_nocuda.exe v1.53 which implements KoboldCPP API v1.
- Sugoi NMT requires Sugoi Translator. Tested using Sugoi Offline 4.0 Translator (part of Sugoi 6.0 Toolkit) and an updated dictionary from here[dictionary pretrained]().
    - Put the library at Sugoi\media\

## Licenses:

- KoboldCPP has their license [here].
- DeepL's [various plans](//www.deepl.com/pro).
- DeepL's [python library](//github.com/DeepLcom/deepl-python) for their API has its own license available [here](//github.com/DeepLcom/deepl-python/blob/main/LICENSE).
- Sugoi has their license [here].
- p3yTranslateLLM is [GNU Affero GPL v3](//www.gnu.org/licenses/agpl-3.0.html).
    - Feel free to use it, modify it, and distribute it to an unlimited extent, but if you distribute binary files of this program outside of your organization, then please make the source code for those binaries available. The imperative to make source code available also applies if using this program as part of a server if that server is publically accessible.


Programs:
####Engine#####
KoboldCPP API (For Mixtral8x)
DeepL API (For DeepL)

Program that sends the CSV/JSON data to KoboldCPP API/DeepL and recieves a response. Reads/writes output to translated.csv, translated.json.
Notes: -DeepL natively supports document files, but only XLSX and .txt files are supported and only through their API, so writing a full parser might be a better idea instead due to having more control over parsing. It is also necessary to write a full parser in order to also support Mixtral8x via KoboldCPP API.
-https://support.deepl.com/hc/en-us/articles/360020582359-Document-formats

Intermediary formats:
Option 1) CSV/DataStructure that has # of lines represented as 2nd column (but no positioning information?), or maybe as 3rd column. Or maybe no positioning information, but the original lines that include \n?
-Or maybe only include original lines (with \n) in column 1
-dynamically compute whether to feed them to translator line-by-line or as a paragraph.
-For replacing, if word wrapping enabled, check if number of translated lines after word wrap matches original.
    -If not and fewer lines, then replace raw data strings in original file with empty strings.
    -If not and more lines, then replace last line with remaining translated lines that includes \n.
-If word wrapping = strict and a mismatch occurs,
    -then... prompt user for mis-matches?
    -Or just output all on one line and let the user deal with it. Print word wrapping mismatch into error log and inform user.
-To create data that goes into first cell of column, go until delimitor is reached or paragraphMaxSize.
    -Line-by-line parsing of raw files can also be enabled so every line of input in source files corresponds to one DB entry.
    -Document this extensively. Line by line parsing => always single line "paragraphs"; line-by-line parsing disabled creates
    -up to maximum
-If word wrapping disabled, then dump contents all into one line. This makes sense for engines that support automatic word wrapping, like Kirikiri or RPG Maker MV/MZ with so-and-so plugin.
    -If using RPG Maker's wrapping system, specify it during launch and instead of inserting \n, insert <br>. Maybe just "use br for word wrapping" option instead?  Replace space with \n normally, replace space with <br>,


Option 2) Or CSV.rawText.csv/Datastructure with only text and a companion file?
Notes:
-In all cases: Might be difficult to associate data with each line if translator returns them in different order or if python data structures (dictionary, json, xml) are used and it processes them in a different order.
-Maybe include total number of lines header at the top (1st row), or as a different file (metadata.txt)?
-Starting in Python 3.7, all dictionaries are ordered. In 3.6, it was required to use an orderedDictionary.
-JSON Objects are unordered. JSON Lists are ordered.

xp3/.ks, json, RPGM parsing software that 1) transfers the lines to CSV/JSON in an ordered way, 2) takes lines from CSV/JSON and inserts them in the appropriate ks/RPGM files. (maybe use a deliminator.settings.txt file?)


Raw Unencrypted Data files (xp3->ks; RPGM files)
####Final/RawData####

Concept Art:
Maybe write 1 program in Python that can take lines from .KS and RPGM files, inserts them into an ordered dictionary (internally), and with that data, it can:
1) translate them using DeepL (free, maybe Pro), KoboldCPP API (specify: DeepL, DeepLPro, KoboldCPP).
2) export raw text as: JSON/CSV. Maybe also support TEXT(?)/XLSX(?)
Maybe use Pandas.read_excel (supports OpenDocument odf/ods, and MS Document .xls/xlsx)
3) export translated text as above formats (containing both raw text, only translated text, or with everything+metadata)
4) 

Use cases/Interface:
-debug flag, prints all inputs and outputs
Files to input/output:
) -Input: raw file to import from .ks
) -Input/Output: template.parser.txt file to use as a template for parsing entries
) -Input/Output: specially formated CSV file that has raw output parsed data (should be entirely JPN, with # of lines input represents and other metadata())
-optional: outputRaw filename (just name output automatically, and export as raw.untranslated.csv
    -optional: outputRaw outputfile type (maybe get from extension?)

-raw.untranslated.csv from previously parsed .ks or other text file
2) 
-optional: outputTranslated filename (just name output automatically, and export as translated.csv, which is actually just untranslated.csv but with an extra column
    -optional: outputTranslated outputfile type (maybe get from extension?)
-optional: outputTranslated filename (just name output automatically, and export as translated.csv, which is actually just untranslated.csv but with an extra column
    -optional: outputTranslated outputfile type (maybe get from extension?)


address of koboldCPPServerAddress
address of koboldCPP_APIPath relative to server path
address of fullKoboldCPP_APIPath path to Kobloid CPP server API, including underlings
-Dry run... translate first 5-10 entries or so and output to console.
-Dictionary (only valid for DeepL Pro), so maybe not.
Parse Raw Data (Shift-JIS; UTF-16 BOM LE) + Export csv/json/txt/xlsx/ods
-Context= number of previous translated lines to include
    -historySize; default=10 entries  (might need to be split into rawHistorySize and translatedHistorySize internally)


Raw Data Parser (in Python) for .ks:
-Specifiy which lines to ignore.
-Specify end of "paragraph" delimitor. (none=every line is 1 entry,specified as newLine=same as none; specify as empty line or other delimitor means keep adding to existing); Must have maximum "paragraph length", 5(?).
-Does the document include character names?
-At the start or end? 
-If document includes replaceable character names, specify them: Example text file [%MDLS]=SoAndSo or [＠クロエ]=[＠クロエ]; 
--How should padding be handled? Completely ignored or user specified? Could also try an auto mode that figures it out, like if it appears at the start of the line do not add a leading space, add an ending space if a punctuation mark is not after the replacement.
Maybe: Create a ks.parser.template.txt file so user can fill it in? Entering input using console does not work due to lack of UTF-8 support.
Requirements: -Must also support importing from json/csv; likely also xlsx/ods can be supported easily.

