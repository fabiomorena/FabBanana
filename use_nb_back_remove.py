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

# --- Schritt 2: Modell und Prompt für Hintergrundentfernung ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

# Spezifischer Prompt für Hintergrundentfernung
prompt = """Remove the background from this image completely.
Keep only the main subject (the cat) and make the background fully transparent.
The output should be a PNG image with transparency.
Focus on clean edges and precise masking around the subject."""

# Lade das Eingabebild
input_image_path = "katze.png"  # Passe ggf. den Namen an
try:
    image = Image.open(input_image_path)
    print(f"Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Hintergrund-Entfernungsanfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und Bild ---
try:
    response = model.generate_content([prompt, image])

    # --- Schritt 4: Antwort verarbeiten und Bild mit transparentem Hintergrund speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(f"Textantwort vom Modell erhalten: {part.text}")
            elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Bilddaten mit entferntem Hintergrund gefunden, verarbeite...")
                image_data = part.inline_data.data
                removed_bg_image = Image.open(BytesIO(image_data))

                # Speichere das Bild mit transparentem Hintergrund als PNG
                output_filename = "katze_ohne_hintergrund.png"
                removed_bg_image.save(output_filename, format="PNG")
                print(f"Bild mit entferntem Hintergrund erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")
        print("Möglicherweise unterstützt das gewählte Modell keine direkte Hintergrundentfernung.")

except Exception as e:
    print(f"Ein Fehler ist bei der Hintergrund-Entfernung aufgetreten: {e}")
