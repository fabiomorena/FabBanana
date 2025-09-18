import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import google.generativeai as genai
from PIL import Image, ImageTk
from io import BytesIO
import customtkinter as ctk

# Setzt das Standard-Erscheinungsbild und das Farbschema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NanoBananaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍌 NanoBanana AI Image Studio")
        self.geometry("1200x800")

        # API Key Status
        self.api_key = os.environ.get("GOOGLE_API_KEY", "")
        self.model = None
        self.setup_model()

        # Aktuelle Bilddaten
        self.current_image = None
        self.second_image = None
        self.current_image_path = None
        self.second_image_path = None

        # Zustand der Anwendung
        self.current_mode = "edit"

        # GUI erstellen
        self.setup_gui()

    def setup_model(self):
        """Initialisiert das Gemini-Modell"""
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            except Exception as e:
                print(f"Modell-Setup Fehler: {e}")

    def setup_gui(self):
        """Erstellt die Haupt-GUI mit CustomTkinter"""

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        control_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        workspace_frame = ctk.CTkFrame(self, corner_radius=10)
        workspace_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        workspace_frame.grid_rowconfigure(1, weight=1)
        workspace_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(control_frame, text="🍌 NanoBanana", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20, padx=20)

        # NEUE FUNKTION HIER HINZUGEFÜGT
        functions = [
            ("Bild bearbeiten", self.edit_image_mode),
            ("Objekt entfernen", self.object_removal_mode),  # <-- NEU
            ("Hintergrund entfernen", self.remove_background_mode),
            ("Bild restaurieren", self.restore_image_mode),
            ("Stil übertragen", self.style_transfer_mode),
            ("Chat-Modus", self.chat_mode),
            ("Produkt-Mockup", self.product_mockup_mode),
            ("Marketing-Asset", self.marketing_asset_mode)
        ]

        for text, command in functions:
            btn = ctk.CTkButton(control_frame, text=text, command=command)
            btn.pack(fill='x', padx=10, pady=5)

        ctk.CTkButton(control_frame, text="Erstes Bild laden", command=self.load_image, fg_color="#28a745",
                      hover_color="#218838").pack(fill='x', padx=10, pady=(20, 5))

        self.second_image_button = ctk.CTkButton(control_frame, text="Zweites Bild laden",
                                                 command=self.load_second_image, fg_color="#ffc107",
                                                 hover_color="#e0a800", text_color="black")

        api_status = "✓ Verbunden" if self.api_key else "✗ Nicht verbunden"
        api_color = "green" if self.api_key else "red"
        api_status_label = ctk.CTkLabel(control_frame, text=f"API: {api_status}", text_color=api_color)
        api_status_label.pack(side="bottom", pady=10)

        prompt_frame = ctk.CTkFrame(workspace_frame)
        prompt_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        prompt_frame.grid_columnconfigure(0, weight=1)

        self.prompt_text = ctk.CTkTextbox(prompt_frame, height=100, corner_radius=8, font=("Arial", 14))
        self.prompt_text.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.action_button = ctk.CTkButton(prompt_frame, text="🚀 Ausführen", command=self.execute_action, height=40,
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.action_button.grid(row=0, column=1, padx=10, pady=5)

        image_frame = ctk.CTkScrollableFrame(workspace_frame, label_text="Bildvorschau")
        image_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.image_label = ctk.CTkLabel(image_frame, text="Kein Bild geladen")
        self.image_label.pack(fill='both', expand=True, padx=10, pady=10)

        self.second_image_label = ctk.CTkLabel(image_frame, text="")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Erstes Bild auswählen",
            filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.current_image_path = file_path
                ctk_image = ctk.CTkImage(light_image=self.current_image, size=(400, 300))
                self.image_label.configure(image=ctk_image, text="")
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    def load_second_image(self):
        file_path = filedialog.askopenfilename(
            title="Zweites Bild auswählen",
            filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                self.second_image = Image.open(file_path)
                self.second_image_path = file_path
                ctk_image = ctk.CTkImage(light_image=self.second_image, size=(400, 300))
                self.second_image_label.configure(image=ctk_image, text="")
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    def execute_action(self):
        if not self.model:
            messagebox.showerror("Fehler", "Keine API-Verbindung! Bitte API-Key setzen.")
            return
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Prompt ein!")
            return

        if self.current_mode == "product_mockup":
            if not self.current_image or not self.second_image:
                messagebox.showerror("Fehler", "Für Produkt-Mockup benötigen Sie zwei Bilder!")
                return
            images_to_send = [self.current_image, self.second_image]
        else:
            if not self.current_image:
                messagebox.showerror("Fehler", "Bitte laden Sie zuerst ein Bild!")
                return
            images_to_send = [self.current_image]

        self.action_button.configure(state='disabled', text="Verarbeite...")
        threading.Thread(target=self.api_call_thread, args=(prompt, images_to_send), daemon=True).start()

    def api_call_thread(self, prompt, images):
        try:
            response = self.model.generate_content([prompt] + images)
            self.after(0, self.handle_response, response)
        except Exception as e:
            self.after(0, self.handle_error, e)
        finally:
            self.after(0, lambda: self.action_button.configure(state='normal', text="🚀 Ausführen"))

    def handle_response(self, response):
        image_found = False
        try:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        image_data = part.inline_data.data
                        result_image = Image.open(BytesIO(image_data))
                        save_path = filedialog.asksaveasfilename(
                            defaultextension=".png",
                            filetypes=[("PNG Dateien", "*.png"), ("Alle Dateien", "*.*")]
                        )
                        if save_path:
                            result_image.save(save_path)
                            messagebox.showinfo("Erfolg", f"Bild erfolgreich gespeichert!\n{save_path}")
                        image_found = True
                        break
                if image_found:
                    break
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Verarbeitung der API-Antwort:\n{e}")

        if not image_found:
            messagebox.showwarning("Kein Bild", "Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

    def handle_error(self, error):
        messagebox.showerror("Fehler", f"Verarbeitung fehlgeschlagen:\n{error}")

    def set_mode(self, mode, prompt_text, show_second_image=False):
        self.current_mode = mode
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", prompt_text)

        if show_second_image:
            self.second_image_button.pack(fill='x', padx=10, pady=(5, 10))
            self.second_image_label.pack(fill='both', expand=True, padx=10, pady=10)
        else:
            self.second_image_button.pack_forget()
            self.second_image_label.pack_forget()
            self.second_image = None
            self.second_image_label.configure(image=None)

    def edit_image_mode(self):
        self.set_mode("edit",
                      "Bearbeite das Bild gemäß der Beschreibung. Verbessere die Qualität und passe den Stil an.")

    # NEUE METHODE HIER HINZUGEFÜGT
    def object_removal_mode(self):  # <-- NEU
        self.set_mode("object_removal",
                      "Beschreibe das Objekt, das du entfernen möchtest, so präzise wie möglich. Beispiel: 'Entferne den umgefallenen Pappbecher auf dem Bürgersteig'.")

    def remove_background_mode(self):
        self.set_mode("remove_background",
                      "Entferne den Hintergrund vollständig und mache ihn transparent. Behalte nur das Hauptmotiv.")

    def restore_image_mode(self):
        self.set_mode("restore", "Restauriere dieses alte/beschädigte Foto. Entferne Kratzer und verbessere Farben.")

    def style_transfer_mode(self):
        self.set_mode("style_transfer", "Übertrage den Stil eines Kunstwerks auf dieses Bild.")

    def chat_mode(self):
        self.set_mode("chat", "Interaktiver Modus: Gib eine spezifische Bearbeitungsanweisung ein...")

    def product_mockup_mode(self):
        self.set_mode("product_mockup",
                      "Erstelle ein fotorealistisches Produkt-Mockup, indem du das Produkt aus dem ersten Bild nahtlos in die Szene des zweiten Bildes einfügst.",
                      show_second_image=True)

    def marketing_asset_mode(self):
        self.set_mode("marketing_asset",
                      "Verwandle dieses Produktbild in ein ansprechendes Marketing-Asset für soziale Medien.")


if __name__ == "__main__":
    app = NanoBananaGUI()
    app.mainloop()