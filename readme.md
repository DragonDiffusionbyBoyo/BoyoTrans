This project provides a Python-based audio translation tool that converts English to Mandarin Chinese and vice versa. It uses Whisper for transcription, MarianMT for translation, and XTTS v2 for text-to-speech generation. The tool features a simple GUI for processing all WAV files in an input folder.

## Features
- Automatically detects audio language (English or Mandarin).
- Translates English → Mandarin or Mandarin → English.
- Generates translated audio files with a modern GUI interface.
- Batch processes all `.wav` files in the `input/` folder.

## Requirements
- **Python**: Version 3.10.11 (required).
- **Operating System**: Windows (due to `.bat` file usage).
- **GPU (Optional)**: CUDA 12.4 support for faster processing (PyTorch configured for `cu124`).

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/audio-translator.git
   cd audio-translator
   ```

2. **Run the Setup Script**:
   - Ensure Python 3.10.11 is installed and added to your PATH.
   - Double-click `setup_audio_translater.bat` or run it from the command line:
     ```bash
     setup_audio_translater.bat
     ```
   - This script:
     - Creates a virtual environment (`venv`).
     - Installs dependencies from `requirements.txt` and PyTorch with CUDA 12.4.
     - Downloads required models to `models/` (Whisper, MarianMT, XTTS v2).

3. **Prepare Input Files**:
   - Place your `.wav` audio files in the `input/` folder (created automatically if it doesn’t exist).

## Usage
1. **Run the Application**:
   - After setup, run the Python script:
     ```bash
     venv\Scripts\python boyotrans.py
     ```
   - A GUI titled "Audio Translator - Dragon Diffusion UK" will open.

2. **Translate Audio**:
   - Click "Generate Translations" to process all `.wav` files in the `input/` folder.
   - Progress is displayed in the GUI, and translated audio files are saved to `output/` as `translated_<filename>.wav`.

## Project Structure
- `boyotrans.py`: Main Python script with GUI and translation logic.
- `setup_audio_translater.bat`: Setup script for environment and model downloads.
- `requirements.txt`: List of Python dependencies (excluding PyTorch, handled separately).
- `input/`: Folder for input WAV files.
- `output/`: Folder for translated audio outputs.
- `models/`: Folder for downloaded models (auto-populated by setup).

## Dependencies
- `huggingface_hub`: For model downloads.
- `TTS`: For text-to-speech (XTTS v2).
- `torch==2.4.1`, `torchaudio==2.4.1`, `torchvision==0.19.1`: PyTorch with CUDA 12.4.
- `transformers`: For MarianMT models.
- `whisper`: For audio transcription.

## Notes
- If you don’t have a CUDA-compatible GPU, edit `setup_audio_translater.bat` to replace `gpu=True` with `gpu=False` in the XTTS download line and adjust PyTorch to a CPU version.
- Ensure your WAV files are properly formatted (e.g., mono, 16-bit PCM).

## Credits
Developed by Andrew Baines under Dragon Diffusion UK Tools.
