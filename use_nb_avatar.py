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

# --- Schritt 2: Modell und Prompt für Avatar-Erstellung ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Transform the person in this image into a stylized, high-quality avatar.
Give them a 'fantasy adventurer' look, with intricate armor and a magical, glowing background.
The style should be painterly and epic. Maintain the original facial features but elevate the overall aesthetic."""

# Lade das Eingabebild
input_image_path = "portrait.jpg" # Passe den Namen deines Portraitfotos an
try:
    image = Image.open(input_image_path)
    print(f"Eingabebild '{input_image_path}' erfolgreich geladen.")
except FileNotFoundError:
    print(f"Fehler: Das Bild '{input_image_path}' wurde nicht gefunden.")
    exit()

print("Sende Anfrage zur Avatar-Erstellung an die API... Bitte warten.")

# --- Schritt 3: API aufrufen mit Text und Bild ---
try:
    response = model.generate_content([prompt, image])

    # --- Schritt 4: Antwort verarbeiten und Bild speichern ---
    image_found = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                print("Avatar-Bilddaten gefunden, verarbeite...")
                image_data = part.inline_data.data
                avatar_image = Image.open(BytesIO(image_data))

                # Speichere das neue Bild
                output_filename = "fantasy_avatar.png"
                avatar_image.save(output_filename)
                print(f"Avatar erfolgreich als '{output_filename}' gespeichert.")
                image_found = True
                break
        if image_found:
            break

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")

except Exception as e:
    print(f"Ein Fehler ist bei der Erstellung des Avatars aufgetreten: {e}")
    