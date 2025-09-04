import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import threading
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os
API_URL = "http://127.0.0.1:5000/predict"

def detect_scream(file_path, result_label, detect_button):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(API_URL, files=files)
            data = response.json()
            if 'error' in data:
                result_label.config(text=f"Error: {data['error']}", fg="red")
            else:
                if data['is_scream']:
                    result_label.config(
                        text=f"Scream Detected! 😱\nProbability: {data['probability']*100:.2f}%",
                        fg="#ff4e50"
                    )
                else:
                    result_label.config(
                        text=f"No Scream Detected. 🙂\nProbability: {data['probability']*100:.2f}%",
                        fg="#f9d423"
                    )
    except Exception as e:
        result_label.config(text=f"Error: {e}", fg="red")
    finally:
        detect_button.config(state=tk.NORMAL)

def select_file(result_label, detect_button):
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac *.m4a"), ("All Files", "*.*")]
    )
    if file_path:
        result_label.config(text="Detecting...", fg="white")
        detect_button.config(state=tk.DISABLED)
        threading.Thread(target=detect_scream, args=(file_path, result_label, detect_button), daemon=True).start()

def record_audio(result_label, detect_button, duration=3, fs=44100):
    def _record():
        try:
            result_label.config(text="Recording... Speak now!", fg="#f9d423")
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                write(temp_wav.name, fs, audio)
                temp_wav_path = temp_wav.name
            result_label.config(text="Detecting...", fg="white")
            detect_scream(temp_wav_path, result_label, detect_button)
            os.remove(temp_wav_path)
        except Exception as e:
            result_label.config(text=f"Recording error: {e}", fg="red")
        finally:
            detect_button.config(state=tk.NORMAL)

    detect_button.config(state=tk.DISABLED)
    threading.Thread(target=_record, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Scream Detection Desktop App")
    root.geometry("420x340")
    root.configure(bg="#232526")

    title = tk.Label(root, text="Scream Detection", font=("Montserrat", 18, "bold"), bg="#232526", fg="white")
    title.pack(pady=(30, 10))

    result_label = tk.Label(root, text="", font=("Montserrat", 12), bg="#232526", fg="white", wraplength=350, justify="center")
    result_label.pack(pady=20)

    button_frame = tk.Frame(root, bg="#232526")
    button_frame.pack(pady=10)

    detect_button = tk.Button(
        button_frame, text="Select Audio File",
        font=("Montserrat", 12, "bold"),
        bg="#ff4e50", fg="white",
        activebackground="#f9d423", activeforeground="#232526",
        relief=tk.RAISED, bd=2,
        command=lambda: select_file(result_label, detect_button)
    )
    detect_button.grid(row=0, column=0, padx=10)

    record_button = tk.Button(
        button_frame, text="Record Audio (3s)",
        font=("Montserrat", 12, "bold"),
        bg="#f9d423", fg="#232526",
        activebackground="#ff4e50", activeforeground="#fff",
        relief=tk.RAISED, bd=2,
        command=lambda: record_audio(result_label, record_button)
    )
    record_button.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()