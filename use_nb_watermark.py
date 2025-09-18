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

# --- Schritt 2: Modell und Prompt für Wasserzeichen ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Place the logo (second image) onto the main image (first image).
Position it in the bottom right corner. Make it semi-transparent (around 70% opacity)
and scale it down to be about 15% of the main image's width.
Ensure the final output is a high-quality composite image."""

# --- Schritt 3: Bilder laden ---
main_image_path = "main_image.png"      # Bild, das das Wasserzeichen erhalten soll
watermark_image_path = "logo.png"       # Das Logo- oder Wasserzeichen-Bild

try:
    main_image = Image.open(main_image_path)
    print(f"Hauptbild '{main_image_path}' erfolgreich geladen.")
    watermark_image = Image.open(watermark_image_path)
    print(f"Wasserzeichen-Bild '{watermark_image_path}' erfolgreich geladen.")
except FileNotFoundError as e:
    print(f"Fehler: Bild nicht gefunden - {e}")
    exit()

print("Sende Anfrage zur Wasserzeichen-Integration an die API... Bitte warten.")

# --- Schritt 4: API aufrufen ---
try:
    response = model.generate_content([prompt, main_image, watermark_image])

    # --- Schritt 5: Antwort verarbeiten ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Bild mit Wasserzeichen gefunden, verarbeite...")
                image_data = part.inline_data.data
                final_image = Image.open(BytesIO(image_data))

                output_filename = "image_with_watermark.png"
                final_image.save(output_filename)
                print(f"Bild erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    