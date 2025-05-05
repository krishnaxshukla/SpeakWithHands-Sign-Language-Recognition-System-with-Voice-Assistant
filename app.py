import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import mediapipe as mp
import pyttsx3
import tensorflow as tf
from PIL import Image, ImageTk
import speech_recognition as sr
import time
import json

# Load model and labels
model = tf.keras.models.load_model("sign_language_model.h5")
with open("label_map.json", "r") as f:
    label_map = json.load(f)
label_map = {int(k): v for k, v in label_map.items()}

# Text-to-speech engine
engine = pyttsx3.init()
is_muted = False

def speak(text):
    if not is_muted:
        engine.say(text)
        engine.runAndWait()

# Global Flags
running = False
capture = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# GUI Setup
root = tk.Tk()
root.title("Sign Language Detection")
root.geometry("900x700")
root.configure(bg="#1e1e2f")

# Page 1 - Name Entry Page
name_frame = tk.Frame(root, bg="#1e1e2f")
name_label = tk.Label(name_frame, text="Enter Your Name", font=("Arial", 22), bg="#1e1e2f", fg="white")
name_label.pack(pady=20)

name_entry = tk.Entry(name_frame, font=("Arial", 18), justify='center')
name_entry.pack(pady=10)

submit_button = ttk.Button(name_frame, text="Submit", command=lambda: submit_name())
submit_button.pack(pady=20)

# Stickers/Logo
sticker_label = tk.Label(name_frame, text="👋 🎨 🎮", font=("Arial", 32), bg="#1e1e2f")
sticker_label.pack(pady=30)

# Page 2 - Voice Control Page
control_frame = tk.Frame(root, bg="#1e1e2f")
status_label = tk.Label(control_frame, text="Waiting for Your Command", fg="white", bg="#1e1e2f", font=("Arial", 18))
status_label.pack(pady=20)

voice_label = tk.Label(control_frame, text="", fg="yellow", bg="#1e1e2f", font=("Arial", 16))
voice_label.pack(pady=10)

btn_frame = tk.Frame(control_frame, bg="#1e1e2f")
btn_frame.pack(pady=20)

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    mute_btn.config(text="Unmute" if is_muted else "Mute")

def exit_app():
    global running
    running = False
    capture.release()
    root.destroy()

start_btn = ttk.Button(btn_frame, text="Start", command=lambda: start_model())
start_btn.grid(row=0, column=0, padx=10)

mute_btn = ttk.Button(btn_frame, text="Mute", command=toggle_mute)
mute_btn.grid(row=0, column=1, padx=10)

exit_btn = ttk.Button(btn_frame, text="Quit", command=exit_app)
exit_btn.grid(row=0, column=2, padx=10)

# Page 3 - Model Detection Page
video_frame = tk.Frame(root, bg="#1e1e2f")
video_label = tk.Label(video_frame)
video_label.pack(pady=10)

video_status_label = tk.Label(video_frame, text="Model Running...", fg="green", bg="#1e1e2f", font=("Arial", 16))
video_status_label.pack(pady=10)

video_voice_label = tk.Label(video_frame, text="", fg="yellow", bg="#1e1e2f", font=("Arial", 14))
video_voice_label.pack(pady=5)

# Navigation
user_name = ""
def submit_name():
    global user_name
    user_name = name_entry.get().strip()
    if user_name:
        speak(f"Welcome, {user_name}. Waiting for your command.")
        name_frame.pack_forget()
        control_frame.pack()

def start_model():
    global running
    running = True
    speak("Okay, opening the model for you.")
    control_frame.pack_forget()
    video_frame.pack()
    video_status_label.config(text="Model Running...")

    def detect():
        last_prediction = ""
        while running:
            success, frame = capture.read()
            if not success:
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    x_list = [lm.x for lm in handLms.landmark]
                    y_list = [lm.y for lm in handLms.landmark]
                    h, w, _ = frame.shape
                    xmin, xmax = int(min(x_list) * w), int(max(x_list) * w)
                    ymin, ymax = int(min(y_list) * h), int(max(y_list) * h)
                    cropped = frame[ymin:ymax, xmin:xmax]
                    if cropped.size == 0:
                        continue
                    try:
                        resized = cv2.resize(cropped, (64, 64))
                        input_img = np.expand_dims(resized, axis=0) / 255.0
                        predictions = model.predict(input_img)
                        class_id = np.argmax(predictions)
                        confidence = np.max(predictions)
                        label = label_map.get(class_id, "Unknown")

                        if label != last_prediction and confidence > 0.75:
                            last_prediction = label
                            video_status_label.config(text=f"Detected: {label}", fg="yellow")
                            speak(label)

                        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    except Exception as e:
                        print("Error in processing:", e)

            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_pil = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))
            video_label.config(image=img_pil)
            video_label.image = img_pil

    threading.Thread(target=detect, daemon=True).start()

# Voice Control Thread (shared across page 2 and 3)
def voice_control():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        with mic as source:
            voice_label.config(text="Listening...")
            video_voice_label.config(text="Listening...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print("Command received:", command)
                voice_label.config(text=f"You said: {command}")
                video_voice_label.config(text=f"You said: {command}")
                if "open" in command and not running:
                    speak("Okay, Opening the model for you")
                    root.after(0, start_model)
                elif "close" in command:
                    speak("Okay, closing the model.")
                    exit_app()
            except Exception:
                voice_label.config(text="Could not understand...")
                video_voice_label.config(text="")
                continue

threading.Thread(target=voice_control, daemon=True).start()

# Start from name entry
name_frame.pack()
root.mainloop()
