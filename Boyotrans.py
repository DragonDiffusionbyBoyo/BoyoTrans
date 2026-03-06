import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import whisper
from transformers import MarianTokenizer, MarianMTModel
from TTS.api import TTS
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
whisper_model = whisper.load_model("base", download_root="./models/whisper")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

# Chinese models
tokenizer_en_to_zh = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-en-zh", local_files_only=True)
model_en_to_zh     = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-en-zh", local_files_only=True)
tokenizer_zh_to_en = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-zh-en", local_files_only=True)
model_zh_to_en     = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-zh-en", local_files_only=True)

# Korean models
tokenizer_en_to_ko = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-en-ko", local_files_only=True)
model_en_to_ko     = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-en-ko", local_files_only=True)
tokenizer_ko_to_en = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-ko-en", local_files_only=True)
model_ko_to_en     = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-ko-en", local_files_only=True)

# ---------------------------------------------------------------------------
# Translation model map  (source_lang, target_lang) -> (tokenizer, model)
# ---------------------------------------------------------------------------
TRANSLATION_MODELS = {
    ("en",    "zh-cn"): (tokenizer_en_to_zh, model_en_to_zh),
    ("zh",    "en"):    (tokenizer_zh_to_en, model_zh_to_en),
    ("en",    "ko"):    (tokenizer_en_to_ko, model_en_to_ko),
    ("ko",    "en"):    (tokenizer_ko_to_en, model_ko_to_en),
}

# Whisper returns these codes; map them to our target language
TARGET_LANG_MAP = {
    "en": "zh-cn",   # English  -> Mandarin  (default pairing)
    "zh": "en",      # Mandarin -> English
    "ko": "en",      # Korean   -> English
}

# XTTS language codes
XTTS_LANG = {
    "en":    "en",
    "zh-cn": "zh-cn",
    "ko":    "ko",
}

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------
def transcribe_audio(audio_path):
    if not audio_path.lower().endswith(".wav"):
        raise ValueError("Input file must be .wav")
    result = whisper_model.transcribe(audio_path, language=None)
    return result["text"], result["language"]


def translate_text(text, source_lang, target_lang):
    # Nothing to do if same language family
    if source_lang == target_lang:
        return text
    if source_lang.startswith("zh") and target_lang.startswith("zh"):
        return text

    key = (source_lang, target_lang)
    if key not in TRANSLATION_MODELS:
        raise ValueError(
            f"No translation model for '{source_lang}' -> '{target_lang}'. "
            f"Supported pairs: {list(TRANSLATION_MODELS.keys())}"
        )

    tokenizer, model = TRANSLATION_MODELS[key]
    inputs     = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    translated = model.generate(**inputs)
    return tokenizer.batch_decode(translated, skip_special_tokens=True)[0]


def generate_translated_audio(translated_text, target_lang, original_audio, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    xtts_lang = XTTS_LANG.get(target_lang, "en")
    tts.tts_to_file(
        text=translated_text,
        file_path=output_path,
        speaker_wav=original_audio,
        language=xtts_lang,
    )
    return output_path


def translate_audio(input_audio, output_audio):
    source_text, source_lang = transcribe_audio(input_audio)
    print(f"Detected source language: {source_lang}")

    if source_lang not in TARGET_LANG_MAP:
        raise ValueError(
            f"Detected language '{source_lang}' is not supported. "
            f"Supported: English (en), Mandarin (zh), Korean (ko)."
        )

    target_lang     = TARGET_LANG_MAP[source_lang]
    translated_text = translate_text(source_text, source_lang, target_lang)
    print(f"Translated text: {translated_text}")

    final_audio = generate_translated_audio(translated_text, target_lang, input_audio, output_audio)
    print(f"Translated audio saved as: {final_audio}")
    return source_lang, target_lang, translated_text, final_audio


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
def create_gui():
    root = tk.Tk()
    root.title("Audio Translator - Dragon Diffusion UK")
    root.geometry("500x430")
    root.configure(bg="#f0f4f8")

    # Title
    tk.Label(
        root, text="Audio Translator",
        font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50"
    ).pack(pady=10)

    # Supported languages note
    tk.Label(
        root,
        text="Supports: English  ↔  Mandarin  |  Korean → English",
        font=("Arial", 9), bg="#f0f4f8", fg="#7f8c8d"
    ).pack()

    # Main frame
    main_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    main_frame.pack(pady=10, padx=20, fill="both", expand=True)

    status_text = scrolledtext.ScrolledText(
        main_frame, width=50, height=15, font=("Arial", 10), wrap=tk.WORD
    )
    status_text.pack(pady=10, padx=10)

    tk.Button(
        main_frame, text="Generate Translations",
        command=lambda: process_files(status_text),
        font=("Arial", 12, "bold"), bg="#3498db", fg="white",
        relief="flat", padx=10, pady=5
    ).pack(pady=10)

    # Branding
    tk.Label(
        root, text="Dragon Diffusion UK Tools",
        font=("Arial", 10, "italic"), bg="#f0f4f8", fg="#7f8c8d"
    ).pack(side="bottom", pady=5)

    # ------------------------------------------------------------------
    def process_files(status_widget):
        input_dir  = "./input"
        output_dir = "./output"
        os.makedirs(input_dir,  exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        status_widget.delete(1.0, tk.END)
        status_widget.insert(tk.END, "Starting translation process...\n\n")

        wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]
        if not wav_files:
            status_widget.insert(tk.END, "No WAV files found in input folder.\n")
            return

        for filename in wav_files:
            input_file  = os.path.join(input_dir,  filename)
            output_file = os.path.join(output_dir, f"translated_{filename}")
            status_widget.insert(tk.END, f"Processing {filename}...\n")
            root.update()

            try:
                source_lang, target_lang, translated_text, final_audio = translate_audio(
                    input_file, output_file
                )
                status_widget.insert(
                    tk.END,
                    f"  Detected : {source_lang}\n"
                    f"  Target   : {target_lang}\n"
                    f"  Text     : {translated_text}\n"
                    f"  Saved as : {os.path.basename(final_audio)}\n\n"
                )
            except Exception as e:
                status_widget.insert(tk.END, f"  Error: {str(e)}\n\n")
                messagebox.showerror("Error", f"Failed to process {filename}:\n{str(e)}")

        status_widget.insert(tk.END, "All files processed!\n")
        messagebox.showinfo("Complete", "Translation process completed!")

    root.mainloop()


if __name__ == "__main__":
    create_gui()
