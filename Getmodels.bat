@echo off
echo Downloading models to the 'models' directory...

:: Create models directory structure
mkdir models
mkdir models\marianmt
mkdir models\xtts



:: Download XTTS v2 using TTS library
echo Downloading XTTS v2 (this may take a while)...
call venv\Scripts\activate
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=True)"
echo Moving XTTS files to models\xtts\xtts_v2...
mkdir models\xtts\xtts_v2
move %USERPROFILE%\.local\share\tts\tts_models--multilingual--multi-dataset--xtts_v2\* models\xtts\xtts_v2\
deactivate

echo Download complete! Models are in 'models/'.
pause