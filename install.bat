@echo off
setlocal EnableDelayedExpansion

:: Set working directory to the script's location
cd /d "%~dp0"
if %ERRORLEVEL% neq 0 (
    echo Error: Could not change to script directory.
    pause
    exit /b 1
)

:: Check if Python 3.10.11 is available
python --version 2>nul | findstr "3.10.11" >nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.10.11 is not installed or not in PATH.
    echo Please ensure Python 3.10.11 is installed and accessible.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to upgrade pip.
    pause
    exit /b 1
)

:: Install PyTorch with CUDA 12.4
echo Installing PyTorch, torchaudio, and torchvision with CUDA 12.4...
pip install torch==2.4.1 torchaudio==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu124
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install PyTorch packages.
    pause
    exit /b 1
)

:: Install remaining requirements from requirements.txt
if not exist "requirements.txt" (
    echo Error: requirements.txt not found in current directory.
    pause
    exit /b 1
)
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install requirements.
    pause
    exit /b 1
)

:: Check if huggingface-cli is installed
where huggingface-cli >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: huggingface-cli is not installed. Installing...
    pip install huggingface_hub
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install huggingface_hub.
        pause
        exit /b 1
    )
)

:: Define models and their target directories for MarianMT (relative paths)
set "MODELS[0]=Helsinki-NLP/opus-mt-en-zh"
set "TARGET_DIRS[0]=.\models\marianmt\opus-mt-en-zh"
set "MODELS[1]=Helsinki-NLP/opus-mt-zh-en"
set "TARGET_DIRS[1]=.\models\marianmt\opus-mt-zh-en"

:: List of files to download for MarianMT
set "FILES=vocab.json source.spm target.spm tokenizer_config.json config.json pytorch_model.bin"

:: Download MarianMT models
echo Downloading MarianMT models...
for /L %%i in (0,1,1) do (
    set "HF_MODEL=!MODELS[%%i]!"
    set "TARGET_DIR=!TARGET_DIRS[%%i]!"

    if not exist "!TARGET_DIR!" (
        mkdir "!TARGET_DIR!"
        if !ERRORLEVEL! neq 0 (
            echo Error: Could not create directory !TARGET_DIR!
            pause
            exit /b 1
        )
    )

    for %%f in (%FILES%) do (
        echo Downloading %%f for !HF_MODEL!...
        huggingface-cli download !HF_MODEL! %%f --local-dir "!TARGET_DIR!" --local-dir-use-symlinks False
        if !ERRORLEVEL! neq 0 (
            echo Error: Failed to download %%f for !HF_MODEL!
            pause
            exit /b 1
        )
    )

    for %%f in (%FILES%) do (
        if not exist "!TARGET_DIR!\%%f" (
            echo Error: %%f was not downloaded successfully for !HF_MODEL!.
            pause
            exit /b 1
        )
    )
    echo All files for !HF_MODEL! downloaded successfully to !TARGET_DIR!
)

:: Download XTTS v2
echo Downloading XTTS v2 (this may take a while)...
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=True)"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to download XTTS v2.
    pause
    exit /b 1
)

:: Move XTTS files to target directory (relative path)
echo Moving XTTS files to .\models\xtts\xtts_v2...
mkdir ".\models\xtts\xtts_v2"
if %ERRORLEVEL% neq 0 (
    echo Error: Could not create XTTS target directory.
    pause
    exit /b 1
)
move "%USERPROFILE%\.local\share\tts\tts_models--multilingual--multi-dataset--xtts_v2\*" ".\models\xtts\xtts_v2\"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to move XTTS files.
    pause
    exit /b 1
)

:: Deactivate virtual environment
echo Deactivating virtual environment...
deactivate

echo Setup complete! Virtual environment created and all models downloaded.
pause
exit /b 0