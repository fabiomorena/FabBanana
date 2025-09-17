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

# --- Schritt 2: Modell und Prompt für Restoration ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

# Prompt für Bildrestaurierung
prompt = """Restore this old, damaged photograph to its original quality.
Remove scratches, dust, and fading. Enhance colors and details while maintaining
the authentic vintage look. Do not add any elements that weren't in the original image."""

# Lade das beschädigte Eingabebild
input_image_path = "altes_bild.png"  # Passe ggf. den Namen an
try:
    image = Image.open(input_image_path)
    print(f"Beschädigtes Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Restaurierungsanfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und Bild ---
try:
    response = model.generate_content([prompt, image])

    # --- Schritt 4: Antwort verarbeiten und restauriertes Bild speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(f"Textantwort vom Modell erhalten: {part.text}")
            elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Restaurierte Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                restored_image = Image.open(BytesIO(image_data))

                # Speichere das restaurierte Bild
                output_filename = "restauriertes_bild.png"
                restored_image.save(output_filename)
                print(f"Restauriertes Bild erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")
        print("Möglicherweise unterstützt das gewählte Modell keine direkte Bildrestaurierung.")

except Exception as e:
    print(f"Ein Fehler ist bei der Restaurierung aufgetreten: {e}")
    