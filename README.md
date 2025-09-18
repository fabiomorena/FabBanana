Of course\! It's a great idea to keep the documentation updated with the app's growing capabilities. Here is the updated and complete `README.md` file, including all the new features we've implemented.

-----

# 🍌 NanoBanana AI Image Studio

This repository contains a set of Python scripts and a comprehensive GUI application that leverage the `gemini-2.5-flash-image-preview` model from Google Generative AI for a wide array of image editing and generation tasks.

## Features

The **NanoBanana AI Image Studio** is a full-featured desktop application (`nano_banana_gui.py`) that provides a user-friendly interface for the following AI-powered functionalities:

### Generation & Creation

  * **Text-to-Image Generation**: Create entirely new images from a detailed text description.
  * **AI-Generated Avatars**: Transform a portrait photo into a stylized avatar in various artistic styles (e.g., fantasy, cartoon, sci-fi).
  * **Image Outpainting/Uncropping**: Expand an image beyond its original borders by intelligently generating new, context-aware content.

### Editing & Enhancement

  * **Background Removal**: Isolate the main subject of an image by making the background fully transparent.
  * **Image Restoration**: Restore old or damaged photos by removing scratches, dust, and fading while enhancing colors.
  * **Image Upscaling**: Increase the resolution and clarity of an image, adding fine details for a high-quality result.
  * **Object Removal**: Seamlessly remove unwanted objects from an image.
  * **Logo and Watermark Integration**: Add a logo or watermark to an image with controls for position and opacity.
  * **Conversational Image Editing (Chat Mode)**: Interactively edit an image by giving sequential text commands.

### Application & Workflow

  * **Product Mockups**: Create photorealistic product mockups by placing a product image into a different scene or background.
  * **Marketing Asset Creation**: Transform product images into compelling social media assets by adding slogans and modern styling.
  * **Batch Processing**: Apply the same AI action (e.g., background removal) to an entire folder of images at once.
  * **Style Transfer**: Transfer the artistic style of one image to another.

## Prerequisites

Before use, ensure the following components are installed:

  * **Python**: Version 3.13 or higher is recommended.
  * **Required Python Libraries**: `google-generativeai`, `Pillow`, and `customtkinter`.
  * **Google API Key**: An API key for the Google Generative AI API is required.
  * **(Optional) Inter Font**: For the best visual experience with the GUI, it is recommended to install the "Inter" font family.
  * [How to build with Nano Banana - Complete Developer Tutorial](https://dev.to/googleai/how-to-build-with-nano-banana-complete-developer-tutorial-646)

## Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/fabiomorena/FabBanana.git
    cd FabBanana
    ```

2.  **Install required libraries**:

    ```bash
    pip install google-generativeai Pillow customtkinter
    ```

3.  **Set the API Key**:
    You must set your `GOOGLE_API_KEY` as an environment variable.

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
```