## Mockup for Unclear Shadows

Homage to Clear Shadows (Kumanaki kage, 1867) by Ochiai Yoshiiku. 
Visual social network filter to reflect collected data points -
  our shadow trails and a darkness of social networks.

\[Requires an OpenAI API key\]

Example images for prompt results contained in folder

## Installation

Before running the script, ensure you have Python installed on your system. Then, install the required libraries using pip:

```bash
pip install requests openai numpy opencv-python Pillow argparse ultralytics
```

Note:

cv2 (OpenCV) is installed via opencv-python.
YOLO from ultralytics requires additional setup; refer to the Ultralytics YOLO documentation for detailed instructions.
If you're using OpenAI's API, you need an API key from OpenAI

```markdown
# Image and Video Processing Tool
```
This script processes images and videos, allowing for dynamic generation based on textual descriptions or specific image inputs.

## Usage

```bash
python script.py --mode [image|video] [--shadow PATH] [--top_right PATH] [--bottom_right PATH] [--text TEXT] [--wood PATH] [--paper PATH] [--openai_apikey KEY]


- `--mode`: Choose 'image' or 'video' to specify the processing mode.
- `--shadow`: Path to the shadow image. If not provided, a default is generated.
- `--top_right`: Path to the top-right image. Defaults to a generated image if not specified.
- `--bottom_right`: Path to the bottom-right image. Defaults to a generated image if not specified.
- `--text`: Text to overlay. If omitted, it's generated based on a city's context.
- `--wood`: Path to the wood texture image. If omitted, a default wood texture is generated.
- `--paper`: Path to the paper texture image. If omitted, a default paper texture is generated.
- `--openai_apikey`: Your OpenAI API key, required for generating content if not all inputs are provided.

Ensure to replace `script.py` with the name of your Python script.
```

Adjust the script name and paths as necessary for your specific setup.
