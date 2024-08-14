# py3TranslateLLM.py

py3TranslateLLM.py uses Artificial Intelligence (AI) to translate files.

The focus is on producing the highest quality local [Large Language Model (LLM)](//en.wikipedia.org/wiki/Large_language_model) translations possible, but there is also support for batches using [Neural Machine Translation (NMT)](//en.wikipedia.org/wiki/Neural_machine_translation) models and certain cloud translation APIs.

More specifically, this Python program is a CLI wrapper for the following translation engines:

- [KoboldCpp](//github.com/LostRuins/koboldcpp) [API](//lite.koboldai.net/koboldcpp_api).
- [py3translationServer](//github.com/gdiaz384/py3translationServer).
- [pykakasi](//codeberg.org/miurahr/pykakasi).

And provides interoperability for the following formats:

- Comma separated value (.csv).
- Open Office XML (.xlsx).
- Plain text.

## Support is planned for:

- These translation engines:
    - [DeepL API (Free)](//www.deepl.com/pro-api).
    - DeepL API (Pro).
    - Sugoi Offline Translator from Sugoi Toolkit v4-9.
- These file formats:
    - Microsoft Excel 97/2000/XP/2003 (.xls).
    - OpenDocument spreadsheet (.ods).
- Generic OpenAI compatible web servers.
    - Example: https://github.com/vllm-project/vllm
- Certain cloud based NMT translation engines: Google Translate, Google Cloud NMT, Bing Translate, Microsoft Azure NMT, Yandrex, etc.
    - Use software like [this](//github.com/JustFrederik/aiotranslator) for now.

Not Planned:

- Microsoft Excel 95 (.xls).
    - This might end up being supported anyway.
- Sugoi's DeepL, Sugoi Translator Premium, Sugoi Papago.
- Parsing arbitrary file types. Only spreadsheets and plain text files are natively supported.
    - To support arbitrary input (.doc, .srt, .epub, .ks, .json) see [Regarding Scope](#regarding-scope) for help converting arbtrary data types.

Undetermined:

- Which cloud based LLMs py3TranslateLLM should incorporate.
    - Which ones that can be used for translation are expected to be long lived and have unlimited use APIs?
    - Or is web hooking any of them worthwhile?
- OpenAI's GPT. For now, consider:
    - [DazedMTL](//github.com/dazedanon/DazedMTLTool) - Supports OpenAI's LLM models like v3.5 Turbo, v4.0 Turbo, GPT-4o.
- py3TranslateLLM should (unofficially) work on older Python versions like 3.4.
    - Older than 3.7 is tricky because dictionaries became ordered in 3.7 and the order might be important for cache, especially cache.rebuildCache().
    - Older than 3.4 might be tricky because:
        - `pathlib`, which contains `Path` that is used by py3TranslateLLM to create folders, was not included in the Python standard library before 3.4.
            - The exist_ok parameter was not added to pathlib.Path().mkdir() until 3.5.
        - Same with `pip`.
        - 3.4 already requires using an older `openpyxl` version. Using even older versions might incorporate even more already fixed bugs.
        - It is unlikely any `deepl-python` version that supports 3.4 still works with DeepL's contemporary API.
        - Minor: The `chardet` library requires 3.7+.
            - Minor because that library is optional and text encodings should always be in utf-8 or manually specified anyway.

## What are the best LLM models available?

- https://artificialanalysis.ai
- Guide: huggingface's [chatbot-arena-leaderboard](//huggingface.co/spaces/lmsys/chatbot-arena-leaderboard). Examples:
    - [Mixtral 8x7b v0.1](//huggingface.co/TheBloke/Mixtral-8x7B-v0.1-GGUF).
    - [Yi-34B-Chat](//huggingface.co/TheBloke/Yi-34B-Chat-GGUF).
    - [Tulu-2-DPO](//huggingface.co/TheBloke/tulu-2-dpo-70B-GGUF).
    - Google's [Gemma](//huggingface.co/collections/google/gemma-release-65d5efbccdbb8c4202ec078b).
    - Random: [Japanese StableLM Instruct Gamma 7B](//huggingface.co/TheBloke/japanese-stablelm-instruct-gamma-7B-GGUF).
- Notes:
    - The size of the model is also the RAM requirements to load it into memory.
    - The more it fits into GPU memory (VRAM), the better the performance.
    - Not all models listed on leaderboard are compatible with KoboldCpp. See KoboldCpp's [documentation](//github.com/LostRuins/koboldcpp/wiki) for compatible model formats.

## Installation guide

`Current version: 2024.08.01-alpha`

Warning: py3TranslateLLM is currently undergoing active development. The project in the alpha stages. Alpha means core functionality is currently under development.

1. Install [Python 3.7+](//www.python.org/downloads). For Windows 7, use [this repository](//github.com/adang1345/PythonWin7/).
    - Make sure the Python version matches the architecture of the host machine:
        - For 64-bit Windows, download the 64-bit (amd64) installer.
        - For 32-bit Windows, download the 32-bit installer.
    - During installation, make sure `Add to Path` is selected.
    - Open an command prompt.
    - `python --version` #Check to make sure Python 3.7+ is installed.
    - `python -m pip install --upgrade pip` #Optional. Update pip, python's package manager program.
1. Download py3TranslateLLM using *one* of the following methods:
    1. Download the latest project archive:
        - Click on the green `< > Code` button at the top -> Download ZIP.
    1. Git:  #Requires `git` to be installed.
        1. Open an administrative command prompt.
        2. Navigate to a directory that supports downloading and arbitrary file execution.
        3. `git clone https://github.com/gdiaz384/py3TranslateLLM`
    1. Download from last stable release:
        - Click on on "Releases" at the side (desktop), or bottom (mobile), or [here](//github.com/gdiaz384/py3TranslateLLM/releases).
        - Download either of the archive formats (.zip or .tar.gz).
1. If applicable, extract py3TranslateLLM to a directory that supports arbitrary file execution.
1. Open an administrative command prompt.
1. `cd /d py3TranslateLLM`  #change directory to enter the `py3TranslateLLM` folder.
6. `pip install -r resources/requirements.txt`
6. `pip install -r resources/optional.txt`
7. `python py3TranslateLLM.py --help`

Install/configure these other projects as needed:

- DeepL:
    - [DeepL API](//www.deepl.com/pro?cta=header-pro) support is implemented using their [Python library](//pypi.org/project/deepl).
        - It can be installed with:
            - `pip install -r resources/requirements.txt` or separately with:
            - `pip install deepl`
        - Usage of the DeepL API, both Free and Pro, requires an [account](//www.deepl.com/login) and credit card verification.
        - For the DeepL API, an API key is needed. It must be in one of the following places:
            - TODO: Put stuff here.
    - [DeepL Web](//www.deepl.com/translator) and DeepL's [native clients](//www.deepl.com/en/app) do not seem to have usage limits, and the Windows client at least does not require an account. They might do IP bans after a while.
    - All usage of DeepL's translation services and is governed by their [Terms of Use](//www.deepl.com/en/pro-license).
- LLM support is currently implemented using the KoboldCPP's API which requires KoboldCPP:
    - CPU/Nvidia GPUs: [KoboldCPP](//github.com/LostRuins/koboldcpp), [FAQ](//github.com/LostRuins/koboldcpp/wiki).
    - AMD GPUs: [KoboldCPP-ROCM](//github.com/YellowRoseCx/koboldcpp-rocm).
    - Developed and tested using `KoboldCPP_nocuda.exe` v1.53 which implements KoboldCPP API v1.
- [fairseq](//github.com/facebookresearch/fairseq) is a library released by Facebook/Meta for data training.
    - Sugoi NMT is a wrapper for fairseq that comes preconfigured with a Japanese->English dictionary.
    - To install and use fairseq outside of Jpn->Eng translation, refer to fairseq's [documentation](//fairseq.readthedocs.io/en/latest) and obtain an appropriately trained model.
- Sugoi NMT only does Jpn->Eng translation. It requires Sugoi Offline Translator which is part of the [Sugoi Toolkit](//sugoitoolkit.com).
    - DL: [here](//www.patreon.com/mingshiba/about) or [here](//archive.org/search?query=Sugoi+Toolkit).
    - Reccomended: Remove some of the included spyware.
        - Open: `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\main.js`
        - Comment out `/*  */` or delete the analytics.
    - Tested using Sugoi Offline Translator 4.0 which is part of Sugoi Toolkit 6.0-8.0+.

## Usage:

`TODO:`
```
Syntax for executable file (.exe):
    py3TranslateLLM.exe [options]
Syntax for Python3 script (.py):
    python py3TranslateLLM.py [options]
    python3 py3TranslateLLM.py [options]

Usage:
py3TranslateLLM --help
py3TranslateLLM -h
py3TranslateLLM koboldcpp --address=http://192.168.1.100 --port=5001
py3TranslateLLM deepl_api_free [options]
py3TranslateLLM deepl_api_pro [options]
py3TranslateLLM deepl_web [options]
py3TranslateLLM sugoi [options] #sugoi is an alias for fairseq
py3TranslateLLM fairseq [options]
```
 
### Parameters

TODO: This section.

Parameter | Description | Example(s)
--- | --- | ---
`-mode`, `--translationEngine` | The engine used for translation. Use `parseOnly` to read from source files but not translate them. | `parseOnly`, `koboldcpp`, `deepl-api-free`, `deepl-api-pro`, `deepl-web`, `py3translationserver`, `sugoi`
`-a`, `--address` | A valid network address including the protocol but not the port number. | `--address=http://192.168.1.100`, `-a=http://localhost`
`--port` | The port number associated with the `--address` listed above. | `--port=5001`, `--port=8080`, `--port=443`

### The following files are required:

Variable name | Description | Examples
--- | --- | ---
`fileToTranslate` | The file to translate. Should be a spreadsheet or a plaintext.txt. | `myFile.txt`, `mySpreadsheet.xlsx`
`languageCodesFile` | Contains the list of supported languages. | `resources/ languageCodes.csv`

### The following files are optional:

Variable name | Description | Examples
--- | --- | ---
`py3TranslateLLM.ini` | This file may be used instead of the CLI to specify input options. Keys in the key=value pairs are case sensitive. | `py3TranslateLLM.ini`, `renamedBinary.ini`
`parsingSettingsFile` | Defines how to read and write to `fileToTranslate`. Not required if working only with spreadsheet formats but required if reading from or writing to text files. | `resources/ templates/ KAG3_kirikiri_parsingTemplate.txt`
`outputFile` | The name and path of the file to use as output. Will be same as input if not specified. Specify a spreadsheet format to dump the raw data or a text file to output only the preferred translation. | `None`, `output.csv`, `myFolder/ output.xlsx`
`promptFile` | This file has the prompt for the LLM. Only needed if using an LLM. | `resources/ templates/ prompt.Mixtral8x7b.example.txt`
`revertAfterTranslationDictionary` | Entries will be submitted to the translation engine but then replaced back to the original text after translation. | `resources/ templates/ characterNamesDictionary_example.csv`
`preTranslationDictionary` | Entries will be replaced prior to submission to the translation engine. | `preTranslationDictionary.csv`
`postTranslationDictionary` | Entries will be replaced after translation. | `postTranslationDictionary.csv`
`postWritingToFileDictionary` | After the translated text has been written back to a text file, the file will be opened again to perform these replacements. | `postWritingToFileDictionary.csv`
`sceneSummaryPrompt` | Experimental feature. This file has the prompt used to generate summaries using an LLM. Using this disables translation. | `sceneSummaryPrompt.txt`

### Keyword replacements for LLMs:

- LLMs supports many different sources of information when translating text. However, since much of this information is dynamic, known only at runtime, or constantly changing, py3TranslateLLM supports replacing certain {keywords} in the instructions to the LLM at runtime. This should ensure the highest quality translation possible while also supporting a very large degree of automation by making it possible to use the same set of LLM instructions, `prompt.txt`, `memory.txt`, and `sceneSummary.txt`, for an entire dataset.
- LLM translations always require a `prompt.txt`.
    - `prompt.txt` should include the main instructions to the LLM, e.g. translate this text, as well as examples to help the LLM understand how to format the desired output. See resources\templates\* for examples.
    - Guides:
        - Microsoft's [prompt engineering guide](//learn.microsoft.com/en-us/ai/playbook/technology-guidance/generative-ai/working-with-llms/prompt-engineering).
        - Nvidia's [developer blog LLM introduction](//developer.nvidia.com/blog/an-introduction-to-large-language-models-prompt-engineering-and-p-tuning/).
    - Examples:
        - https://github.com/0xeb/TheBigPromptLibrary
        - https://github.com/langgptai/awesome-llama-prompts
        - [resources/templates](resources/templates)
- To optionally improve translation quality, it is also recommended to always use `memory.txt`.
    - `memory.txt` should include background information that may or may not be directly relevant to the immediate translation. Examples include a description of the source content (e.g. story, dialogue, novel, subtitles, game), translations for character names, information about the characters and their relationships to one another, and a description of what is happening in the scene currently being translated.
- Experimental Feature: To optionally improve translation quality, consider using `sceneSummary.txt`.
    - `sceneSummary.txt` is a `prompt.txt` with instructions to generate a summary of the current scene being translated so that summary can be inserted into `prompt.txt` and/or `memory.txt` prior to translating individual lines.
- Keywords:

Variable | Scope | Description
--- | --- | ---
`{untranslatedText}` | prompt.txt | The current line prior to translation.
`{sourceLanguage}` | All | The source language specified at the command prompt. The literal text is the first entry in `languageCodes.csv`.
{targetLanguage} | All | The target language specified at the command prompt. The literal text is the first entry in `languageCodes.csv`.
`{history}` | prompt.txt | The rolling history buffer of previously untranslated/translated entry pairs. This gets formatted according to the LLM instruction type: chat, instruct, autocomplete.
`{scene}` | sceneSummary.txt | The current batch of untranslated lines to use when generating a summary.
`{scene}` | prompt.txt, memory.txt | The summary generated from the current untranslated lines.

Note: If the data inserted in the above variables is not formatted properly for a given model, especially `{history}`, then update the code at engine.py appropriately or [open an issue] to request support for a specific LLM model.

## Release Notes:

- [This xkcd](//xkcd.com/1319) is my life.
- Backups of the imported data are written to backups/[date]/* prior to data processing. Use `--backups`, `-bk` to disable this feature.
- If interrupted, translated entries are still available in the local cache. Running the same command as-is will therefore skip previously translated data starting from the last time cache was written to disk.
    - Alternatively, use one of the backup files created under backups/[date]/* to continue with minimal loss of translated data. Resuming from save data in this folder after interruptions is not automatic. Technically `--resume` (`-r`) exists for this reason, but only backup files with today and yesterday's date are checked.
- The second column in the spreadsheets is reserved for the speakerName of the current line. If present, the speakerName is automatically used for LLM translations.
- By default, backups of fileToTranslate are made at most once every 9 minutes. To alter this behavor change `defaultMinimumSaveIntervalForMainSpreadsheet` in `py3TranslateLLM.py`.
- By default, cache is written at most once every 5 minutes. To alter this behavior change `defaultMinimumSaveIntervalForCache` in `py3TranslateLLM.py`.
- By default, sceneSummaryCache is written at most once every 5 minutes. To alter this behavior change `defaultMinimumSaveIntervalForSceneSummaryCache` in `py3TranslateLLM.py`.
- Settings can be specified during runtime from the command prompt/terminal/CLI and/or using `py3TranslateLLM.ini`. See __Regarding Settings Files__ for more information.
- Aside: LLaMA stands for Large Language Model Meta AI. [Wiki](//en.wikipedia.org/wiki/LLaMA).
    - Therefore [Local LLaMA](//www.reddit.com/r/LocalLLaMA) is about running AI on a local PC.

#### Known Bugs:

- Many features have not been implemented yet.
- Most features have not been tested yet.

### Concept art:

- The design concept behind pyTranslateLLM is to produce the highest quality machine and AI translations possible for dialogue and narration by providing NMT and LLM models the information they need to translate to the best of their ability. This includes but is not limited to:
    - Bunding the untranslated language strings into paragraphs to increase the context of the translated text.
    - For LLMs and DeepL, providing them with the history of previously translated text to ensure proper flow of dialogue.
    - For LLMs and DeepL, identifying any speakers by name, sex and optionally other metrics like age and occupation.
    - For LLMs and DeepL, providing other arbitrary bits of information in the prompt.
    - Supporting dictionaries that allow removing and/or substituting strings that should not be translated prior to forming paragraphs and prior to submitting text for translation. Examples in-line text that should be removed or altered: [＠クロエ] [r] [repage] [heart].
        - This should help the LLM/NMT understand the submitted text as contiguous 'paragraphs' better.
        - Tip: To automate this, use [escapeLibrary.py] during parsing.
- Other translation techniques omit one or all of the above. Providing this information _should_ dramatically increase the translation quality when translating languages that are heavily sensitive to context, like Japanese, where much or most of the meaning of the language is not found in the spoken or written words but rather in the surrounding context in which the words are spoken.
    - Aside: For Japanese in particular, context is very important as it is often the only way to identify who is speaking and whom they are talking about.
- **If translating from context light languages, like English where most of the meaning of the language is found within the language itself, then there should not be any or only small differences in translation quality**. For such languages, use a translation engine that supports batch translations for the maximum possible speed.
- In addition, substution dictionaries are supported at every step of the translation workflow to fine tune input and output and deal with common mistakes. This should result in a further boost in translation quality.
- The intent is to increase the productivity of translators by cutting down the time required for the most time consuming aspect of creating quality dialogue translations, the editing phase, by providing the highest quality MTL baseline possible from which to start editing and providing multiple translation engines for easy cross referencing.
- This program was written as part of a workflow meant to complement other automated parsing and script extraction programs meaning that compatibility with such programs and openness required to adjust workflows as needed are part of the core design concept.

### Regarding Scope

- This program focuses on translating dialogue that has been input into spreadsheets.
- Other programs can be used to find and parse small bits of untranslated text in text files and images and handle how to reinsert them.
- While it is not the emphasis of this program, submitting translations in batches to some NMT models is also supported.
- While it is not the emphasis of this program, there is some code to help translate plain.txt files. This only works in line-by-line mode.
- For more complicated input, parse the output using a parsing program that can convert it to a spreadsheet format, like .csv, before using py3TranslateLLM. Examples:
    - [py3AnyText2Spreadsheet](//github.com/gdiaz384/py3AnyText2Spreadsheet). Supports parsering many common formats via templates but intended more for DIY non-regex parsing.
    - [SExtractor](//github.com/satan53x/SExtractor). Supports regex.
    - [fileTranslate](//github.com/UserUnknownFactor/filetranslate). Supports regex.
    - Consider writing a parser yourself. Assuming plain text files, it should not take more than an afternoon to write a parser in Python due to Python's very large standard library, [available templates], and a very large amount of third party libraries readily availble on [PyPi.org](pypi.org).
        - Tip: After parsing, use [pyexcel](//github.com/pyexcel/pyexcel), [documentation](//docs.pyexcel.org/en/latest/design.html) or [chocolate.py] to export the data to and out of spreadsheets easily. 
        - pyexcel and chocolate are wrapper libraries for openpyxl and other libraries that focuses on providing i/o or data structure manipulation for the various spreadsheet formats.
            - Note that pyexcel has a plugin system for various formats and requires those plugins to also be installed in addition to the implemented base libraries. See their [installation](//github.com/pyexcel/pyexcel#installation) section for a lack of guidance on how to install them.

### Regarding the Spreadsheet Formats:

- py3TranslateLLM uses spreadsheets for its internal data structures. LibreOffice and other spreadsheet manipulation programs can be used to read/write them directly. For more information, see: "Regarding Open Office XML".
- For the spreadsheet formats, .csv, .xlsx, .xls, .ods, the following apply:
    - The first row, 1st, is reserved for headers and is always ignored for data processing otherwise.
    - The first column is reserved for the source content for translation.
    - Multiple lines within a cell for the first column, called 'paragraphs,' are allowed.
        - New lines will not be preserved in the output cell. If this behavior is desired, regenerate them dynamically when writing to the output files as needed. Word wrap is outside the scope of this project.
    - The second column, 2nd, is reserved for the character speaking.
        - Feel free to add the speaker if a speaker could not be automatically determined during parsing.
    - The third column, 3rd, and columns after it are used for metadata or the translation engines. Currently that is KoboldCpp, DeepL API Free, DeepL API Pro, py3translationServer, Sugoi.
        - Label the first cell in a column to reserve that column for that translation engine. One translation engine per column.
        - To reserve it for metadata, call it `metadata` or similar.
        - If the current translation engine does not exist as a column, then it will be added dynamically as needed.
            - KoboldCPP translation engines are in the format `koboldcpp/[modelName]`, therefore changing the model mid-translation will result in a completely new column because different models produce different output.
            - py3translationServer columns are in the format py3translationServer/[modelName] which can result in a completely new column when gaming models because different models produce different output.
                - For CTranslate2, the model name sometimes takes the form py3translationServer/model.bin if the model.bin file was explicitly used when invoking py3translationServer. This behavior can result in collisions between different models and potentially different languages as well. As a workaround, if using py3translationServer +  CTranslate2, then specify loading the model by using the folder name of the model instead and name the folder in a descriptive way.
                - Example: `b100_model/model.bin` and invoke using `b100_model` only.
                - This behavior of py3translationServer may change in the future.
        - The order of the translation engine columns (4+) only matters when writing back to files (.txt). The column furthest to the right will be preferred.
- .csv files:
    - Must use a comma `,` as a delimiter.
    - Entries containing:
        - new line character(s) `\n`, `\r\n` 
        - comma(s) `,`
        - must be quoted using two double quotes `"`. Example: `"Hello, world!"`
    - Single quotes `'` are not good enough. Use double quotes `"`
    - Entries containing more than one double quote `"` within the entry must escape those quotes.
        - Use a backlash `\` like: `"\"Hello, world!\""`
        - Or use double quotes `""` like: `"""Hello, world!"""` TODO: Test this.
    - Whitespace is ignored for `languageCodes.csv` and for .csv's that contain the untranslated text.
    - Whitespace is preserved for all of the dictionaries.
- .xls is quite old and supports a maximum of ~65,000 rows, which is relatively small. [Source](//github.com/pyexcel/pyexcel-xls#warning). Consider using any other format.
    - Microsoft's [documentation](//learn.microsoft.com/en-us/previous-versions/office/developer/office-2010/gg615597(v=office.14)).

### Regarding Settings Files:

- Settings read from the command prompt take priority over what is specified in the `.ini` text file.
- By default, the name of the program without an extension + `.ini` is used to determine the name of the settings.ini file from which to read settings. Example: pyTranslateLLM.ini
- This file can also specified manually at the CLI during runtime by using `--settingsFile`, `-sf`.
- Values in the settings.ini file are designated using the following syntax:
    - `commandLineOption=value`
    - The 'None' keyword for an option indicates no value. Example: `preTranslationDictionary=None`
    - Whitespace is ignored.
    - Lines with only whitespace are ignored.
    - Lines starting with `#` are ignored. In other words, `#` means a comment.
    - Keys in the key=value pairs are case sensitive.
    - Keys in the key=value pairs must match the command line options exactly or will be interpreted as user-defined custom values.
    - See: `py3TranslateLLM --help` and the **Parameters** enumeration below for valid values.
- The text formats used for settings.ini (.ini .txt) have their own syntax:
    - `#` indicates that line is a comment.
    - Values are specified by using `item=value` Example:
        - `paragraphDelimiter=emptyLine`
    - Empty lines are ignored.
- TODO: Update this part.
- For the text formats used for input (.txt, .ks, .ts), the inbuilt parser will use the user provided settings file to parse the file.
    - A settings file is required when parsing such raw text files.
    - Examples of text file parsing templates can be found under `resources/templates/`.

### Regarding the Various Dictionaries:

-  There are a lot of dictionary.csv files involved. Understanding the overall flow of the program should clarify how to use them:
    1. All input files besides `fileToTranslate` are read and parsed.
    1. The data structure that holds both the untranslated and translated text while the program is working is called `mainSpreadsheet`. How it is created is handled differently depending upon if `fileToTranslate` is a spreadsheet or a text file. For spreadsheets:
        1. If `fileToTranslate` is a spreadsheet, .csv, .xlsx, .xls, .ods, .tsv, it is converted to `mainSpreadsheet` as-is. See above for the formatting guidelines.
    1. If `fileToTranslate` is not a spreadsheet, it is treated as a text file:
        1. The lines in the text file are read in as-is line-by-line without any parsing logic.
            - To parse the text file in a more complicated way, use [py3AnyText2Spreadsheet](//github.com/gdiaz384/py3AnyText2Spreadsheet).
    1. The process to translate the first column, 'A', in `mainSpreadsheet` using a particular translation engine begins. Examples: koboldcpp, deepl_api_free, deepl_api_pro, deepl_web, py3translationServer, sugoi.
        1. If the paragraph is present in `cache.xlsx`, it is translated using the cache file and the translation process skips to step 7/step g.
        1. If present, `revertAfterTranslationDictionary` is considered and replacements are performed.
        1. If present, `preTranslationDictionary` is considered and replacements are performed.
        1. The paragraph is submitted to the translation engine.
            - If context history is enabled, the translated paragraph is added to context history for subsequent translations.
        1. If present, `revertAfterTranslationDictionary` is considered to revert certain changes.
        1. The untranslated line and the translated line are added to the `cache.xlsx` file as a pair.
        1. If present, `postTranslationDictionary` is considered to alter the translation further.
        1. The translated paragraph is written to `mainSpreadsheet` in the column for the current translation engine.
        1. Periodically as entries are translated, a backup.xlsx is made under `backups/[date]/`.
    1. The spreadsheet file, .xlsx,  is written to output.
    1. For text file and .csv output only, `postWritingToFileDictionary` is considered. This file is intended to fix encoding errors when doing baseEncoding -> unicode -> baseEncoding conversions since codec conversions are not lossless.

#### Regarding revertAfterTranslation.csv:

- The `revertAfterTranslation.csv` dictionary is not a perfect solution to the problem it was intended to solve.
- The actual functionality is as follows:
    1. Entries in the first column of this dictionary will be replaced with the entries for the second column prior to text getting translated.
    1. After the translated text returns, every entry matching the second column will be replaced back to the text in the first column.
    1. If there is no entry in the second column, not even whitespace, then step 2/step b will be skipped and the text in the first column will simply be removed prior to translation.
- Background:
    - This dictionary was originally conceived from the notion that some dialogue scripts have entries like `[＠クロエ]`, `\N[1]`, `\N[2]` that represent replacable character names within the dialogue. The idea being the player gives a custom name to a character and the game engine will replace these placeholders that are within the dialogue with the chosen name during runtime.
    - These placeholders, in essence, contain the true names of characters, so they have relevant information that should be considered when translating paragraphs. However, they do not contain that information while they are just placeholders. In addition, they should also be left untranslated in the final text to retain the original functionality of the placeholder.
    - On a technical level, if left as-is, then in addition to not being allowed to consider the information they contain, these placeholders can also often distort the resulting translation because translation engines might split a paragraph into two fragments based upon the `[ ]`, especially fairseq/Sugoi. The translation engine might also change the placeholder in such a way as to cause the game engine to overtly crash.
    - Thus, the idea of the `revertAfterTranslation.csv` dictionary was conceived. The idea is to specify that `[＠クロエ]` is `Chloe` during translation but revert `Chloe` back to `[＠クロエ]` after translation. This idea lead to the functionality described above getting integrated into py3TranslateLLM. However, this approach has a number of problems.
- Problems:
    - There is no gurantee that the translation engine will preserve the entries in the second column, e.g. leave `Chloe` as `Chloe`. If it changes the name of the character in any way, like using a pronoun, then there is no way to revert the substitution.
    - The untranslated line now contains two languages.
        - This will almost certainly mess with the translation engine's logic in unintended ways.
        - This also creates uncertainty in how specifying a source language should be handled. Not specifying the source language all is asking for a lot of unrelated problems to crop up but specifying one source language is technically wrong because there are now two languages in the source text.
        - However, leaving the name in the source language in the untranslated form `クロエ` to prevent a mixed language scenario will almost certainly cause the translation engine to mess up when it translates it different ways based upon the source context changing constantly. Sugoi NMT especially does this a lot.
    - One not automated solution is to replace the substitution string `[＠クロエ]` with the name in the source language `クロエ` to prevent multiple languages from in the source text. Then tell the translation engine to explcitly translate that name/string of characters a very specific way `Chloe` using a translation engine specific dictionary. And finally, revert the translation back to the original substitution string after translation by the translation engine.
    - This can be done in py3TranslateLLM by:
        1. Specifying an entry in the `preTranslation.csv` dictionary to remove the [ ] and add the actual name in the source language: `[＠クロエ]` -> `クロエ`.
        1. Tell the LLM translation engine to translate the name a specific way using the `prompt.txt` file or a DeepL dictionary `クロエ` -> `Chloe`.
            - Note: DeepL dictionaries are not currently implemented in py3TranslateLLM.
        1. Specifying an entry in the `postTranslation.csv` dictionary to revert back the translated text to the original placeholder text used by the game engine: `Chloe` -> `[＠クロエ]`.
    - At this time, it is not clear which approach is 'better' because the 'problems' with the `revertAfterTranslation.csv` dictionary approach are entirely hypothetical and so might be non-existent for a particular translation engine.

### Regarding DeepL:

- DeepL has quite a few quirks:
- DeepL's [support page](//support.deepl.com/hc).
- Certain languages, like Chinese, English, and Portuguese, have regional variants.
- DeepL is picky about the target English dialect based upon the source language.
- But yet, language dictionaries can be used with any dialect of that language (TODO: double-check this).
- DeepL's [API Free](//support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-Free) vs Pro plans.
    - The formal vs informal feature is only available for Pro users, so not available for the deepl-api-free or deepl-web translation engines. [About-the-formal-informal-feature](//support.deepl.com/hc/en-us/articles/4406432463762-About-the-formal-informal-feature).
- If translating to Japanese, not from, then read DeepL's [plain vs polite feature](//support.deepl.com/hc/en-us/articles/6306700061852-About-the-plain-polite-feature-in-Japanese).

### Notes about languages:

- The default list of supported languages can be found at `resources/languageCodes.csv`.
- If using an LLM for translation and utilizing a language not listed in `languageCodes.csv`, then add that language as a new row to make py3TranslateLLM aware of it. This file is subject to change without notice.
- The default supported languages list is based on DeepL's [supported languages list](//support.deepl.com/hc/en-us/articles/360019925219-Languages-included-in-DeepL-Pro) and their [openapi.yaml](//www.deepl.com/docs-api/api-access/openapi) specification.
- py3TranslateLLM uses mappings based upon [this](//www.loc.gov/standards/iso639-2/php/code_list.php) table and supports any of the following to specify a language:
    1. The full language name in English: `English`, `German`, `Spanish`, `Russian`.
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

### Regarding Open Office XML

- [Open Office XML](//en.wikipedia.org/wiki/Office_Open_XML) (OOXML), .xlsx, is the native format used in py3TranslateLLM to store data internally during processing and should be the most convenient way to edit translated entries and the cache directly without any unnecessary conversions that could introduce formatting bugs.
- Here are some free and open source software ([FOSS](//en.wikipedia.org/wiki/Free_and_open-source_software)) office suits that can read and write Open Office XML and the other spreadsheet formats (.csv, .xls, .ods):
    - [LibreOffice](//www.libreoffice.org). [License](//www.libreoffice.org/about-us/licenses) and [source](//www.libreoffice.org/download/download-libreoffice/).
    - [OnlyOffice](//www.onlyoffice.com/download-desktop.aspx) is [AGPL v3](//github.com/ONLYOFFICE/DesktopEditors/blob/master/LICENSE). [Source](//github.com/ONLYOFFICE/DesktopEditors).
    - Apache [OpenOffice](//www.openoffice.org). [License](//www.openoffice.org/license.html) and [source](//openoffice.apache.org/downloads.html). Note: Can read but not write to .xlsx.
- [OpenPyXL](//openpyxl.readthedocs.io), the library used in the core data structure for this program, follows the Open Office XML standard closely, and [will not load](//openpyxl.readthedocs.io/en/stable/tutorial.html#errors-loading-workbooks) documents that do not follow the same standard closely.
    - In other words, Microsoft Office will probably not work. If using Microsoft Excel, then export as .ods, .xls, or .csv instead. For Excel .csv files, specify the option... TODO: this part.
    - See Microsoft's [documentation](//learn.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/2c5dee00-eff2-4b22-92b6-0738acd4475e) for why their software does not work correctly.

### Text Encoding and py3TranslateLLM:

- Read the [Text Encoding](//github.com/gdiaz384/py3TranslateLLM/wiki/Text-Encoding) wiki entry.
    - After reading the above wiki entry, the rest of this section should make more sense.
- Tip: Use `py3TranslateLLM.ini` to specify the encoding for text files used with `py3TranslateLLM.py`.
- For compatability reasons, data gets converted to binary strings for stdout which can result in the console sometimes showing utf-8 hexadecimal (hex) encoded unicode characters, like `\xe3\x82\xaf\xe3\x83\xad\xe3\x82\xa8`, especially with `debug` enabled. To convert them back to non-ascii chararacters, like `クロエ`, dump them into a hex to unicode converter.
    - Example: [www.coderstool.com/unicode-text-converter](//www.coderstool.com/unicode-text-converter)
    - Example: If the local console or Python IDE supports utf-8, then it can also be displayed properly after decoding the string in Python:
        - Start a command prompt or terminal.
        - `python`
        - `string=b'\xe3\x82\xaf\xe3\x83\xad\xe3\x82\xa8'`
        - `string.decode('utf-8')`
        - ctrl + z
- Some character encodings cannot be converted to other encodings. When such errors occur, use the following error handling options:
    - [docs.python.org/3.7/library/codecs.html#error-handlers](//docs.python.org/3.7/library/codecs.html#error-handlers), and [More Examples](//www.w3schools.com/python/ref_string_encode.asp) -> Run example.
    - The default error handler for input files is `strict` which means 'crash the program if the encoding specified does not match the file perfectly'.
    - On Python >= 3.5, the default error handler for the output file is `namereplace`.  This obnoxious error handler:
        - Makes it obvious that there were conversion errors.
        - Does not crash the program catastrophically.
        - Makes it easy to do ctrl+f replacements to fix any problems.
            - Tip: Use `postWritingToFileDictionary` or [py3stringReplace](//github.com/gdiaz384/py3stringReplace) to automate these ctrl+f replacements.
    - If there are more than one or two such conversion errors per file, then the chosen file encoding settings are probably incorrect.
- If the [chardet](//pypi.org/project/chardet), [charamel](//pypi.org/project/charamel), or [charset-normalizer](//pypi.org/project/charset-normalizer) libraries are available, they will be used to try to detect the character encoding of files via heuristics. While heuristics are an imperfect solution and obviously very error prone, it is still better than nothing.
    - To make the above libraries available, install at least one using `pip`:
        - `pip install chardet`
        - `pip install charamel`
        - `pip install charset-normalizer`
    - Priority is chardet > charamel > charset-normalizer.
    - If none of the above are available, then everything is assumed to be `utf-8` unless otherwise specified.
    - Note that support for `charamel` and `charset-normalizer` has not actually been implemented yet (2024-07-09).

## Regarding Python libraries:

- Reccomended: If you do not want to deal with this, then use a binary file in the [releases](//github.com/gdiaz384/py3TranslateLLM/releases) page instead.
- py3TranslateLLM was developed on Python 3.7.
- deepl-python is going to start requiring Python 3.8+ in 2024 because ???.
- It is not necessarily clear what versions work with what other versions, in part due to the shenanigans of some developers creating deliberate incompatibilities, so just install whatever and hope it works.
- In addition to the libraries listed below, py3TranslateLLM also uses several libraries from the Python standard library. See source code for an enumeration of those.

Library name | Required, Recommended, or Optional | Description | Install command | Version used to develop py3TranslateLLM
--- | --- | --- | --- | ---
[openpyxl](//pypi.python.org/pypi/openpyxl) | Required. | Used for main data structure and Open Office XML (.xlsx) support. | `pip install openpyxl` | 3.1.2
chocolate | Required. | Implements `openpyxl`. Has various functions to manage using it as a data structure. Also implements other spreadsheet libraries. | Included with py3TranslateLLM. | See [source].
functions | Required. | Has various helper functions used in main program. | Included with py3TranslateLLM. | See [source].
dealWithEncoding | Required. | Handles text codecs. Implements text codec detection libraries. | Included with py3TranslateLLM. | See [source](resources).
translationEngines/* | Required. | Handles logic for translation services. | Included with py3TranslateLLM. | See [source](resources).
[requests](//pypi.org/project/requests) | Required. | Used for HTTP get/post requests. Required by both py3TranslateLLM and DeepL. | `pip install requests` | 2.31.0
[chardet](//pypi.org/project/chardet) | Recommended. | Detects text codecs. | `pip install chardet` | 5.2.0
[charamel](//pypi.org/project/charamel) | Recommended. | Detects text codecs. | `pip install charamel` | 1.0.0
[charset-normalizer](//pypi.org/project/charset-normalizer) | Recommended. | Detects text codecs. | `pip install charset-normalizer` | 3.3.2
[deepl-python](//github.com/DeepLcom/deepl-python) | Optional. | Used for DeepL NMT via their API. Optional otherwise. | `pip install deepl` | 1.16.1
[xlrd](//pypi.org/project/xlrd/) | Optional. | Provides reading from Microsoft Excel Document (.xls). | `pip install xlrd` | 2.0.1
[xlwt](//pypi.org/project/xlwt/) | Optional. | Provides writing to Microsoft Excel Document (.xls). | `pip install xlwt` | 1.3.0
[odfpy](//pypi.org/project/odfpy) | Optional. | Provides interoperability for Open Document Spreadsheet (.ods). | `pip install odfpy` | 1.4.1
[tdqm](//pypi.org/project/tqdm) | Optional. | Adds pretty progress bar to CLI. | `pip install tdqm` | 0.0.1
[pykakasi](//codeberg.org/miurahr/pykakasi) | Optional. | Fast, simple, and lightweight JPN->Romaji dictionary based on [Kakasi](http://kakasi.namazu.org). | `pip install pykakasi` | 2.2.1
[cutlet](//github.com/polm/cutlet) | Optional. | Accurate JPN->Romaji dictionary with [MeCab](//taku910.github.io/mecab) support. | `pip install cutlet` | n/a

Libraries can also require other libraries.

- deepl-python requires: `requests`, `charset-normalizer`, `idna`, `urllib3`, `certifi`.
- openpyxl can optionally use: `defusedxml`.
- odfpy requires: `defusedxml`.
- cutlet requires [fugashi](//github.com/polm/fugashi) to tokenize contents based upon the [MeCab](//taku910.github.io/mecab) tokenizer using a dictionary like [unidic-py](//github.com/polm/unidic-py), [unidic-lite](//github.com/polm/unidic-lite), [ipadic-py](//github.com/polm/ipadic-py), [jumandic-py](//github.com/polm/jumandic-py).
    - Alternative MeCab wrappers:
    - https://github.com/SamuraiT/mecab-python3
    - https://github.com/WorksApplications/sudachi.rs and https://github.com/WorksApplications/SudachiPy
    - Korean versions:
    - https://github.com/NoUnique/pymecab-ko
    - https://konlpy.org/en/latest/

###  Guide: Installing and managing Python library versions with `pip`:

- [pip Usage Guide](//github.com/gdiaz384/py3TranslateLLM/wiki/pip-Usage-Guide).

## Licenses:

- Python standard library's [license](//docs.python.org/3/license.html). For source code, open the Python installation directory on the local system.
- [openpyxl](//pypi.python.org/pypi/openpyxl)'s [license](//foss.heptapod.net/openpyxl/openpyxl/-/blob/3.1.2/LICENCE.rst) and [source code](//foss.heptapod.net/openpyxl/openpyxl).
- [chardet](//pypi.org/project/chardet)'s license is [LGPL v2+](//github.com/chardet/chardet/blob/main/LICENSE). [Source code](//github.com/chardet/chardet).
- [charamel](//pypi.org/project/charamel)'s [license](//github.com/chomechome/charamel/blob/master/LICENSE) and [source code](//github.com/chomechome/charamel).
- [charset-normalizer](//pypi.org/project/charset-normalizer)'s [license](//github.com/jawah/charset_normalizer/blob/master/LICENSE) and [source code](//github.com/jawah/charset_normalizer).
- [xlrd](//pypi.org/project/xlrd)'s [license](//github.com/python-excel/xlrd/blob/master/LICENSE) and [source code](//github.com/python-excel/xlrd).
- [xlwt](//pypi.org/project/xlwt)'s [license](//github.com/python-excel/xlwt/blob/master/LICENSE) and [source code](//github.com/python-excel).
- [odfpy](//pypi.org/project/odfpy)'s, license is [GPL v2](//github.com/eea/odfpy/blob/master/GPL-LICENSE-2.txt). [Source code](//github.com/eea/odfpy).
- [tdqm](//pypi.org/project/tqdm)'s [license](//github.com/tqdm/tqdm/blob/master/LICENCE) and [source code](//github.com/tqdm/tqdm).
- [KoboldCPP](//github.com/LostRuins/koboldcpp) is [AGPL v3](//github.com/LostRuins/koboldcpp/blob/concedo/LICENSE.md). The GGML library and llama.cpp part of KoboldCPP has this [license](//github.com/LostRuins/koboldcpp/blob/concedo/MIT_LICENSE_GGML_LLAMACPP_ONLY).
- DeepL's [various plans](//www.deepl.com/pro) and [Terms of Use](//www.deepl.com/en/pro-license). DeepL's [python library](//pypi.org/project/deepl) for their API has this [license](//github.com/DeepLcom/deepl-python/blob/main/LICENSE) and [source code](//github.com/DeepLcom/deepl-python).
- [fairseq](//github.com/facebookresearch/fairseq) and [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE).
- [Sugoi](//sugoitoolkit.com) and [source code](//github.com/leminhyen2/Sugoi-Japanese-Translator).
    - The pretrained model used in Sugoi NMT has its own non-commericial [license](//www.kecl.ntt.co.jp/icl/lirg/jparacrawl).
    - 'Sugoi NMT' is a wrapper for fairseq which, along with the pretrained model, does the heavy lifting for 'Sugoi NMT'.
    - Sugoi NMT is one part of the 'Sugoi Translator Toolkit' which is itself part of the free-as-in-free-beer distributed 'Sugoi Toolkit' which contains other projects like manga translation and upscaling.
    - The use of Github to post source code for Sugoi Toolkit suggests intent to keep the wrapper code under a permissive license. A more concrete license may be available on discord.
- py3TranslateLLM.py and the associated libraries under `resources/` are [GNU Affero GPL v3](//www.gnu.org/licenses/agpl-3.0.html).
    - You are free to use the software as long as you do not infringe on the [freedoms](//www.gnu.org/philosophy/free-sw.en.html#four-freedoms) of other people.
    - Summary: Feel free to use it, modify it, and distribute it to an unlimited extent, but *if you distribute binary files of this program outside of your organization*, then please make the source code for those binaries available.
    - The imperative to make source code available also applies if using this program as part of a server *if that server can be accessed by people outside of your organization*. For additional details, consult the license text.
    - Binaries for py3TranslateLLM.py made with pyinstaller, or another program that can make binaries, also fall under GNU Affero GPL v3.
        - This assumes the licenses for libraries used in the binary are compatible with one another. If the licenses used for a particular binary are not compatible with one another, then the resulting binary is not considered redistributable. Only lawyers can determine that, and also only lawyers need to worry about it.
