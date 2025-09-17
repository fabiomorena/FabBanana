import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# --- Schritt 1: Konfiguration ---
# Der API-Schlüssel wird sicher aus einer Umgebungsvariable geladen.
# Stellen Sie sicher, dass Sie diese Variable gesetzt haben!
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("Fehler: Die Umgebungsvariable 'GOOGLE_API_KEY' wurde nicht gefunden.")
    print("Bitte setzen Sie die Variable und versuchen Sie es erneut.")
    exit()  # Beendet das Skript, wenn der Schlüssel fehlt

# --- Schritt 2: Modell und Prompt definieren ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Using the image of the cat, create a photorealistic,
street-level view of the cat walking along a sidewalk in a
New York City neighborhood, with the blurred legs of pedestrians
and yellow cabs passing by in the background."""

print("Sende Anfrage an die API... Bitte warten.")

# --- Schritt 3: API aufrufen und Bild generieren ---
try:
    response = model.generate_content(prompt)

    # --- Schritt 4: Antwort verarbeiten und Bild speichern ---
    # Die Antwort kann Text- und Bilddaten enthalten. Wir suchen nach den Bilddaten.
    image_found = False
    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"Textantwort vom Modell erhalten: {part.text}")
        elif part.inline_data and part.inline_data.mime_type.startswith("image/"):
            print("Bilddaten gefunden, verarbeite...")
            image_data = part.inline_data.data
            image = Image.open(BytesIO(image_data))

            # Speichere das Bild
            output_filename = "picture.png"
            image.save(output_filename)
            print(f"Bild erfolgreich als '{output_filename}' gespeichert.")
            image_found = True
            break  # Schleife beenden, nachdem das erste Bild gefunden wurde

    if not image_found:
        print("Es wurden keine Bilddaten in der Antwort des Modells gefunden.")
        print("Möglicherweise unterstützt das gewählte Modell keine direkte Bilderzeugung oder die Anfrage war unklar.")

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")