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

# --- Schritt 2: Modell und Prompt für Marketing-Assets ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Transform this product image into a vibrant social media marketing asset.
Add an attractive, modern text overlay with the slogan 'Entdecke die Zukunft.'
The style should be bold and eye-catching, suitable for an Instagram post.
Ensure the product remains the central focus and the text is clearly readable."""

# Lade das Eingabebild
# Passe den Dateinamen an Ihr Produktbild an
input_image_path = "product_original.png"
try:
    image = Image.open(input_image_path)
    print(f"Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Anfrage zur Erstellung von Marketing-Assets an die API... Bitte warten.")

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
                print("Marketing-Asset-Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                marketing_asset = Image.open(BytesIO(image_data))

                # Speichere das neue Bild
                output_filename = "marketing_asset.png"
                marketing_asset.save(output_filename)
                print(f"Marketing-Asset erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist bei der Erstellung des Marketing-Assets aufgetreten: {e}")