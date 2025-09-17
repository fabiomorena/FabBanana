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

# --- Schritt 2: Modell und Eingaben definieren ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Using the image of the cat, create a photorealistic,
street-level view of the cat walking along a beach in a
southern city, with the blurred legs of pedestrians
and yellow cabs passing by in the background."""

# Lade das Eingabebild
input_image_path = "katze.png"  # Passe ggf. den Namen an
try:
    image = Image.open(input_image_path)
    print(f"Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Anfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und Bild ---
try:
    response = model.generate_content([prompt, image])

    # --- Schritt 4: Antwort verarbeiten und Bild speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(f"Textantwort vom Modell erhalten: {part.text}")
            elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                output_image = Image.open(BytesIO(image_data))

                # Speichere das neue Bild
                output_filename = "edited_cat.png"
                output_image.save(output_filename)
                print(f"Bearbeitetes Bild erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")
        print("Möglicherweise unterstützt das gewählte Modell keine direkte Bilderzeugung.")

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
