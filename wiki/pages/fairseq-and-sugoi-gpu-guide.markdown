# PyTorch GPU Guide for fairseq, CTranslate2, and Sugoi

[fairseq](//github.com/facebookresearch/fairseq) is a project originally used by Meta/Facebook for data training.

[CTranslate2](//github.com/OpenNMT/CTranslate2) is an inference engine with an emphasis on high performance and low resource utilization that is part of the [OpenNMT](//opennmt.net), [Py](//github.com/OpenNMT/OpenNMT-py)), [TensorFlow](//github.com/OpenNMT/OpenNMT-tf), open source ecosystem for neural machine translation (NMT) and neural sequence learning.

Sugoi Translator is a wrapper for fairseq that comes preconfigured to support JPN->ENG translation. When this guide refers to 'Sugoi', it refers to 'Sugoi Offline Translator 4.0' which comes bundled with 'Sugoi Toolkit' versions 6.0/7.0.

fairseq and CTranslate2 rely on [PyTorch](//pytorch.org) for many of their backend engine services. PyTorch is an [open-source](//github.com/pytorch/pytorch) tensor framework designed for machine learning and deep learning that has both CPU and GPU modes with native Nvidia CUDA and AMD ROCm support.

While CTranslate2 has native CPU acceleration support, both fairseq and CTranslate2 rely on PyTorch for their GPU acceleration support. PyTorch also has limited support for DirectML by means of a Microsoft written plugin. As of early 2024, there are no PyTorch builds with ROCm support on Windows.

In other words, since fairseq/Sugoi and CTranslate2 use PyTorch as the main engine for data processing, getting fairseq and CTranslate2 to support GPU acceleration really just means getting PyTorch to work work as intended. As long as PyTorch is configured properly to use the GPU for processing, it can expose that capability to fairseq/Sugoi and CTranslate2 for much faster inferencing.

```
--top of stack--
Applications (py3TranslateLLM, Translator++, interactive translators)
CTranslate2, fairseq / Sugoi
PyTorch
Python 3
Operating System
Hardware (CPU/GPU)
--bottom of stack--
```

- fairseq [source code](//github.com/facebookresearch/fairseq) and [license](//github.com/facebookresearch/fairseq/blob/main/LICENSE).
- fairseq's [guide on translation](//github.com/facebookresearch/fairseq/blob/main/examples/translation/README.md).
- CTranslate2's [source code](//github.com/OpenNMT/CTranslate2) and [license](//github.com/OpenNMT/CTranslate2/blob/master/LICENSE).
    - Interesting: https://github.com/ymoslem/DesktopTranslator

## Important

- Before following this guide, be sure to [install fairseq](//github.com/gdiaz384/py3TranslateLLM/wiki/fairseq-Installation-Guide) directly or download the prepackaged Sugoi version from [here](//www.patreon.com/mingshiba/about) or [here](//archive.org/search?query=Sugoi+Toolkit).
- CTranslate2 can be installed with `pip install ctranslate2`.
    - More on managing versions with [Python](//github.com/gdiaz384/py3TranslateLLM/wiki/Python-Resources) and [pip](//github.com/gdiaz384/py3TranslateLLM/wiki/pip-Usage-Guide).

## PyTorch Background

- [PyTorch](//pytorch.org) was originally a Facebook/Meta technology before the project was handed off to the Linux Foundation. [Source](//www.zdnet.com/article/facebooks-pytorch-ai-ignites-at-the-linux-foundation).
- PyTorch supports both CPU and GPU processing of model data.
- With some caveats, see **Regarding AMD GPUs**, GPU processing basically requires CUDA which means only Nvidia graphics cards can be used to accelerate fairseq/Sugoi as of 2024 January.
- More info:
    - PyTorch Website: [pytorch.org](//pytorch.org).
    - [Soure code](//github.com/pytorch/pytorch) and [license](//github.com/pytorch/pytorch/blob/main/LICENSE).

## GPU Hardware Requirements

- As of 2024 January, PyTorch supports both CUDA 11.8 and 12.1.
- For OpenCL, ROCm, DirectML, and AMD GPUs, see: **Regarding AMD GPUs**.
- PyTorch Stable (2.2.0) using CUDA requires an Nvidia GPU with Compute Capability 3.5+.
- If Compute Capability 3.5+ is not available, then older versions of PyTorch can be used for CUDA 10.x . Otherwise, use the latest version of PyTorch if at all possible.
- There is no way to upgrade the hardware's [Compute Capability](//developer.nvidia.com/cuda-gpus) without a new video card as that is a hardware feature.
- Additional information:
    - Check the Compute Capability of the current GPU: [developer.nvidia.com/cuda-gpus](//developer.nvidia.com/cuda-gpus).
    - [stackoverflow.com/questions/28932864/which-compute-capability-is-supported-by-which-cuda-versions](//stackoverflow.com/questions/28932864/which-compute-capability-is-supported-by-which-cuda-versions)
- Summary:
    - CUDA 10.x requires Compute Capability 3.0+
    - CUDA 11.x requires Compute Capability 3.5+
    - CUDA 12.x requires Compute Capability 5.0+

### The operating system driver must also support CUDA:

- The actual exposed CUDA version depends on both the underlying video card and the operating system driver, meaning that it can be upgraded and downgraded somewhat. For example, some newer driver versions remove old CUDA versions completely.
- Technical information on driver versions and CUDA: [docs.nvidia.com/deploy/cuda-compatibility/index.html](//docs.nvidia.com/deploy/cuda-compatibility/index.html)
- Aside: If using Windows 7 or Windows 8, See: **Regarding Windows 7 and Windows 8** for information on selecting a compatible driver.
- First, check the Nvidia driver version the operating system is using:
    - On Windows, start the Nvidia Control Panel -> Help -> System Information -> Driver Version.
    - On Linux, pick one:
        - Check nvidia-settings GUI -> Server information
        - `nvidia-smi`
        - `nvidia-settings -q NvidiaDriverVersion`
        - `cat /proc/driver/nvidia/version`
- Only update the driver if the CUDA version needed for PyTorch is not in the currently installed driver.
    - If needed, search for the GPU + OS here:
    - [www.nvidia.com/download/find.aspx](//www.nvidia.com/download/find.aspx)

Cuda Toolkit | Linux_x86_64 Driver | Windows Driver
--- | --- | ---
CUDA 10.2 | >= 440.33 | >=441.22
CUDA 11.x | >= 450.80.02 | >=452.39
CUDA 12.x | >=525.60.13 | >=527.41

- CUDA 12 might be better for GeForce RTX 4000 Series cards, and CUDA 11 might be better for earlier generations.
- For optimal performance, test each CUDA version on the local system and compare the results.

## Installing PyTorch GPU for fairseq and CTranslate2 (Not for Sugoi)

- **Important**: fairseq CPU and CTranslate2 should already be working in CPU mode. If it is not, then please follow [this guide](//github.com/gdiaz384/py3TranslateLLM/wiki/fairseq-Installation-Guide) before continuing further.
- If the CPU version of PyTorch is currently installed, uninstall it:
    - `pip uninstall torch torchvision torchaudio`
- [PyTorch.org](//pytorch.org) has a table showing the official installation commands based upon the selected cells.
- Please refer to the official installation table, but here are some examples:
    - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
    - Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
        - `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
    - PyTorch v2.2.0 Windows/Linux GPU for CUDA 11.8 Syntax:
        - `pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118`
    - PyTorch v2.2.0 Windows/Linux GPU for CUDA 12.1 Syntax:
        - `pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu121`
    - Previous versions (CPU + GPU): [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions).
- `pip install tensorboardX`

## Installing PyTorch GPU for Sugoi

### Regarding Sugoi and Python:

- Sugoi Offline Translator 4.0 comes prepackaged with Python 3.9, an old version of PyTorch CPU, and other associated libraries.
- These instructions to get Sugoi working with CUDA via PyTorch attempt to work with the prepackaged Python version distributed with Sugoi, but that means the paths can become impossible to read.
- The commands entered in **Installing PyTorch GPU for fairseq** and **Installing PyTorch GPU for Sugoi** are exactly the same, but the binaries used to process those commands are not.

### Determine and set the correct paths

- The Sugoi instructions have been split into two sections in order to ensure the correct Python environment is being invoked and to increase readability.
- First, find the location of the embedded `python.exe`.
    - For example: Sugoi Toolkit 7.0 has Python 3.9 embedded at:
        - `Sugoi-Toolkit-V7.0_New_Year\Sugoi_Translator_Toolkit_V7\Code\Power-Source\Python39`
- Open a command prompt. Note: Use this command prompt instance for all of the tasks related to updating Sugoi.
- Create the `pythonExe` batch variable.
    - Hold the Shift key on the keyboard
    - Right-click on `python.exe`
    - Let go of the Shift key
    - Select "Copy as path"
    - Type the following into the command prompt:
```
set pythonExe=
```
- Paste the path copied earlier into the command prompt after the `=`.
    - On newer versions of Windows:
        - Ctrl + V, or
        - Right-click + Paste.
    - On older versions of Windows:
        - Right-click the title bar on the command prompt Window.
        - Make sure "Insert Mode" and "QuickEdit Mode" are both checked.
        - OK
        - Right-click in the main command prompt window. That should paste the text. Example:
```
set pythonExe="D:\Sugoi-Toolkit-V7.0_New_Year\Sugoi_Translator_Toolkit_V7\Code\Power-Source\Python39\python.exe"
```
- Press Enter.
- The `pythonExe` variable can be invoked by surrounding it with `%`. Example: `%pythonExe%`
    - In Batch, the native Windows scripting language, the case does not matter.
- Next, is `pip.exe`.
    - pip is available as the python module `pip` which can be invoked more simply as:
        - `python.exe -m pip`
        - Since python is already available as a variable, the final syntax is: `%pythonExe% -m pip`
    - This `python -m pip` syntax for invoking pip as a Python module is preferred since that reduces the need to worry about the path to pip.exe and the correct environment for both is always invoked automatically.
    - Technically, Python and pip.exe can also be invoked together to use the correct paths by entering one executable after the other.
        - Example: `python.exe pip.exe`
        - pip.exe is at: `Python39\Scripts\pip.exe`.
        - A variable for pip could be created similarly as above with `set pipExe=`
        - Since they would both be variables, the syntax would be: `%pythonExe% %pipExe%`
        - However, the module syntax will be used going forward as that is simpler.
- To get the current version of pip and confirm it is working with the embedded environment, enter: 
``` 
%pythonExe% -m pip --version
```
If all of the paths are correct, then it should output something like:
```
pip 21.2.4 from D:\Sugoi-Toolkit-V7.0_New_Year\Sugoi_Translator_To
olkit_V7\Code\Power-Source\Python39\lib\site-packages\pip (python 3.9)
```
- That confirms that this Python and pip invocation are not conflicting with the local environment.
- If it crashes, displays that python or pip is not a recognized command or outputs something like:
```
pip 23.3.2 from D:\Python310\lib\site-packages\pip (python 3.10)
```
Then the paths are not correct. Troubleshoot before proceding further.

### Use the correct paths to update PyTorch in the portable version of Python

- **Important**: fairseq/Sugoi CPU should already be working. If it is not, then troubleshoot it before continuing further.
- If the CPU version of PyTorch is currently installed, uninstall it:
    - `%pythonExe% -m pip uninstall torch torchvision torchaudio`
    - It is possible to check what version of torch is installed by using pip's freeze command.
        - `%pythonExe% -m pip freeze`
- [pytorch.org](//pytorch.org) has a table showing the official installation commands based upon the selected cells.
    - Replace their `pip3` syntax with the updated syntax of `%pythonExe% -m pip` that uses the local Sugoi environment.
    - The commands should otherwise be the same.
- Please refer to the official installation table, but here are some examples:
    - Latest stable PyTorch Windows/Linux GPU for CUDA 11.8 Syntax:
```
%pythonExe% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
- Latest stable PyTorch Windows/Linux GPU for CUDA 12.1 Syntax:
```
%pythonExe% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
- Previous versions (CPU + GPU): [pytorch.org/get-started/previous-versions](//pytorch.org/get-started/previous-versions)
    - Use the 'For Windows and Linux' options.

## Verify that CUDA is available in PyTorch:

### Method 1) Using the interactive Python interpreter.

Launch a command prompt and launch the Python interpreter:

```
python
```
- For Windows, if using Sugoi, then launch Python using `%pythonExe%` instead.
- For Linux, check if an Nvidia GPU is active with the following command:
    - `nvidia-smi -L`
- Next, enter the following:
```
import torch
torch.cuda.is_available()
```
- It might take a few moments to import torch.
- If it prints True, then PyTorch is available to use with fairseq.
- Alternatively, try Method 2. It is longer but more automated once it is working.
- Use CTRL + Z, end of input, to exit the Python interpreter. CTRL + C, keyboard interupt, will not work.

### Method 2) Use a Python script.

- Create a new file called `testTorch.py` with these contents:

```
print('')
try:
    import torch
except:
    print(' torch library is not available.')
print( ' torch.version=' + torch.__version__ )
print ( ' torch.cuda.is_available()=' + str(torch.cuda.is_available()) )
#print( ' torch.version.cuda=' + str(torch.version.cuda) )
if torch.cuda.is_available() == True:
    print( ' torch.version.cuda=' + str(torch.version.cuda) )
```
- Then run it as: `python testTorch.py`
    - If using Sugoi, then launch python using `%pythonExe% testTorch.py` instead.
- If everything is working, it should print out something like:
```
torch.version=2.1.2+cu118
torch.cuda.is_available()=True
torch.version.cuda=11.8
```
For Windows 7/8, the minor version mismatch is inconsequential. 
But if it prints out:
```
torch.version=2.1.2+cu118
torch.cuda.is_available()=False
```
Or:
```
torch library is not available
#And then crashes.
```
Then something went wrong installing torch or CUDA. Troubleshoot as needed.

## Updating fairseq to use GPU

### For fairseq:

Open software used to invoke fairseq, and find the `TransformerModel.from_pretrained()` function. Add a `cuda()` method invocation after it to the assigned handle.
Example:
```
from fairseq.models.transformer import TransformerModel
model = TransformerModel.from_pretrained(
#Lots of code here
)
```
Add `myHandle.cuda()`.
```
from fairseq.models.transformer import TransformerModel
model = TransformerModel.from_pretrained(
#Lots of code here
)
model.cuda()
```

The assigned handle, `model` in the above example, is going to be different depending on the code used to invoke the model but it will always be a variable with the constructor `TransformerModel.from_pretrained()`. Adjust the handle name as needed.

### For Sugoi:

- Sugoi comes prepackaged with a development flask server. It needs to be updated to invoke PyTorch CUDA.
- Open the following file:
```
Sugoi-Toolkit\Sugoi_Translator_Toolkit\Code\backendServer\Program-Backend\Sugoi-Japanese-Translator\offlineTranslation\fairseq\flaskServer.py
```
Locate the ja2en function and change the code from:
```
ja2en = TransformerModel.from_pretrained(
    './japaneseModel/',
    checkpoint_file='big.pretrain.pt',
    source_lang = "ja",
    target_lang = "en",
    bpe='sentencepiece',
    sentencepiece_model='./fairseq/spmModels/spm.ja.nopretok.model',
    # is_gpu=True
)

# ja2en.cuda()
```
Remove the last `#`. In Python, `#` means 'comment out the rest of the line'. Change it to:
```
ja2en = TransformerModel.from_pretrained(
    './japaneseModel/',
    checkpoint_file='big.pretrain.pt',
    source_lang = "ja",
    target_lang = "en",
    bpe='sentencepiece',
    sentencepiece_model='./fairseq/spmModels/spm.ja.nopretok.model',
    # is_gpu=True
)

ja2en.cuda()
```
- Save the file.
- Relaunch Sugoi.
- Test Sugoi.
- The GPU should now register usage.

## Additional resources:

- cuDNN:
    - https://developer.download.nvidia.com/compute/redist/cudnn/
    - https://developer.download.nvidia.com/compute/redist/cudnn/v8.8.0/local_installers/11.8/
    - https://developer.download.nvidia.com/compute/redist/cudnn/v8.8.0/local_installers/12.0/
    - https://developer.download.nvidia.com/compute/redist/cudnn/v8.2.4/
        - Last Windows 7 version is `cudnn-11.4-windows-x64-v8.2.4.15.zip`
    - https://github.com/Purfview/whisper-standalone-win/releases/tag/libs

## Regarding Windows 7 and Windows 8:

With some caveats, CUDA supports compatibility between minor versions transparently. So, even if PyTorch supports up to CUDA 11.8, PyTorch will work with any CUDA 11.x version provided that CUDA version is available from the driver and the correct library file is used.

- The last WHQL driver for Windows 7 is 474.11 released on 2022Dec20 and supports up to CUDA 11.4.
- CUDA 11.4 was added on Windows with Nvidia driver version 465.
- Thus, if using a driver version older than 465, update it to the last WHQL driver available for Windows 7/8: 474.11.
    - [www.nvidia.com/download/find.aspx](//www.nvidia.com/download/find.aspx)
    - Use the WHQL drivers. Game Ready Drivers do not support Windows 7/8.x.

### Shortcuts for 474.11:

- GeForce 1000 Series, GeForce 900 Series, GeForce 700 Series, GeForce 600 Series, Titan Series (Windows 7 + Windows 8):
    - https://www.nvidia.com/download/driverResults.aspx/197671
- GeForce 16 Series, RX 2000 Series, RTX 3000 Series (Windows 7 only):
    - https://www.nvidia.com/download/driverResults.aspx/197672
    - Note: Nvidia does not have any Windows 8 drivers for these cards.
- cuDNN: https://developer.download.nvidia.com/compute/redist/cudnn/v8.2.4/cudnn-11.4-windows-x64-v8.2.4.15.zip

The installation order starts roughly the same as above:

1. Use one of the [custom installers for Python](//github.com/adang1345/PythonWin7) as needed.
1. Uninstall any old version of PyTorch CPU as above.
1. Download and install PyTorch for CUDA 11.8 as above.
1. However, PyTorch installs a `cudart64_110.dll` that is compiled against CUDA 11.8 which is not supported by 474.11. To fix that incompatibility, download a [cudart64_110.dll](//github.com/AUTOMATIC1111/stable-diffusion-webui/issues/7379#issuecomment-1407782858) that was complied against CUDA 11.4.
1. Next open the Python installation directory. To find out where Python is installed:
    1. Open a command prompt.
    1. `where python`
1. Next open the PyTorch installation path. For example, for Python 3.10 it should be under:
    - `Python310\Lib\site-packages\torch\lib`
1. Rename `cudart64_110.dll` to `cudart64_110.dll.backup` for safekeeping.
    - Important: Change the extension of this file in some way. It must not end in `.dll` or it will load automatically and the new version will not take effect.
    - Deleting it also works, but that is unnecessary.
1. Place the downloaded `cudart64_110.dll` into this folder.
1. See **Verify that CUDA is available in PyTorch** and continue with the rest of the installation procedure as normal.

## Regarding AMD GPUs:
- PyTorch supports CPU and CUDA, but it has [no OpenCL support](//github.com/pytorch/pytorch/issues/488).
- Technically, PyTorch 2.0.1 added support for AMD GPUs through ROCm under Linux. However, this has not been implemented for Windows as of 2024 January and ROCm compatibility on Linux is abysmally small.
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
    - https://rocm.docs.amd.com/projects/radeon/en/latest/docs/compatibility.html
    - https://github.com/ROCm/pytorch/wiki/Building-PyTorch-for-ROCm

### Microsoft DirectML

- One alternative is to use Microsoft's DirectML implementation.
- DirectML provides GPU acceleration for machine learning based on the DirectX 12 API, which means it is a Windows only machine learning framework.
- Requirements:
    - Windows 1703/1903.
    - DirectX 12 capable GPU (Nvidia, AMD, Intel, Qualcomm).
    - PyTorch 1.3.0
- Currently, in "Public Preview" and has a lot of bugs.
- Documentation:
    - https://pypi.org/project/torch-directml  Includes built-in spyware notice.
    - https://github.com/microsoft/DirectML
    - https://github.com/microsoft/DirectML/tree/master/PyTorch
    - Conflicting licenses: [Microsoft.AI.DirectML 1.13.0](//www.nuget.org/packages/Microsoft.AI.DirectML/1.13.0/License) vs [MIT](//github.com/microsoft/DirectML/blob/master/LICENSE)

```
Data Collection Notice
The software may collect information about you and your use of the software and send it to Microsoft.
Microsoft may use this information to provide services and improve our products and services. There
are also some features in the software that may enable you and Microsoft to collect data from users of
your applications. If you use these features, you must comply with applicable law, including providing
appropriate notices to users of your applications together with a copy of Microsoft's privacy statement.
Our privacy statement is located at https://go.microsoft.com/fwlink/?LinkID=824704. You can learn more
about data collection and use in the help documentation and our privacy statement. Your use of the
software operates as your consent to these practices.

Specifically, in torch-directml, we are collecting the GPU device info and operators that fall back to CPU
for improving operator coverage.
```

- Installation:
    - `pip install torch-directml`
    - Add the following import statment near the top of the server.py file: `import torch_directml`
    - Update the handle of `TransformerModel.from_pretrained` with the following:
        - `myHandle.to( torch_directml.device() )`
        - replace `myHandle` with the actual handle used in the server.py file code.

