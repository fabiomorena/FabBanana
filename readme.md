# 🍌 NanoBanana AI Image Studio

This repository contains a set of Python scripts and a GUI application that leverage the `gemini-2.5-flash-image-preview` model from Google Generative AI for various image editing and generation tasks.

## Features

* **GUI Application (`nano_banana_gui.py`)**: An interactive desktop application that allows users to load images and perform various AI-powered editing functions.
* **Background Removal**: A script to remove the background from an image and isolate the main subject. The resulting image has a transparent background.
* **Image Restoration**: A script for restoring old or damaged photos, removing scratches and fading.
* **Multi-Image Processing**: A sample script demonstrating how to combine two or more images into a cohesive scene.
* **Conversational Image Editing**: An interactive chat mode where the user can continuously provide instructions to edit an image.

## Prerequisites

Before use, ensure the following components are installed:

* **Python**: Version 3.13 or higher is recommended.
* **Google API Key**: An API key for the Google Generative AI API is required and must be set as an environment variable `GOOGLE_API_KEY`.

* Source : **https://dev.to/googleai/how-to-build-with-nano-banana-complete-developer-tutorial-646**


## Installation

1.  **Clone the repository (if applicable)**:
    ```bash
    git clone [https://github.com/fabiomorena/FabBanana.git](https://github.com/fabiomorena/FabBanana.git)
    cd FabBanana
    ```

2.  **Install required libraries**:
    ```bash
    pip install google-generativeai Pillow
    ```

3.  **Set the API Key**:
    Set your `GOOGLE_API_KEY` environment variable as follows:
    * On Unix/macOS:
        ```bash
        export GOOGLE_API_KEY="Your-API-Key"
        ```
    * On Windows (Command Prompt):
        ```bash
        set GOOGLE_API_KEY="Your-API-Key"
        ```

## Usage

### Starting the GUI Application

Run the main script to launch the graphical user interface:

```bash
python nano_banana_gui.py

