import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import glob

# --- Schritt 1: Konfiguration ---
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("Fehler: Die Umgebungsvariable 'GOOGLE_API_KEY' wurde nicht gefunden.")
    exit()

# --- Schritt 2: Modell und Prompt für die Stapelverarbeitung ---
model = genai.GenerativeModel(model_name='gemini-2.5-flash-image-preview')

prompt = """Remove the background from this image completely.
Keep only the main subject and make the background fully transparent.
The output should be a PNG image with transparency."""

# --- Schritt 3: Verzeichnisse definieren ---
input_directory = "batch_input"   # Ordner mit den Originalbildern
output_directory = "batch_output" # Ordner für die bearbeiteten Bilder

# Sicherstellen, dass die Verzeichnisse existieren
if not os.path.isdir(input_directory):
    print(f"Fehler: Das Eingabeverzeichnis '{input_directory}' wurde nicht gefunden.")
    exit()
if not os.path.isdir(output_directory):
    os.makedirs(output_directory)
    print(f"Ausgabeverzeichnis '{output_directory}' wurde erstellt.")

# --- Schritt 4: Alle Bilder im Verzeichnis verarbeiten ---
image_files = glob.glob(os.path.join(input_directory, '*.png')) + \
              glob.glob(os.path.join(input_directory, '*.jpg'))

if not image_files:
    print(f"Keine Bilder im Verzeichnis '{input_directory}' gefunden.")
    exit()

print(f"{len(image_files)} Bilder zur Verarbeitung gefunden. Starte Stapelverarbeitung...")

for image_path in image_files:
    try:
        print(f"\nVerarbeite Bild: {os.path.basename(image_path)}")
        image = Image.open(image_path)

        # API aufrufen
        response = model.generate_content([prompt, image])

        # Antwort verarbeiten
        image_found = False
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    image_data = part.inline_data.data
                    processed_image = Image.open(BytesIO(image_data))

                    # Neues Bild im Ausgabe-Ordner speichern
                    base_filename = os.path.splitext(os.path.basename(image_path))[0]
                    output_filename = f"{base_filename}_processed.png"
                    output_path = os.path.join(output_directory, output_filename)
                    processed_image.save(output_path, format="PNG")
                    print(f"-> Erfolgreich gespeichert als '{output_path}'")
                    image_found = True
                    break
            if image_found:
                break

        if not image_found:
            print("-> Fehler: Keine Bilddaten in der Antwort für dieses Bild gefunden.")

    except Exception as e:
        print(f"-> Ein Fehler ist bei der Verarbeitung von {os.path.basename(image_path)} aufgetreten: {e}")

print("\nStapelverarbeitung abgeschlossen.")
