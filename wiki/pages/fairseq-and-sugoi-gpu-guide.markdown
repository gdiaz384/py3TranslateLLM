# fairseq and Sugoi GPU Guide

[fairseq](//github.com/facebookresearch/fairseq) is a project originally used by Meta/Facebook for data training.

Sugoi Translator is a wrapper for [fairseq](//github.com/facebookresearch/fairseq) that comes preconfigured to support JPN->ENG translation. When this guide refers to 'Sugoi', it refers to 'Sugoi Offline Translator 4.0' which comes bundled with 'Sugoi Toolkit' versions 6.0/7.0 which are downloadable [here] and [here].

fairseq, and thus Sugoi, uses '[PyTorch](//pytorch.org)', a Machine Learning framework, as its main engine for data processing. In other words, getting fairseq and Sugoi to support GPU processing really just means getting PyTorch to work work as intended. As long as PyTorch is configured properly to use the GPU for processing, it can expose that capability to fairseq/Sugoi for much faster inferencing.

- [Source code](//github.com/facebookresearch/fairseq) and [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE).
- fairseq's [guide on translation](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md).


## Important

- Before following this guide, be sure to [install fairseq]() directly or [download]() the prepackaged Sugoi version.


## PyTorch Background

- PyTorch was originally a Facebook/Meta technology before the project was handed off to the Linux Foundation. -[source](//www.zdnet.com/article/facebooks-pytorch-ai-ignites-at-the-linux-foundation)
- PyTorch supports both CPU and GPU processing of model data.
- With some caveats, see 'Regarding AMD GPUs', GPU processing basically requires CUDA which means only Nvidia graphics cards can be used to accelerate fairseq/Sugoi as of 2024 January.
- More info:
    - PyTorch Website: [pytorch.org](//pytorch.org)
    - [Soure code](//github.com/pytorch/pytorch) and [license](//github.com/pytorch/pytorch/blob/main/LICENSE).

## GPU Hardware Requirements

- PyTorch Stable (2.1.2) requires an Nvidia GPU with Compute Capability 3.5+.
- [docs.nvidia.com/deploy/cuda-compatibility/index.html](//docs.nvidia.com/deploy/cuda-compatibility/index.html)
- [developer.nvidia.com/cuda-gpus](//developer.nvidia.com/cuda-gpus)
- [stackoverflow.com/questions/28932864/which-compute-capability-is-supported-by-which-cuda-versions](//stackoverflow.com/questions/28932864/which-compute-capability-is-supported-by-which-cuda-versions)
- Summary:
    - CUDA 10.x requires Compute Capability 3.0+
    - CUDA 11.x requires Compute Capability 3.5+
    - CUDA 12.x requires Compute Capability 5.0+

### The operating system driver must also support CUDA:

Cuda Toolkit | Linux_x86_64 Driver | Windows Driver
--- | --- | ---
CUDA 10.2 | >= 440.33 | >=441.22
CUDA 11.x | >= 450.80.02 | >=452.39
CUDA 12.x | >=525.60.13 | >=527.41

- As of 2024 January, PyTorch supports both CUDA 11.8 and 12.1.
- If Compute Capability 3.5+ is not available, older versions of PyTorch can be used for CUDA 10.x . Otherwise, use the latest version of PyTorch if at all possible.
- There is no way to upgrade the hardware's [Compute Capability](//developer.nvidia.com/cuda-gpus) without a new video card.
- The exposed CUDA version depends on both the underlying video card and the operating system driver, meaning that it can be upgraded and downgraded somewhat. For example, some newer driver versions remove old CUDA versions completely.
- In other words, check the Nvidia driver version the operating system is using.
    - On Windows, start the Nvidia Control Panel -> Help -> System Information -> Driver Version.
    - On Linux: TODO: Put stuff here.
- Only update the driver if the CUDA version needed for PyTorch is not in the currently installed driver.
    - If needed, search for the GPU + OS here:
    - [www.nvidia.com/download/find.aspx](//www.nvidia.com/download/find.aspx)

## Regarding Sugoi and Python:

- Sugoi Offline Translator 4.0 comes prepackaged with Python 3.9 and an old version of PyTorch CPU. These instructions attempt to work with the prepackaged version of Python, but that means the paths become impossible to read.
- The commands entered are exactly the same, but the binaries used to process those commands are not.
- For example: Sugoi Toolkit 7.0 has Python 3.9 embedded at... TODO: Put stuff here.

## Software Requirements (Not for Sugoi):

- If not done already, [download Python](//www.python.org/downloads) and install it. For Windows 7, download from [here](//github.com/adang1345/PythonWin7).
     - If using Windows, PyTorch on Windows only supports Python 3.8-3.11.
        - Do not use Python 3.12 until PyTorch starts to support it.
        - Python 3.11 or is the safest modern option, otherwise use Python 3.10 if concerned about compatibility.
        - Make sure to "Add to Path" is selected during installation.

## Installing PyTorch GPU for fairseq

- If the CPU version of PyTorch is currently installed, uninstall it:
    - `pip uninstall torch torchvision torchaudio`
- [pytorch.org](//pytorch.org) has a table showing the official installation commands based upon the selected cells.
- Please refer to the official installation table, but here are some examples:
    - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
    - Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
    - Previous versions (CPU + GPU): [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions)

pip install tensorboardX

## Installing PyTorch GPU for Sugoi

- If the CPU version of PyTorch is currently installed, uninstall it:
    - `pip uninstall torch torchvision torchaudio`
- [pytorch.org](//pytorch.org) has a table showing the official installation commands based upon the selected cells.
- Please refer to the official installation table, but here are some examples:
    - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
    - Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
    - Previous versions (CPU + GPU): [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions)


## Regarding Windows 7 and Windows 8:

With some caveats, CUDA supports compatibility between minor versions transparently. So, even if PyTorch supports up to CUDA 11.8, PyTorch will work with any CUDA 11.x version provided that CUDA version is available from the driver and the correct library file is used.

- The last WHQL driver for Windows 7 is 474.11 released on 2022Dec20 and supports up to CUDA 11.4.
- CUDA 11.4 was added on Windows with Nvidia driver version 465.
- Thus, if using a driver version older than 465, update it to the last WHQL driver available for Windows 7/8: 474.11.
- If using a driver version older than 465, update it from here: 
    - [www.nvidia.com/download/find.aspx](//www.nvidia.com/download/find.aspx)
    - Use the WHQL drivers. Game Ready Drivers do not support Windows 7/8.x.

### Shortcuts for 474.11:

- GeForce 1000 Series, GeForce 900 Series, GeForce 700 Series, GeForce 600 Series, Titan Series (Windows 7 + Windows 8):
    - https://www.nvidia.com/download/driverResults.aspx/197671
- GeForce 16 Series, RX 2000 Series, RTX 3000 Series (Windows 7 only):
    - https://www.nvidia.com/download/driverResults.aspx/197672
    - Note: Nvidia does not have any Windows 8 drivers for these cards.

The installation order starts roughly the same as above:

1. Use one of the [custom installers for Python](//github.com/adang1345/PythonWin7) as needed.
3. Uninstall any old version of PyTorch CPU as above.
2. Download and install PyTorch for CUDA 11.8 as above.
1. However, PyTorch installs a cuda.dll[] that is compiled against CUDA 11.8 which is not supported by 474.11. To fix that incompatibility, download a [] that was complied against CUDA 11.4
5. Next open the Python installation directory. To find out where Python is installed:
    1. Open a command prompt.
    1. `where python`
1. Next open the PyTorch installation path. It should be under:
    - ~`Python\Libs\site-packages\torch\Lib` TODO: fix this.
1. Rename the old cuda.dll to cuda.dll.backup
    - Important: Change the extension of this file in some way. It must not be `.dll` Deleting it also works but that is unnecessary.
1. Place the downloaded cuda.dll in this folder.
1. Verify it is loading. TODO:
    1. Launch a command prompt.
    1. `python`
    1. `import torch`
    1. verify_cuda()


## Regarding AMD GPUs:
Technically, PyTorch 2.0.1 added support for AMD GPUs through ROCm under Linux. But this has not been implemented for Windows as of 2024 January. ROCm compatibility is abysmally small.
https://rocm.docs.amd.com/projects/radeon/en/latest/docs/compatibility.html

- PyTorch has CUDA but [no OpenCL support](//github.com/pytorch/pytorch/issues/488).
- Newer versions of PyTorch do support [ROCm](//rocm.docs.amd.com/en/latest/what-is-rocm.html) on [Linux](//rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html) for use with AMD GPUs, but very few AMD GPUs are currently compatible in that exact configuration.
    - The [Windows](//rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html) versions of ROCm support more GPUs but there are no PyTorch builds for Windows that use it.
    - While fairseq may be able to use AMD GPUs on Linux through PyTorch's ROCm support, but in practical terms, it would need to be updated to actually enable this functionality. fairseq may only need small adjustments or it may need very large changes.
    - Support for AMD GPUs and Windows may improve in the future.
- Further reading:
    - https://github.com/facebookresearch/fairseq/issues?q=is%3Aissue+ROCm
    - https://stackoverflow.com/questions/64523498/can-you-accelerate-torch-dl-training-on-anything-other-than-cuda-like-hip-or
    - https://github.com/artyom-beilis/pytorch_dlprim
- AMD's ROCm documentation:
    - https://www.amd.com/en/products/software/rocm.html
    - https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html
    - https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html
    - https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/component-support.html
