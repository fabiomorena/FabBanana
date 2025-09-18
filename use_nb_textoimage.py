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

# --- Schritt 2: Modell und Prompt für die Bildgenerierung ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Create a photorealistic image of a futuristic city at sunset.
Skyscrapers made of chrome and glowing glass, flying vehicles weaving between them.
The color palette should be dominated by deep oranges, purples, and blues.
The style should be epic and highly detailed."""

print("Sende Anfrage zur Bildgenerierung an die API... Bitte warten.")

# --- Schritt 3: API aufrufen (nur mit Text) ---
try:
    response = model.generate_content(prompt)

    # --- Schritt 4: Antwort verarbeiten ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Generierte Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                generated_image = Image.open(BytesIO(image_data))

                output_filename = "generated_city.png"
                generated_image.save(output_filename)
                print(f"Bild erfolgreich als '{output_filename}' generiert und gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist bei der Bildgenerierung aufgetreten: {e}")
