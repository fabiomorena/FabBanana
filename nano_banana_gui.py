import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import google.generativeai as genai
from PIL import Image, ImageOps
from io import BytesIO
import customtkinter as ctk
import glob

# --- Modernes UI-Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppFont:
    FAMILY = "Inter"
    MAIN_SIZE = 13
    TITLE_SIZE = 22
    WEIGHT_BOLD = "bold"


class AppTheme:
    BACKGROUND = "#4c4f52"
    CONTROL_FRAME_BG = "#505357"
    CONTROL_FRAME_BORDER = "#3E4044"
    BUTTON_BG = "#5E6165"
    BUTTON_HOVER = "#797C80"
    BUTTON_BORDER = "#A0A3A7"
    WORKSPACE_BG = "#6F7276"
    WORKSPACE_BORDER = "#B0B3B7"
    TEXTBOX_BG = "#808387"
    TEXTBOX_BORDER = "#B0B3B7"
    ACCENT_COLOR = "#5E6165"
    ACCENT_HOVER = "#797C80"
    ACCENT_BORDER = "#A0A3A7"
    TEXT_COLOR = "#F5F5F5"
    IMAGE_BORDER_COLOR = "#FFFFFF"
    API_STATUS_CONNECTED = "#32CD32"
    API_STATUS_DISCONNECTED = "#FF6347"


class NanoBananaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🍌 NanoBanana AI Image Studio (Final)")
        self.geometry("1200x800")
        self.configure(fg_color=AppTheme.BACKGROUND)

        self.api_key = os.environ.get("GOOGLE_API_KEY", "")
        self.model = None
        self.setup_model()

        self.current_image = None
        self.second_image = None
        self.current_mode = "text_to_image"

        self.setup_gui()
        self.text_to_image_mode()

    def setup_model(self):
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            except Exception as e:
                print(f"Modell-Setup Fehler: {e}")

    def setup_gui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        control_frame = ctk.CTkFrame(self, width=250, corner_radius=10, fg_color=AppTheme.CONTROL_FRAME_BG,
                                     border_width=2, border_color=AppTheme.CONTROL_FRAME_BORDER)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        workspace_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=AppTheme.WORKSPACE_BG, border_width=1,
                                       border_color=AppTheme.WORKSPACE_BORDER)
        workspace_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        workspace_frame.grid_rowconfigure(1, weight=1)
        workspace_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(control_frame, text="🍌 FabBanana",
                                   font=(AppFont.FAMILY, AppFont.TITLE_SIZE, AppFont.WEIGHT_BOLD),
                                   text_color=AppTheme.TEXT_COLOR)
        title_label.pack(pady=20, padx=20)

        functions = [
            ("Text zu Bild", self.text_to_image_mode), ("Bild erweitern (Outpaint)", self.uncropping_mode),
            ("Avatar erstellen", self.avatar_mode), ("Bild bearbeiten", self.edit_image_mode),
            ("Objekt entfernen", self.object_removal_mode), ("Hintergrund entfernen", self.remove_background_mode),
            ("Bild restaurieren", self.restore_image_mode), ("Bild hochskalieren", self.upscaling_mode),
            ("Wasserzeichen hinzufügen", self.watermark_mode), ("Stil übertragen", self.style_transfer_mode),
            ("Chat-Modus", self.chat_mode), ("Produkt-Mockup", self.product_mockup_mode),
            ("Marketing-Asset", self.marketing_asset_mode), ("Stapelverarbeitung", self.batch_mode),
        ]

        for text, command in functions:
            btn = ctk.CTkButton(control_frame, text=text, command=command, font=(AppFont.FAMILY, AppFont.MAIN_SIZE),
                                fg_color=AppTheme.BUTTON_BG, hover_color=AppTheme.BUTTON_HOVER,
                                text_color=AppTheme.TEXT_COLOR, corner_radius=8, border_width=1,
                                border_color=AppTheme.BUTTON_BORDER)
            btn.pack(fill='x', padx=10, pady=4)

        self.load_image_button = ctk.CTkButton(control_frame, text="Bild laden", command=self.load_image,
                                               font=(AppFont.FAMILY, AppFont.MAIN_SIZE), fg_color=AppTheme.BUTTON_BG,
                                               hover_color=AppTheme.BUTTON_HOVER, border_width=1,
                                               border_color=AppTheme.BUTTON_BORDER)
        self.load_image_button.pack(fill='x', padx=10, pady=(20, 5))

        self.second_image_button = ctk.CTkButton(control_frame, text="Logo/Wasserzeichen laden",
                                                 command=self.load_second_image,
                                                 font=(AppFont.FAMILY, AppFont.MAIN_SIZE), fg_color=AppTheme.BUTTON_BG,
                                                 hover_color=AppTheme.BUTTON_HOVER, border_width=1,
                                                 border_color=AppTheme.BUTTON_BORDER)

        api_status_label = ctk.CTkLabel(control_frame,
                                        text=f"API: {'✓ Verbunden' if self.api_key else '✗ Nicht verbunden'}",
                                        text_color=AppTheme.API_STATUS_CONNECTED if self.api_key else AppTheme.API_STATUS_DISCONNECTED,
                                        font=(AppFont.FAMILY, AppFont.MAIN_SIZE, AppFont.WEIGHT_BOLD))
        api_status_label.pack(side="bottom", pady=10)

        prompt_frame = ctk.CTkFrame(workspace_frame, fg_color="transparent")
        prompt_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        prompt_frame.grid_columnconfigure(0, weight=1)

        self.prompt_text = ctk.CTkTextbox(prompt_frame, height=100, corner_radius=12, font=(AppFont.FAMILY, 14),
                                          fg_color=AppTheme.TEXTBOX_BG, border_width=1,
                                          border_color=AppTheme.TEXTBOX_BORDER, text_color=AppTheme.TEXT_COLOR)
        self.prompt_text.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.action_button = ctk.CTkButton(prompt_frame, text="🚀 Generieren", command=self.execute_action, height=40,
                                           font=(AppFont.FAMILY, 14, AppFont.WEIGHT_BOLD),
                                           fg_color=AppTheme.ACCENT_COLOR, hover_color=AppTheme.ACCENT_HOVER,
                                           border_width=1, border_color=AppTheme.ACCENT_BORDER)
        self.action_button.grid(row=0, column=1, padx=10, pady=5)

        self.image_frame = ctk.CTkScrollableFrame(workspace_frame, label_text="Vorschau",
                                                  label_font=(AppFont.FAMILY, AppFont.MAIN_SIZE),
                                                  fg_color="transparent", border_width=1,
                                                  border_color=AppTheme.BUTTON_BORDER)
        self.image_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.image_label = ctk.CTkLabel(self.image_frame, text="Hier erscheint das generierte Bild",
                                        font=(AppFont.FAMILY, AppFont.MAIN_SIZE), text_color=AppTheme.TEXT_COLOR)
        self.image_label.pack(fill='both', expand=True, padx=10, pady=10)
        self.second_image_label = ctk.CTkLabel(self.image_frame, text="")

    def display_image_with_aspect_ratio(self, pil_image, image_label, max_w=600, max_h=450):
        pil_image_with_border = ImageOps.expand(pil_image, border=2, fill=AppTheme.IMAGE_BORDER_COLOR)

        img_w, img_h = pil_image_with_border.size
        ratio = min(max_w / img_w, max_h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        ctk_image = ctk.CTkImage(light_image=pil_image_with_border, size=(new_w, new_h))
        image_label.configure(image=ctk_image, text="")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.display_image_with_aspect_ratio(self.current_image, self.image_label)
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    def load_second_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            try:
                self.second_image = Image.open(file_path)
                self.display_image_with_aspect_ratio(self.second_image, self.second_image_label)
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    def execute_action(self):
        if not self.model:
            messagebox.showerror("Fehler", "Keine API-Verbindung!")
            return
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showerror("Fehler", "Bitte Prompt eingeben!")
            return

        if self.current_mode == "batch":
            self.execute_batch_processing(prompt)
            return

        images_to_send = []
        if self.current_mode != "text_to_image":
            if not self.current_image:
                messagebox.showerror("Fehler", "Bitte laden Sie zuerst ein Hauptbild!")
                return
            images_to_send.append(self.current_image)

        if self.current_mode in ["product_mockup", "watermark"]:
            if not self.second_image:
                messagebox.showerror("Fehler", "Für diesen Modus wird ein zweites Bild benötigt!")
                return
            images_to_send.append(self.second_image)

        content_to_send = [prompt] + images_to_send
        self.action_button.configure(state='disabled', text="Verarbeite...")
        threading.Thread(target=self.api_call_thread, args=(content_to_send,), daemon=True).start()

    def api_call_thread(self, content):
        try:
            response = self.model.generate_content(content)
            self.after(0, self.handle_response, response)
        except Exception as e:
            self.after(0, self.handle_error, e)
        finally:
            self.after(0, self.set_action_button_text)

    def handle_response(self, response):
        image_found = False
        try:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        result_image = Image.open(BytesIO(part.inline_data.data))
                        self.display_image_with_aspect_ratio(result_image, self.image_label)
                        self.current_image = result_image

                        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                                 filetypes=[("PNG Files", "*.png")])
                        if save_path:
                            result_image.save(save_path)
                            messagebox.showinfo("Erfolg", f"Bild gespeichert: {save_path}")
                        image_found = True
                        break
                if image_found: break
        except Exception as e:
            messagebox.showerror("Fehler", f"Antwort konnte nicht verarbeitet werden:\n{e}")
        if not image_found:
            messagebox.showwarning("Kein Bild", "Keine Bilddaten in der Antwort gefunden.")

    def handle_error(self, error):
        messagebox.showerror("API Fehler", f"Verarbeitung fehlgeschlagen:\n{error}")

    def set_action_button_text(self):
        mode_texts = {"text_to_image": "Generieren", "uncropping": "Erweitern", "avatar": "Erstellen",
                      "watermark": "Hinzufügen", "batch": "Ordner auswählen..."}
        text = mode_texts.get(self.current_mode, "Ausführen")
        self.action_button.configure(state='normal', text=f"🚀 {text}")

    def set_mode(self, mode, prompt_text, needs_first_image=True, needs_second_image=False,
                 second_image_text="Zweites Bild laden"):
        self.current_mode = mode
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", prompt_text)
        self.set_action_button_text()

        if needs_first_image:
            self.load_image_button.pack(fill='x', padx=10, pady=(20, 5))
            self.load_image_button.configure(text="Hauptbild laden")
        else:
            self.load_image_button.pack_forget()

        if needs_second_image:
            self.second_image_button.pack(fill='x', padx=10, pady=5)
            self.second_image_button.configure(text=second_image_text)
            self.second_image_label.pack(fill='both', expand=True, padx=10, pady=10)
        else:
            self.second_image_button.pack_forget()
            self.second_image_label.pack_forget()

    def text_to_image_mode(self):
        self.set_mode("text_to_image", "Ein fotorealistisches Bild von...", needs_first_image=False)

    def uncropping_mode(self):
        self.set_mode("uncropping", "Erweitere dieses Bild an allen Seiten...")

    def avatar_mode(self):
        self.set_mode("avatar", "Verwandle die Person in einen Avatar im Stil von...")

    def edit_image_mode(self):
        self.set_mode("edit", "Bearbeite das Bild...")

    def object_removal_mode(self):
        self.set_mode("object_removal", "Entferne das folgende Objekt: ...")

    def remove_background_mode(self):
        self.set_mode("remove_background", "Entferne den Hintergrund.")

    def restore_image_mode(self):
        self.set_mode("restore", "Restauriere dieses alte Foto.")

    def upscaling_mode(self):
        self.set_mode("upscaling", "Skaliere dieses Bild hoch und verbessere Details.")

    def watermark_mode(self):
        self.set_mode("watermark", "Platziere das Wasserzeichen (Bild 2) unten rechts...", needs_second_image=True,
                      second_image_text="Wasserzeichen laden")

    def style_transfer_mode(self):
        self.set_mode("style_transfer", "Übertrage den Stil von [Künstler] auf dieses Bild.")

    def chat_mode(self):
        self.set_mode("chat", "Interaktiver Modus...")

    def product_mockup_mode(self):
        self.set_mode("product_mockup", "Füge das Produkt (Bild 1) in die Szene (Bild 2) ein.", needs_second_image=True,
                      second_image_text="Hintergrund laden")

    def marketing_asset_mode(self):
        self.set_mode("marketing_asset", "Erstelle ein Marketing-Asset mit dem Slogan: ...")

    def batch_mode(self):
        self.set_mode("batch", "Entferne den Hintergrund von allen Bildern.", needs_first_image=False)

    def execute_batch_processing(self, prompt):
        input_dir = filedialog.askdirectory(title="Wähle den Ordner mit den Originalbildern")
        if not input_dir: return
        output_dir = filedialog.askdirectory(title="Wähle den Ordner für die bearbeiteten Bilder")
        if not output_dir: return

        image_files = glob.glob(os.path.join(input_dir, '*.png')) + glob.glob(
            os.path.join(input_dir, '*.jpg')) + glob.glob(os.path.join(input_dir, '*.jpeg'))
        if not image_files:
            messagebox.showinfo("Info", "Keine Bilder im ausgewählten Ordner gefunden.")
            return

        self.action_button.configure(state='disabled', text="Verarbeite...")
        threading.Thread(target=self.batch_thread, args=(prompt, image_files, output_dir), daemon=True).start()

    def batch_thread(self, prompt, image_files, output_dir):
        total = len(image_files)
        for i, image_path in enumerate(image_files):
            try:
                print(f"Verarbeite Bild {i + 1}/{total}: {os.path.basename(image_path)}")
                image = Image.open(image_path)
                response = self.model.generate_content([prompt, image])
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            image_data = part.inline_data.data
                            processed_image = Image.open(BytesIO(image_data))
                            base_filename = os.path.splitext(os.path.basename(image_path))[0]
                            output_filename = f"{base_filename}_processed.png"
                            processed_image.save(os.path.join(output_dir, output_filename), "PNG")
                            break
                    break
            except Exception as e:
                print(f"Fehler bei {os.path.basename(image_path)}: {e}")
        self.after(0, self.batch_finished, output_dir)

    def batch_finished(self, output_dir):
        messagebox.showinfo("Erfolg",
                            f"Stapelverarbeitung abgeschlossen! Die Bilder wurden in '{output_dir}' gespeichert.")
        self.set_action_button_text()


if __name__ == "__main__":
    app = NanoBananaGUI()
    app.mainloop()