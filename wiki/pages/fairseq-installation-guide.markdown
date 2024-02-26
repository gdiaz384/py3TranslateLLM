# fairseq Installation Guide

[fairseq](//github.com/facebookresearch/fairseq) is a project originally used by Meta/Facebook for data training.

- "Fairseq(-py) is a sequence modeling toolkit that allows researchers and developers to train custom models for translation, summarization, language modeling and other text generation tasks." -Meta/Facebook's description of fairseq on [PyPi.org](//pypi.org/project/fairseq)
- fairseq can also be configured to process pretrained models for use with language translation.
    - For JPN->ENG translation, consider Sugoi translator, a preconfigured wrapper for fairseq.
- fairseq itself relies on PyTorch as the backend engine for many of its services.
- PyTorch supports both CPU and GPU modes.

```
--top of stack--
Applications (py3TranslateLLM, Translator++, interactive translators)
fairseq / Sugoi
PyTorch
Python 3
Operating System
Hardware (CPU/GPU)
--bottom of stack--
```

- [Source code](//github.com/facebookresearch/fairseq) and [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE).
- fairseq's [guide on translation](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md).

## Last Stable Build VS Building From Source

- Machine learning is an area of active development, so using more recent versions for fairseq and PyTorch may be advisable.
    - Certain versions of software may also require bugfixes which are only present in newer versions of fairseq.
- If the version of available using pip is not very recent, then consider building from source instead.
- To check the available library versions using pip check [this guide](//github.com/gdiaz384/py3TranslateLLM/wiki/pip-Usage-Guide). Summary:
    - `pip index versions <libraryname>`
    - `pip index versions fairseq`
- Compare the available version on pip with the most recent version:
    - Open [github.com/facebookresearch/fairseq/releases](//github.com/facebookresearch/fairseq/releases).
    - Click on the most recent pip release, like v0.12.2.
    - It should list the number of commits to the main branch since the release.
    - Check the [main branch](//github.com/facebookresearch/fairseq)'s [commit history](//github.com/facebookresearch/fairseq/commits/main/).
        - Click on 'commit history' above or the total number number of commits right below the green `<> Code` button.
- If the total number of commits is very high and there are a lot of recent commits, then it might be worth building from source.

## Installing fairseq

## Install fairseq From Last Stable Version

### Install Python

- Python 3.8+.
    - Check if Python is already installed:
        - Open a command prompt or terminal. Enter 
        - `python --version`
            - OSX users should use `python3 --version`.
        - If it lists a version, then is already installed.
    - The latest versions of PyTorch and fairseq require Python 3.8+ as of 2024 January.
    - Python versions older than 3.8+ will have to use older versions of fairseq and PyTorch (not recommended).
    - If using Windows, PyTorch on Windows only supports Python 3.8-3.11 as of 2024 January.
        - Do not use Python 3.12 until PyTorch starts to support it.
    - If Python is not already installed, [download Python](//www.python.org/downloads). For Windows 7, download from [here](//github.com/adang1345/PythonWin7).
        - Python 3.11 or is the safest modern option, otherwise use Python 3.10 if concerned about compatibility.
        - Make sure to "Add to Path" is selected during installation.

### Install fairseq Using pip

- Download the latest version from [PyPi](//pypi.org/project/fairseq) using pip:
    - `pip install fairseq`
    - Requires:
        - Python 3.6+
        - PyTorch 1.5.0+
- `pip` will install various dependencies automatically if using a last stable version. 
- More information: https://pypi.org/project/fairseq/

## Install fairseq From Source

### Install Dependencies:

- Python 3.8+. See above.
- (Optional) Download and install `git`: https://git-scm.com/download/
    - It is possible to download fairseq as a release, a main repository archive, or last stable version using pip.
    - `git` is not needed but still nice to have.
- Download the [Ninja](//ninja-build.org) build system and put the binary somewhere in %path%: [github.com/ninja-build/ninja/releases](//github.com/ninja-build/ninja/releases)
    - To check for locations to place the Ninja binary file, open a command prompt (`cmd.exe`) or terminal and type the following:
        - Windows: `echo %path%`
        - Linux: `echo $PATH`
    - Alternatively, `choco install ninja`
        - [Chocolatey](//chocolatey.org) is a package manager for Windows. It tends to be very good for programs that do not need any special options set during installation, like Ninja, and unlike Python and Git.
- On Windows, building from source requires [Visual Studio C++ 2015 build tools](//stackoverflow.com/questions/40504552/how-to-install-visual-c-build-tools),  [Visual Studio Build Tools 2015-2017](//aka.ms/vs/15/release/vs_buildtools.exe) in addition to the requirements below.
    - Microsoft bundles the installer for the 2015 Build Tools in with their 2017 Visual Studio Installer.
    - **Important**: fairseq needs the "Visual C++ 2015 Build Tools" to compile. These are not selected by default.
        - **Important**: During installation select the "Visual C++ build tools" in the main window pane.
        - **Important**: On the right pane, scroll down and check "VC++ 2015.3 v14.00 (v140) toolset for desktop".
        - Do not skip steps. Do not uncheck things.
        - With both sets of build tools selected, continue installation.
        - There is likely some workaround to avoid having to install any SDKs while still getting the build tools correctly configured.
            - However, the SDKs can also just be uninstalled after the build tools are no longer needed.
    - If not already installed, the build tools install [Microsoft .Net Framework](//dotnet.microsoft.com/en-us/download/dotnet-framework) 4.7.2.
- On Linux:
    - Debian: sudo apt-get install -y git build-essential cmake automake autoconf pkg-config libtool bzip2 curl wget g++ libtool 
    - Fedora: TODO: Put stuff here.
- [PyTorch.org](//pytorch.org) contains is a table showing the official installation commands.
    - Getting started with fairseq and PyTorch GPU processing:
        - Can be very error prone in the real world due different hardware, operating systems, driver versions, Python versions, and CUDA library versions.
        - Requires very large downloads, 2.4GB+ possibly multiple times if any debugging is required.
        - The only benefit is faster processing. CPU processing is slower, but it still works.
        - PyTorch has CUDA but not OpenCL support, so it really only works reliably with Nvidia GPUs as of 2024 January.
            - Newer versions of PyTorch do support [ROCm](//rocm.docs.amd.com/en/latest/what-is-rocm.html) on [Linux](//rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html) for use with AMD GPUs, but very few AMD GPUs are currently compatible in that exact configuration.
            - The [Windows](//rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html) versions of ROCm support more GPUs but there are no PyTorch builds for Windows that use it.
            - In addition, fairseq may need to be updated to enable using PyTorch's ROCm support in contrast to CPU and CUDA which are already supported in fairseq.
            - Support for AMD GPUs may improve in the future, but for now only Nvidia GPUs work with fairseq, especially if using Windows.
            - Technically DirectML, machine learning on DirectX 12, also exists, but it is still in early development and has a mountain's worth of problems.
    - For those reasons, it is strongly recommended to install the CPU version of PyTorch first in order to verify fairseq actually works in the local environment. Once the software stack has been verified to work with PyTorch CPU, it is a relatively simple matter to switch it to PyTorch GPU later.
    - Please refer to the official installation table, but here are some examples:
        - Latest stable PyTorch CPU:
            - `pip install torch torchvision torchaudio`
        - Older PyTorch CPU version:
            - `pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu`
        - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
            - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
        - Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
            - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
        - Previous versions, CPU + GPU: [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions)
        - Aside: [download.pytorch.org/whl/](//download.pytorch.org/whl/) is an interesting place. Very educational, especially the [torch/](//download.pytorch.org/whl/torch/) subdirectory.
- Install additional fairseq dependencies
    - `pip install bitarray hydra-core omegaconf sacrebleu scikit-learn sentencepiece tqdm`
    - `pip install tensorboardX regex requests` #These are optional. Optional means they will very likely be needed very soon, but not yet.

### Build fairseq from source:

- Now that the dependencies are installed, fairseq can finally be installed.
    - Download the main.zip from the central project page.
        - Click on the green `<> Code` button at the top -> Download Zip
    - Alternatively: `git clone https://github.com/facebookresearch/fairseq`
    - For a slightly older version, download a release.zip from the [releases page](//github.com/facebookresearch/fairseq/releases).
- Extract the contents if needed.
- Start a command prompt.
- Enter the following:
```
pushd fairseq     #Change this to the location of the fairseq project directory.
pip install --editable ./
python setup.py build_ext --inplace
```
- Check the above build process for errors and troubleshoot appropriately.

### Add the fairseq directory to path.

- Now that it has been built, Python needs to be made aware of it in order for Python programs to `import fairseq`.
- This can be done by adding the main fairseq directory to the environmental variable `PYTHONPATH`.
    - Windows: System->Advanced system settings->Advanced->Environmental Variables...-> User variables for [account]
        - New -> Variable name: `PYTHONPATH` and Variable value: `C:\my\path\to\fairseq` -> OK -> OK
        - Edit...-> Append `;C:\my\path\to\fairseq` including the first `;` -> OK -> OK
    - Linux: `export PYTHONPATH="${PYTHONPATH}:/my/path/to/fairseq"`
    - Adjust the path to the fairseq directory as appropriate.

## Download Models

- Now that `fairseq` has been installed, it is time to download a model for a language pair and the related vocabulary list. Examples:
    - One of the [JParaCrawl models](http://www.kecl.ntt.co.jp/icl/lirg/jparacrawl) for a Japanese-English language pair. .
        - Download -> NMT Models (based on v3.0) -> Direction -> Japanese-to-English -> small, base, large -> Download
            - small (776MB -> 923MB)
            - base (900MB -> 1.04GB)
            - big (2.59GB -> 3.06GB)
        - Download the associated Sentencepiece models:
            - Download -> NMT Models (based on v3.0) -> sentencepiece models -> Download
    - fairseq's [list of pretrained models](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md#pre-trained-models).
    - Sugoi Toolkit has a JPN->ENG model as well available. Download the toolkit [here](//www.patreon.com/mingshiba/about) or [here](//archive.org/search?query=Sugoi+Toolkit). The model itself is at:
        - `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\offlineTranslation\fairseq\japaneseModel`
    - Sharad Duwal's [nepali-translator](//github.com/sharad461/nepali-translator), a Nepali-English language pair model. [Demo](//translation.ilprl.ku.edu.np/nep-eng/default).
    - It is also possible to fine tune the output of existing models. Example: [jparacrawl-finetune](//github.com/MorinoseiMorizo/jparacrawl-finetune).

### Aside: Different model formats.

- This should probably go somewhere else, but for now, here are some links to different models even if they are not in fairseq format or for other types of generation.
- Background: 
    - OpenAI released Whisper model open-source
    - Meta released MMS and Llama 70B.
    - Google released a slim version of their Gemini model named [Gemma](//blog.google/technology/developers/gemma-open-models).
- Variety, including LLMs:
    - https://huggingface.co
    - https://huggingface.co/google
- Text->Image: 
    - https://civitai.com/search/models
- Text->Text:
    - https://opennmt.net/Models-py/
    - https://github.com/miguelknals/UN-EU-corpus-Demo-streamlit 
        - Related English <-> French [demo](https://un-eu-corpus-demo.streamlit.app).
- Audio->Text:
    - https://github.com/openai/whisper
        - https://huggingface.co/openai/whisper-base
        - https://huggingface.co/openai/whisper-large-v3
    - https://github.com/SYSTRAN/faster-whisper
        - https://huggingface.co/Systran
        - https://huggingface.co/Systran/faster-whisper-large-v3
        - https://github.com/Purfview/whisper-standalone-win
    - Whisper: https://huggingface.co/guillaumekln

- Extract the pretrained model and the vocabulary to fairseq/model. Create the folder if it does not exist.
    - Move `big.pretrain.pt`, `dict.en.txt`, and `dict.ja.txt` to fairseql/model
    - Move the extracted sentence pair model and vocabulary to the same folder.

## Verify the model works with fairseq

- Interactive mode:
    - See: [Interactive translation via PyTorch Hub](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md#example-usage-torchhub)
    - Or use their [command line tool](//fairseq.readthedocs.io/en/latest/command_line_tools.html#fairseq-interactive).
        - This is installed along with fairseq if using `pip`.
- Server mode:
    - OpenNMT's [server.py](//github.com/OpenNMT/OpenNMT-py/blob/master/onmt/bin/server.py). [Usage guide](//forum.opennmt.net/t/simple-opennmt-py-rest-server/1392).
    - reAlpha39's [flask rest server](//github.com/reAlpha39/fairseq-translate-server/blob/main/rest_server.py).
    - Use with [py3fairseqTranslationServer](//github.com/gdiaz384/py3fairseqTranslationServer)
    - There is also a small flask implementation included in Sugoi Toolkit. Also available [here](//github.com/cbc02009/vno-local-cpu/blob/main/flaskServer.py).

## Other Notes:

- BPE stands for 'Byte Pair Encoding' vocabulary.
- Additional resources:
    - phontron's [Japanese translation data](https://www.phontron.com/japanese-translation-data.php).
    - Stanford's [Japanese-English Subtitle Corpus](//nlp.stanford.edu/projects/jesc) (JESC).
    - [NLPL](http://nlpl.eu)'s [open parallel corpus](//opus.nlpl.eu) (OPUS) project.
- https://github.com/facebookresearch/fairseq2
    - Linux only and focused on LLMs instead.

