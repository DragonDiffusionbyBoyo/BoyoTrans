@echo off
setlocal EnableDelayedExpansion

:: Check if huggingface-cli is installed
where huggingface-cli >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: huggingface-cli is not installed or not in PATH.
    echo Please install it by running: pip install huggingface_hub
    pause
    exit /b 1
)

:: Define models and their target directories
set "MODELS[0]=Helsinki-NLP/opus-mt-en-zh"
set "TARGET_DIRS[0]=D:\Audio Translater\models\marianmt\opus-mt-en-zh"
set "MODELS[1]=Helsinki-NLP/opus-mt-zh-en"
set "TARGET_DIRS[1]=D:\Audio Translater\models\marianmt\opus-mt-zh-en"

:: List of files to download (required for MarianMT tokenizer and model)
set "FILES=vocab.json source.spm target.spm tokenizer_config.json config.json pytorch_model.bin"

:: Loop through each model
for /L %%i in (0,1,1) do (
    set "HF_MODEL=!MODELS[%%i]!"
    set "TARGET_DIR=!TARGET_DIRS[%%i]!"

    :: Create the target directory if it doesn't exist
    if not exist "!TARGET_DIR!" (
        mkdir "!TARGET_DIR!"
        if !ERRORLEVEL! neq 0 (
            echo Error: Could not create directory !TARGET_DIR!
            pause
            exit /b 1
        )
    )

    :: Download each file to the target directory
    for %%f in (%FILES%) do (
        echo Downloading %%f for !HF_MODEL!...
        huggingface-cli download !HF_MODEL! %%f --local-dir "!TARGET_DIR!" --local-dir-use-symlinks False
        if !ERRORLEVEL! neq 0 (
            echo Error: Failed to download %%f for !HF_MODEL!
            pause
            exit /b 1
        )
    )

    :: Verify all files are downloaded
    for %%f in (%FILES%) do (
        if not exist "!TARGET_DIR!\%%f" (
            echo Error: %%f was not downloaded successfully for !HF_MODEL!.
            pause
            exit /b 1
        )
    )

    echo All files for !HF_MODEL! downloaded successfully to !TARGET_DIR!
)

echo All models downloaded successfully!
pause
exit /b 0