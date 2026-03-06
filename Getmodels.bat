@echo off
echo Downloading models to the 'models' directory...

:: Create models directory structure
mkdir models
mkdir models\marianmt
mkdir models\xtts

:: Activate venv
call venv\Scripts\activate

:: Download MarianMT - Chinese
echo Downloading MarianMT English to Chinese...
huggingface-cli download Helsinki-NLP/opus-mt-en-zh --local-dir ./models/marianmt/opus-mt-en-zh

echo Downloading MarianMT Chinese to English...
huggingface-cli download Helsinki-NLP/opus-mt-zh-en --local-dir ./models/marianmt/opus-mt-zh-en

:: Download MarianMT - Korean
echo Downloading MarianMT English to Korean...
huggingface-cli download Helsinki-NLP/opus-mt-en-ko --local-dir ./models/marianmt/opus-mt-en-ko

echo Downloading MarianMT Korean to English...
huggingface-cli download Helsinki-NLP/opus-mt-ko-en --local-dir ./models/marianmt/opus-mt-ko-en

:: Download XTTS v2 using TTS library
echo Downloading XTTS v2 (this may take a while)...
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=True)"
echo Moving XTTS files to models\xtts\xtts_v2...
mkdir models\xtts\xtts_v2
move %USERPROFILE%\.local\share\tts\tts_models--multilingual--multi-dataset--xtts_v2\* models\xtts\xtts_v2\

deactivate

echo Download complete! Models are in 'models/'.
pause
