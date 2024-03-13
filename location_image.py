import requests
from openai import OpenAI
from utils import find_available_filename
client = OpenAI()

# TODO def create_img_frame()


def generate_img(name, prompt, model='dall-e-3', size="1024x1024"):
    response = client.images.generate(
      model=model,
      prompt=prompt,
      size=size,
      quality="standard",
      n=1,
    )
    
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    base_name = f'/Users/galgo/code/aalto-2/{name}.png'
    name = find_available_filename(base_name)
    with open(name, 'wb') as handler:
        handler.write(img_data)
    print(image_url)
    return name


def debug_main():
    model = "dall-e-3"
    prompt = "one thing representing Tel Aviv, thing in center and small, background is only ocean, ocean is in style of Ochiai Yoshiiku, style of Kumanaki kagi"
    size = "1024x1024"
    generate_img(prompt, model, size)


# p = 'texture of wood after being used for japanese wood block printing, only texture, a single block,' \
#     'black, wood, high detail, realistic, dynamic lighting, frontal, entire image is wood, close up, ' \
#     'macro photography, zoom in'
p = 'Generate a high-resolution, textured image of one dark-stained wooden plank. ' \
    'The wood should display prominent, intricate grain patterns with variations in the lines and rings ' \
    'suggesting a natural, aged look. The image should be in black and white. ' \
    'The surface should appear slightly weathered, with subtle imperfections such as small knots, minimal scratches, ' \
    'and a faint matte sheen reflecting light. The perspective should be a close-up, ' \
    'showing the detailed texture of the wood. Dark image, low contrast'
# generate_img('black_wood', p)
