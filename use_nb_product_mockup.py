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

# --- Schritt 2: Modell und Prompt für Produkt-Mockups ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Create a photorealistic product mockup. Place the product from the
first image seamlessly into the scene of the second image. Adjust lighting,
shadows, and perspective to make it look natural and integrated."""

# Lade die beiden Eingabebilder
# Passe die Dateinamen an Ihr Produkt- und Hintergrundbild an
product_image_path = "product.png"      # Ihr Produktbild (z.B. eine Flasche)
background_image_path = "background.png"  # Ihr Hintergrundbild (z.B. ein Tisch)

try:
    product_image = Image.open(product_image_path)
    print(f"Produktbild '{product_image_path}' erfolgreich geladen.")
    background_image = Image.open(background_image_path)
    print(f"Hintergrundbild '{background_image_path}' erfolgreich geladen.")
except FileNotFoundError as e:
    print(f"Fehler: Bild nicht gefunden - {e}")
    exit()

print("Sende Mockup-Anfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und beiden Bildern ---
try:
    response = model.generate_content([prompt, product_image, background_image])

    # --- Schritt 4: Antwort verarbeiten und Mockup speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(f"Textantwort vom Modell erhalten: {part.text}")
            elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Mockup-Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                mockup_image = Image.open(BytesIO(image_data))

                # Speichere das Mockup
                output_filename = "product_mockup.png"
                mockup_image.save(output_filename)
                print(f"Mockup erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist bei der Mockup-Erstellung aufgetreten: {e}")