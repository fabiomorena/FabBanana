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

# --- Schritt 2: Modell und Prompt für Multiple Images ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

# Prompt für die Arbeit mit mehreren Bildern
prompt = """Combine these two images into a single cohesive scene.
Create a photorealistic image where a cat (from the first image) 
is sitting on a couch (from the second image) in a cozy living room.
Ensure the lighting and perspective are consistent between both elements."""

# Lade die beiden Eingabebilder
image1_path = "katze.png"      # Erstes Bild (z.B. Katze)
image2_path = "couch.png"      # Zweites Bild (z.B. Couch)

try:
    image1 = Image.open(image1_path)
    print(f"Erstes Bild '{image1_path}' erfolgreich geladen.")
    image2 = Image.open(image2_path)
    print(f"Zweites Bild '{image2_path}' erfolgreich geladen.")
except FileNotFoundError as e:
    print(f"Fehler: Bild nicht gefunden - {e}")
    exit()

print("Sende Multi-Image-Anfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und mehreren Bildern ---
try:
    response = model.generate_content([prompt, image1, image2])

    # --- Schritt 4: Antwort verarbeiten und kombiniertes Bild speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(f"Textantwort vom Modell erhalten: {part.text}")
            elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Kombinierte Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                combined_image = Image.open(BytesIO(image_data))

                # Speichere das kombinierte Bild
                output_filename = "kombiniertes_bild.png"
                combined_image.save(output_filename)
                print(f"Kombiniertes Bild erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")
        print("Möglicherweise unterstützt das gewählte Modell keine direkte Multi-Image-Verarbeitung.")

except Exception as e:
    print(f"Ein Fehler ist bei der Multi-Image-Verarbeitung aufgetreten: {e}")
    