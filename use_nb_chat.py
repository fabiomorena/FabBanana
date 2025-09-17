import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# --- Schritt 1: Konfiguration ---
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("Fehler: Die Umgebungsvariable 'GOOGLE_API_KEY' wurde nicht gefunden.")
    print("Bitte setzen Sie die Variable und versuchen Sie es erneut.")
    exit()

# --- Schritt 2: Modell konfigurieren ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

# --- Schritt 3: Initiales Bild laden ---
initial_image_path = "katze.png"  # Passe ggf. den Namen an
try:
    current_image = Image.open(initial_image_path)
    print(f"Initiales Bild '{initial_image_path}' erfolgreich geladen.")
    print("Willkommen beim Conversational Image Editing!")
    print("Sie können jetzt Anweisungen geben, um das Bild zu bearbeiten.")
    print("Tippen Sie 'quit' oder 'exit' zum Beenden.")
    print("-" * 50)
except FileNotFoundError:
    print(f"Fehler: Das initiale Bild '{initial_image_path}' wurde nicht gefunden.")
    exit()

# --- Schritt 4: Chat-Loop ---
conversation_history = []
image_counter = 1

while True:
    # Benutzer-Eingabe abfragen
    user_input = input("\nIhre Anweisung für die Bildbearbeitung: ").strip()

    if user_input.lower() in ['quit', 'exit', 'beenden']:
        print("Chat beendet. Vielen Dank!")
        break

    if not user_input:
        print("Bitte geben Sie eine gültige Anweisung ein.")
        continue

    print("Verarbeite Ihre Anweisung... Bitte warten.")

    try:
        # API-Anfrage mit aktuellem Bild und Benutzeranweisung
        response = model.generate_content([user_input, current_image])

        # Antwort verarbeiten
        image_found = False
        text_response = ""

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    text_response += part.text + "\n"
                elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    print("Neues bearbeitetes Bild erhalten, verarbeite...")
                    image_data = part.inline_data.data
                    current_image = Image.open(BytesIO(image_data))

                    # Neues Bild speichern
                    output_filename = f"bearbeitetes_bild_{image_counter}.png"
                    current_image.save(output_filename)
                    print(f"Neues Bild erfolgreich als '{output_filename}' gespeichert.")
                    image_counter += 1
                    image_found = True
                    break
            if image_found:
                break

        # Textantwort anzeigen
        if text_response:
            print(f"\nAI Antwort: {text_response.strip()}")
        elif not image_found:
            print(
                "Keine neue Bildausgabe erhalten. Möglicherweise keine visuelle Änderung oder das Modell unterstützt dies nicht.")

    except Exception as e:
        print(f"Fehler bei der Bildbearbeitung: {e}")
        print("Bitte versuchen Sie es mit einer anderen Anweisung.")
        