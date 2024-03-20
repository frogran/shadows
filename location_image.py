import requests
from openai import OpenAI
from utils import find_available_filename

# TODO def create_img_frame()


def generate_img(name, prompt, api_key=None, model='dall-e-3', size="1024x1024"):
	client = OpenAI(api_key=api_key)
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


def get_paper_prompt(city=None):
	if city:
		city = f' from {city}'
	return (f"Create an image of a high-resolution vintage paper texture made in {city}. "
			f"The paper should appear aged and weathered, with a natural pale yellow-brown color. It should showcase "
			f"characteristics like uneven surface, subtle crinkles, patches of discoloration, and faint, scattered "
			f"stains, resembling an antique document or an old manuscript. The texture should convey a sense of "
			f"historical depth and time-worn beauty, ideal for a backdrop of historical art or writing.")

def get_wood_prompt(city=None):
	if city:
		city = f' from {city}'
	return f'Generate a high-resolution, dark textured image of one dark-stained wooden plank{city}. ' \
		   'The wood should display prominent, intricate grain patterns with variations in the lines and rings ' \
		   'suggesting a natural, aged look. The image should be in black and white. ' \
		   'The surface should appear slightly weathered, with subtle imperfections such as small knots, ' \
		   'minimal scratches, and a faint matte sheen reflecting light. The perspective should be a close-up, ' \
		   'showing the detailed texture of the wood. Very dark image, low contrast. Low Brightness. (Dark: 1.3), Low light.'
