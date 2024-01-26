# fairseq Installation Guide

[fairseq](//github.com/facebookresearch/fairseq) is a project originally used by Meta/Facebook for data training.

- fairseq can also be configured to process pretrained models for use with language translation.
- For JPN->ENG translation, consider Sugoi translator, a preconfigured wrapper for fairseq.
- fairseq itself relies on PyTorch as the backend engine for many of its services, and PyTorch supports both CPU and GPU modes.

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

## Installing fairseq

### Install Dependencies

- (Optional) Download and install `git`: https://git-scm.com/download/
    - It is possible to download fairseq as a release or a main repository archive.
    - `git` is not needed but still nice to have.
- Download the [Ninja](//ninja-build.org) build system and put the binary somewhere in %path%: [github.com/ninja-build/ninja/releases](//github.com/ninja-build/ninja/releases)
    - To check for locations to place the Ninja binary file, open a command prompt (`cmd.exe`) or terminal and type the following:
        - Windows: `echo %path%`
        - Linux: `echo $PATH`
    - Alternatively, `choco install ninja`
        - [Chocolatey](//chocolatey.org) is a package manager for Windows. It tends to be very good for programs that do not need any special options set during installation, like Ninja, and unlike Python and Git.
- Python 3.8+.
    - Check if Python is already installed:
        - Open a command prompt or terminal and enter `python--version`
        - If it lists a version, then is already installed.
    - If Python is not already installed, [download Python](//www.python.org/downloads). For Windows 7, download from [here](//github.com/adang1345/PythonWin7).
        - PyTorch and fairseq require Python 3.8+.
        - If using Windows, PyTorch on Windows only supports Python 3.8-3.11 as of 2024 January.
            - Do not use Python 3.12 until PyTorch starts to support it.
            - Python 3.11 or is the safest modern option, otherwise use Python 3.10 if concerned about compatibility.
            - Make sure to "Add to Path" is selected during installation.
- [pytorch](//pytorch.org) contains is a table showing the official installation commands.
    - Getting started with fairseq and PyTorch GPU processing:
        - Can be very error prone in the real world due different hardware, operating systems, driver versions, and CUDA library versions.
        - PyTorch has CUDA but not OpenCL support, so it really only works reliably with Nvidia GPUs as of 2024 January.
            - Newer versions of PyTorch do support [ROCm](//rocm.docs.amd.com/en/latest/what-is-rocm.html) on [Linux](//rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html) for use with AMD GPUs, but very few AMD GPUs are currently compatible in that exact configuration.
            - The [Windows](//rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html) versions of ROCm support more GPUs but there are no PyTorch builds for Windows that use it.
            - In addition, fairseq needs to be updated to enable using PyTorch's ROCm support in contrast to CPU and CUDA which are already supported.
            - Support for AMD GPUs and Windows may improve in the future.
        - Requires very large downloads, 2.4GB+ possibly multiple times if any debugging is required.
        - The only benefit is faster processing. CPU processing is slower, but it still works.
    - For those reasons, it is strongly recommended to install the CPU version of torch first in order to verify fairseq actually works in the local environment. Once the software stack has been verified to work with PyTorch (CPU), it is a (relatively) simple matter to switch it to PyTorch (GPU) later.
    - Please refer to the official installation table, but here are some examples:
        - Latest stable PyTorch CPU:
            - `pip install torch torchvision torchaudio`
        - Older PyTorch CPU version:
            - `pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu`
        - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
            - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
        - Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
            - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
        - Previous versions (CPU + GPU): [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions)
        - Aside: [download.pytorch.org/whl/](//download.pytorch.org/whl/) is an interesting place. Very educational, especially the [torch/](//download.pytorch.org/whl/torch/) subdirectory.
- Install additional fairseq dependencies
    - `pip install bitarray hydra-core omegaconf sacrebleu scikit-learn sentencepiece tqdm`
    - `pip install flask tensorboardX regex requests` #These are optional. Optional means they will very likely be needed later, but not yet.

### Install fairseq

- Now that the dependencies are installed, fairseq can finally be installed.
    - Download the release.zip from the [releases page].
    - Download the main.zip from the central project page.
        - Green thing. TODO: Put stuff here.
    - Alternatively: `git clone https://github.com/facebookresearch/fairseq`
- If needed, extract the contents.
- Start a command prompt.
```
cd fairseq
pip install --editable ./
python setup.py build_ext --inplace
```

### Download models

- Now that `fairseq` has been installed, it is time to download a model for a language pair and the related vocabulary list. Examples:
    - One of the [JParaCrawl models](http://www.kecl.ntt.co.jp/icl/lirg/jparacrawl) for a Japanese-English language pair. .
        - Download -> NMT Models (based on v3.0) -> Direction -> Japanese-to-English -> small, base, large -> Download
            - small (776MB -> 923MB)
            - base (900MB -> 1.04GB)
            - big (2.59GB -> 3.06GB)
        - Download the associated Sentencepiece models:
            - Download -> NMT Models (based on v3.0) -> Sentencepiece models -> Download
    - fairseq's [list of pretrained models](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md#pre-trained-models).
    - [nepali-translator](//github.com/sharad461/nepali-translator), a Nepali-English language pair model.
    - It is also possible to fine tune the output of existing models. Example: [jparacrawl-finetune](//github.com/MorinoseiMorizo/jparacrawl-finetune).
- Extract the model and the vocabulary to fairseq/model. Create the folder if it does not exist.
    - Move `big.pretrain.pt`, `dict.en.txt`, and `dict.ja.txt` to fairseql/model
    - Move the extracted sentence pair model and vocabulary to the same folder.
    - If using Sugoi Offline Translator 4.0, move the updated model to: `Sugoi-Translator-Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\offlineTranslation\fairseq\japaneseModel`

### Verify the model works

- Interactive mode
- Server mode

### Other Notes:

- BPE stands for 'Byte Pair Encoding' vocabulary.
