import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import google.generativeai as genai
from PIL import Image, ImageTk
from io import BytesIO


class NanoBananaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🍌 NanoBanana AI Image Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

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
        """Erstellt die Haupt-GUI"""
        style = ttk.Style()
        style.theme_use('clam')

        dark_bg = '#2c3e50'

        style.configure('Dark.TButton',
                        font=('Arial', 11),
                        background='#2980b9',
                        foreground='white',
                        relief='flat',
                        padding=(10, 5))
        style.map('Dark.TButton',
                  background=[('active', '#3498db')])

        style.configure('DarkGreen.TButton',
                        font=('Arial', 11, 'bold'),
                        background='#1e8449',
                        foreground='white',
                        relief='flat',
                        padding=(10, 5))
        style.map('DarkGreen.TButton',
                  background=[('active', '#27ae60')])

        style.configure('Action.TButton',
                        font=('Arial', 12, 'bold'),
                        background='#2980b9',
                        foreground='white',
                        padding=(20, 5))
        style.map('Action.TButton',
                  background=[('active', '#3498db')])

        style.configure('DarkOrange.TButton',
                        font=('Arial', 11, 'bold'),
                        background='#d35400',
                        foreground='white',
                        relief='flat',
                        padding=(10, 5))
        style.map('DarkOrange.TButton',
                  background=[('active', '#e67e22')])

        # Korrigierte Layout-Reihenfolge
        header_frame = tk.Frame(self.root, bg='#34495e', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame, text="🍌 NanoBanana AI Image Studio", font=('Arial', 20, 'bold'),
            bg='#34495e', fg='white'
        )
        title_label.pack(pady=10)

        self.status_var = tk.StringVar(value="Bereit")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
            anchor=tk.W, bg='#7f8c8d', fg='white'
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame = tk.Frame(self.root, bg=dark_bg)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # <<< NEU: API Statusanzeige wieder hinzugefügt >>>
        status_frame = tk.Frame(main_frame, bg=dark_bg)
        status_frame.pack(fill='x', padx=10, pady=5)

        api_status = "✓ Verbunden" if self.api_key else "✗ Nicht verbunden"
        status_color = 'green' if self.api_key else 'red'
        tk.Label(
            status_frame, text=f"API Status: {api_status}", bg=dark_bg,
            fg=status_color, font=('Arial', 10)
        ).pack(side='left')
        # <<< ENDE NEUER CODE >>>

        control_frame = tk.Frame(main_frame, bg='#34495e', width=300)
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        control_frame.pack_propagate(False)

        tk.Label(
            control_frame, text="Funktion", font=('Arial', 14, 'bold'),
            bg='#34495e', fg='white'
        ).pack(pady=10)

        functions = [
            ("🖼️ Bild bearbeiten", self.edit_image_mode),
            ("🧹 Hintergrund entfernen", self.remove_background_mode),
            ("🏥 Bild restaurieren", self.restore_image_mode),
            ("🎨 Stil übertragen", self.style_transfer_mode),
            ("💬 Chat-Modus", self.chat_mode),
            ("📦 Produkt-Mockup", self.product_mockup_mode),
            ("📊 Marketing-Asset", self.marketing_asset_mode)
        ]

        for text, command in functions:
            btn = ttk.Button(
                control_frame,
                text=text,
                command=command,
                style='Dark.TButton'
            )
            btn.pack(fill='x', padx=10, pady=5)

        ttk.Button(
            control_frame,
            text="📂 Erstes Bild laden",
            command=self.load_image,
            style='DarkGreen.TButton'
        ).pack(fill='x', padx=10, pady=(10, 5))

        self.second_image_button = ttk.Button(
            control_frame,
            text="📂 Zweites Bild laden (Mockup)",
            command=self.load_second_image,
            style='DarkOrange.TButton'
        )
        self.second_image_button.pack(fill='x', padx=10, pady=(5, 10))
        self.second_image_button.pack_forget()

        workspace_frame = tk.Frame(main_frame, bg='#ecf0f1')
        workspace_frame.pack(side='right', fill='both', expand=True)

        prompt_frame = tk.Frame(workspace_frame, bg='#ecf0f1')
        prompt_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(
            prompt_frame, text="Prompt:", font=('Arial', 12, 'bold'),
            bg='#ecf0f1', fg='#2c3e50'
        ).pack(anchor='w')

        self.prompt_text = scrolledtext.ScrolledText(
            prompt_frame, height=4, font=('Arial', 11), wrap=tk.WORD,
            bg='white', fg='#2c3e50', insertbackground='#2c3e50'
        )
        self.prompt_text.pack(fill='x', pady=5)

        self.action_button = ttk.Button(
            prompt_frame,
            text="🚀 Ausführen",
            command=self.execute_action,
            style='Action.TButton'
        )
        self.action_button.pack(pady=10)

        image_canvas = tk.Canvas(workspace_frame, bg='#bdc3c7')
        image_scrollbar = ttk.Scrollbar(workspace_frame, orient="vertical", command=image_canvas.yview)
        scrollable_frame = tk.Frame(image_canvas, bg='#bdc3c7')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: image_canvas.configure(
                scrollregion=image_canvas.bbox("all")
            )
        )

        image_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        image_canvas.configure(yscrollcommand=image_scrollbar.set)

        image_scrollbar.pack(side="right", fill="y")
        image_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(
            scrollable_frame, text="Bildvorschau", font=('Arial', 12, 'bold'),
            bg='#bdc3c7', fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=5)

        self.image_label = tk.Label(
            scrollable_frame, text="Kein Bild geladen", bg='white', relief='sunken',
            font=('Arial', 10), fg='#2c3e50'
        )
        self.image_label.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.second_image_label = tk.Label(
            scrollable_frame, text="Zweites Bild: Nicht geladen", bg='white', relief='sunken',
            font=('Arial', 10), fg='#2c3e50'
        )
        self.second_image_label.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.second_image_label.pack_forget()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Erstes Bild auswählen",
            filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.current_image_path = file_path
                preview = self.current_image.copy()
                preview.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(preview)
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo
                self.status_var.set(f"Erstes Bild geladen: {os.path.basename(file_path)}")
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
                preview = self.second_image.copy()
                preview.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(preview)
                self.second_image_label.configure(image=photo, text="")
                self.second_image_label.image = photo
                self.status_var.set(f"Zweites Bild geladen: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden:\n{e}")

    def execute_action(self):
        if not self.model:
            messagebox.showerror("Fehler", "Keine API-Verbindung! Bitte API-Key setzen.")
            return
        prompt = self.prompt_text.get("1.0", tk.END).strip()
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

        self.action_button.configure(state='disabled')
        self.status_var.set("Verarbeite... Bitte warten...")

        threading.Thread(target=self.api_call_thread, args=(prompt, images_to_send), daemon=True).start()

    def api_call_thread(self, prompt, images):
        """Führt den API-Aufruf im Hintergrund aus."""
        try:
            response = self.model.generate_content([prompt] + images)
            self.root.after(0, self.handle_response, response)
        except Exception as e:
            self.root.after(0, self.handle_error, e)
        finally:
            self.root.after(0, lambda: self.action_button.configure(state='normal'))

    def handle_response(self, response):
        """Verarbeitet die API-Antwort auf dem Haupt-Thread."""
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
                            self.status_var.set(f"Bild gespeichert: {os.path.basename(save_path)}")
                            messagebox.showinfo("Erfolg", f"Bild erfolgreich gespeichert!\n{save_path}")
                        else:
                            self.status_var.set("Speichern abgebrochen.")

                        image_found = True
                        break
                if image_found:
                    break
        except Exception as e:
            self.status_var.set("Fehler bei der Antwortverarbeitung.")
            messagebox.showerror("Fehler", f"Fehler bei der Verarbeitung der API-Antwort:\n{e}")

        if not image_found:
            self.status_var.set("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

    def handle_error(self, error):
        """Behandelt Fehler auf dem Haupt-Thread."""
        self.status_var.set("Fehler bei der Verarbeitung.")
        messagebox.showerror("Fehler", f"Verarbeitung fehlgeschlagen:\n{error}")

    def edit_image_mode(self):
        self.current_mode = "edit"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Bearbeite das Bild gemäß der Beschreibung. Verbessere die Qualität und passe den Stil an.")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()

    def remove_background_mode(self):
        self.current_mode = "remove_background"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Entferne den Hintergrund vollständig und mache ihn transparent. Behalte nur das Hauptmotiv.")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()

    def restore_image_mode(self):
        self.current_mode = "restore"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Restauriere dieses alte/beschädigte Foto. Entferne Kratzer, Staub und Verblassungen. Verbessere Farben und Details.")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()

    def style_transfer_mode(self):
        self.current_mode = "style_transfer"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Übertrage den Stil eines Kunstwerks auf dieses Bild. Erhalte die grundlegende Komposition bei.")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()

    def chat_mode(self):
        self.current_mode = "chat"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", "Interaktiver Modus: Gib eine spezifische Bearbeitungsanweisung ein...")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()

    def product_mockup_mode(self):
        self.current_mode = "product_mockup"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Erstelle ein fotorealistisches Produkt-Mockup, indem du das Produkt aus dem ersten Bild nahtlos in die Szene des zweiten Bildes einfügst.")
        self.second_image_button.pack(fill='x', padx=10, pady=(5, 10))
        self.second_image_label.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def marketing_asset_mode(self):
        self.current_mode = "marketing_asset"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0",
                                "Verwandle dieses Produktbild in ein ansprechendes Marketing-Asset für soziale Medien. Füge einen aussagekräftigen Text-Slogan und passende Grafiken hinzu.")
        self.second_image_button.pack_forget()
        self.second_image_label.pack_forget()


def main():
    root = tk.Tk()
    app = NanoBananaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()