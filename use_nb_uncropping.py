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
    exit()

# --- Schritt 2: Modell und Prompt für Uncropping ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Expand this image ('outpainting').
Extend the scene naturally on all four sides to create a wider, more panoramic view.
Maintain the original photorealistic style and ensure the newly generated areas
blend seamlessly with the existing image content. The final image should have an aspect ratio of 16:9."""

# --- Schritt 3: Bild laden ---
input_image_path = "portrait.jpg" # Das zu erweiternde Bild
try:
    image = Image.open(input_image_path)
    print(f"Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Uncropping-Anfrage an die API... Bitte warten.")

# --- Schritt 4: API aufrufen ---
try:
    response = model.generate_content([prompt, image])

    # --- Schritt 5: Antwort verarbeiten ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Erweitertes Bild gefunden, verarbeite...")
                image_data = part.inline_data.data
                expanded_image = Image.open(BytesIO(image_data))

                output_filename = "expanded_image.png"
                expanded_image.save(output_filename)
                print(f"Erweitertes Bild erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist beim Uncropping aufgetreten: {e}")
    