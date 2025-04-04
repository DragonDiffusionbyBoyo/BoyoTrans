import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import whisper
from transformers import MarianTokenizer, MarianMTModel
from TTS.api import TTS
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

whisper_model = whisper.load_model("base", download_root="./models/whisper")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
tokenizer_en_to_zh = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-en-zh", local_files_only=True)
model_en_to_zh = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-en-zh", local_files_only=True)
tokenizer_zh_to_en = MarianTokenizer.from_pretrained("./models/marianmt/opus-mt-zh-en", local_files_only=True)
model_zh_to_en = MarianMTModel.from_pretrained("./models/marianmt/opus-mt-zh-en", local_files_only=True)

def transcribe_audio(audio_path):
    if not audio_path.lower().endswith(".wav"):
        raise ValueError("Input file must be .wav")
    result = whisper_model.transcribe(audio_path, language=None)
    return result["text"], result["language"]

def translate_text(text, source_lang, target_lang):
    if source_lang == target_lang or (source_lang.startswith("zh") and target_lang.startswith("zh")):
        return text
    if source_lang == "en" and target_lang == "zh-cn":
        tokenizer = tokenizer_en_to_zh
        model = model_en_to_zh
    elif source_lang == "zh" and target_lang == "en":
        tokenizer = tokenizer_zh_to_en
        model = model_zh_to_en
    else:
        raise ValueError("Only 'en' to 'zh-cn' or 'zh' to 'en' supported.")
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    translated = model.generate(**inputs)
    return tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

def generate_translated_audio(translated_text, target_lang, original_audio, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tts.tts_to_file(text=translated_text, file_path=output_path, speaker_wav=original_audio, language=target_lang)
    return output_path

def translate_audio(input_audio, output_audio):
    source_text, source_lang = transcribe_audio(input_audio)
    print(f"Detected source language: {source_lang}")
    
    if source_lang == "en":
        target_lang = "zh-cn"
    elif source_lang == "zh":
        target_lang = "en"
    else:
        raise ValueError("Source language must be 'en' or 'zh'.")
    
    translated_text = translate_text(source_text, source_lang, target_lang)
    print(f"Translated text: {translated_text}")
    final_audio = generate_translated_audio(translated_text, target_lang, input_audio, output_audio)
    print(f"Translated audio saved as: {final_audio}")
    return source_lang, translated_text, final_audio

# GUI Implementation
def create_gui():
    root = tk.Tk()
    root.title("Audio Translator - Dragon Diffusion UK")
    root.geometry("500x400")
    root.configure(bg="#f0f4f8")  # Light background

    # Title
    title_label = tk.Label(root, text="Audio Translator", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50")
    title_label.pack(pady=10)

    # Frame for content
    main_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    main_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Status display using scrolled text
    status_text = scrolledtext.ScrolledText(main_frame, width=50, height=15, font=("Arial", 10), wrap=tk.WORD)
    status_text.pack(pady=10, padx=10)

    # Generate button
    generate_button = tk.Button(main_frame, text="Generate Translations", command=lambda: process_files(status_text),
                                font=("Arial", 12, "bold"), bg="#3498db", fg="white", relief="flat", padx=10, pady=5)
    generate_button.pack(pady=10)

    # Company branding
    company_label = tk.Label(root, text="Dragon Diffusion UK Tools", font=("Arial", 10, "italic"), bg="#f0f4f8", fg="#7f8c8d")
    company_label.pack(side="bottom", pady=5)

    def process_files(status_widget):
        input_dir = "D:/AudioTranslater/input"
        output_dir = "D:/AudioTranslater/output"
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        status_widget.delete(1.0, tk.END)  # Clear previous text
        status_widget.insert(tk.END, "Starting translation process...\n\n")

        wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]
        if not wav_files:
            status_widget.insert(tk.END, "No WAV files found in input folder.\n")
            return

        for filename in wav_files:
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, f"translated_{filename}")
            status_widget.insert(tk.END, f"Processing {filename}...\n")
            root.update()  # Update GUI to show progress

            try:
                source_lang, translated_text, final_audio = translate_audio(input_file, output_file)
                status_widget.insert(tk.END,
                                     f"Detected: {source_lang}\n"
                                     f"Translated: {translated_text}\n"
                                     f"Saved as: {os.path.basename(final_audio)}\n\n")
            except Exception as e:
                status_widget.insert(tk.END, f"Error with {filename}: {str(e)}\n\n")
                messagebox.showerror("Error", f"Failed to process {filename}: {str(e)}")

        status_widget.insert(tk.END, "All files processed!\n")
        messagebox.showinfo("Complete", "Translation process completed!")

    root.mainloop()

if __name__ == "__main__":
    create_gui()