import os
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image


def find_available_filename(base_name):
	"""
	This function takes a base filename and iteratively appends an integer (starting from 0)
	until an available filename is found.

	:param base_name: str - The base name for the file, including the desired extension.
	:return: str - The first available filename not currently in use.
	"""
	counter = 0
	name, extension = os.path.splitext(base_name)
	
	while True:
		potential_name = f"{name}_{counter}{extension}"
		if not os.path.exists(potential_name):
			return potential_name
		counter += 1


def scale_and_crop_center(img, crop_width, crop_height):
	y, x = img.shape[:2]
	# Scale down the image by factors of two until just bigger than the crop
	while x > crop_width * 2 and y > crop_height * 2:
		img = cv2.pyrDown(img)
		y, x = img.shape[:2]
	
	# Now crop around the center
	start_x = x // 2 - crop_width // 2
	start_y = y // 2 - crop_height // 2
	if start_x < 0 or start_y < 0:  # Image is smaller than the crop area
		# Resize image to be at least as large as the specified crop area
		img = cv2.resize(img, (max(crop_width, x), max(crop_height, y)), interpolation=cv2.INTER_AREA)
		y, x = img.shape[:2]
		start_x = x // 2 - crop_width // 2
		start_y = y // 2 - crop_height // 2
	cropped_img = img[start_y:start_y + crop_height, start_x:start_x + crop_width]
	return cropped_img


def stitch_images_to_portrait(img1, img2, img3, text):
	width = 800
	height = 1200
	
	# top = 1/4: 1/3; bottom: w4/5
	top_height = height // 4
	bottom_height = height - top_height
	top_right_width = int(width * (2 / 3))
	top_left_width = width - top_right_width
	bottom_left_width = int(width * (4 / 5))
	bottom_right_width = width - bottom_left_width
	
	# Crop images to fit in the grid
	img1_cropped = scale_and_crop_center(img1, bottom_left_width, bottom_height)
	img2_cropped = scale_and_crop_center(img2, bottom_right_width, bottom_height)
	img3_cropped = scale_and_crop_center(img3, top_right_width, top_height)
	
	# Resize images to fit grid dimensions (if necessary)
	img1_resized = cv2.resize(img1_cropped, (bottom_left_width, bottom_height), interpolation=cv2.INTER_AREA)
	img2_resized = cv2.resize(img2_cropped, (bottom_right_width, bottom_height), interpolation=cv2.INTER_AREA)
	img3_resized = cv2.resize(img3_cropped, (top_right_width, top_height), interpolation=cv2.INTER_AREA)
	img3_resized = add_frame_with_rounded_corners(img3_resized, cv2.imread(f'/Users/galgo/code/aalto-2/paper1.jpeg'))
	# Create empty top left rectangle
	top_left_empty = np.zeros((top_height, top_left_width, 3), dtype=np.uint8)
	
	# Stitch the top half (empty left + third image on the right)
	top_half = np.concatenate((top_left_empty, img3_resized), axis=1)
	
	# Stitch the bottom half (first image on the left + second image on the right)
	bottom_half = np.concatenate((img1_resized, img2_resized), axis=1)
	
	# Stitch the top and bottom halves together
	stitched_image = np.concatenate((top_half, bottom_half), axis=0)

	result = stitched_image.astype(np.uint8)
	if result.shape[2] == 4:
		result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)
	result = add_wrapped_text(result, text, (20, 20), top_left_width - 30, top_height - 40, 100)
	return result


def add_wrapped_text(image, text, pos, max_width, max_height, font_size,
					 font_path='/Users/galgo/code/pythonProject/fonts/Sacramento-Regular.ttf'):
	"""
	Add wrapped text to an image, resizing the font as needed.

	:param image: The image to add text to.
	:param text: The text to add.
	:param pos: The top-left position (x, y) where the text starts.
	:param max_width: Maximum width for the text area.
	:param font_path: Path to the .ttf font file.
	:param font_size: Initial font size (will be adjusted to fit the width).
	:return: The image with the text added.
	"""
	# Convert the image to a PIL format
	img_pil = Image.fromarray(image)
	draw = ImageDraw.Draw(img_pil)

	font = ImageFont.truetype(font_path, font_size)

	def wrap_text_fixed_font(text, font, draw, max_width):
		lines = []
		words = text.split()
		while words:
			words0_size = font.getbbox(words[0])[2] - font.getbbox(words[0])[0]
			if words0_size > max_width:  # Check if the word is wider than the max width
				if font.size <= 1:  # Prevents making the font size smaller than 1
					raise ValueError(
						"Text can't be accommodated, even at the smallest font size. Please increase the max width.")
				# Reduce the font size
				font = ImageFont.truetype(font.path, font.size - 1)
				continue  # Skip the rest of the loop and re-evaluate the condition with a smaller font size
			
			line = ''
			while words:
				next_word = words[0]
				test_line = f"{line} {next_word}".strip()
				size = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]
				if size <= max_width:
					line = test_line
					words.pop(0)
				else:
					break
			lines.append(line)
		return lines, font
	
	# Check if the text fits within the specified height; if not, reduce font size
	lines, font = wrap_text_fixed_font(text, font, draw, max_width)
	text_height = len(lines) * (font.getbbox(lines[0])[3] - font.getbbox(lines[0])[1])
	while text_height > max_height and font.size > 1:
		# Reduce font size
		font = ImageFont.truetype(font.path, font.size - 1)
		lines, font = wrap_text_fixed_font(text, font, draw, max_width)
		# Recalculate the lines and text height
		text_height = len(lines) * (font.getbbox(lines[0])[3] - font.getbbox(lines[0])[1])
	
	# return font, lines

	# Check if font size adjustment is needed based on the longest line
	longest_line = max(lines, key=lambda line: font.getbbox(line)[2] - font.getbbox(line)[0])
	left, top, right, bottom = font.getbbox(text)
	text_width = right - left
	text_height = bottom - top
	while text_width > max_width:
		font_size -= 1
		font = ImageFont.truetype(font_path, font_size)
		left, top, right, bottom = font.getbbox(longest_line)
		text_width = right - left
		text_height = bottom - top

	# Draw the text on the image
	y_offset = pos[1]
	for line in lines:
		draw.text((pos[0], y_offset), line, font=font, fill=(255,255,255))
		y_offset += text_height

	return np.array(img_pil)


def create_rounded_corner_mask(size, corner_radius, border_thickness=30):
    """
    Create a mask for an image with rounded corners.

    :param size: The size of the mask (height, width).
    :param corner_radius: The radius of the rounded corners.
    :return: A mask with rounded corners.
    """
    height, width = size
    mask = np.zeros((height, width), dtype=np.uint8)

    # Draw rectangles to fill the space excluding corners
    cv2.rectangle(mask, (corner_radius + border_thickness, border_thickness), (width - corner_radius -border_thickness, height - border_thickness), 255, -1)
    cv2.rectangle(mask, (border_thickness, corner_radius + border_thickness), (width - border_thickness, height - corner_radius - border_thickness), 255, -1)

    # Draw the four corner circles
    cv2.circle(mask, (corner_radius+border_thickness, corner_radius+border_thickness), corner_radius, 255, -1)
    cv2.circle(mask, (width - corner_radius - border_thickness, corner_radius+border_thickness), corner_radius, 255, -1)
    cv2.circle(mask, (corner_radius+border_thickness, height - corner_radius - border_thickness), corner_radius, 255, -1)
    cv2.circle(mask, (width - corner_radius - border_thickness, height - corner_radius - border_thickness), corner_radius, 255, -1)

    return mask


def add_frame_with_rounded_corners(image, frame_image, corner_radius=40):
	"""
	Add a frame to an image with rounded corners.

	:param image: The main image as an np array.
	:param frame_image: The image to take the frame from, as an np array.
	:param corner_radius: The radius of the rounded corners.
	:return: The framed image with rounded corners.
	"""
	# Ensure the image has an alpha channel
	if image.shape[2] < 4:
		image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
	
	# Resize frame to match image dimensions
	frame_image = cv2.resize(frame_image, (image.shape[1], image.shape[0]))
	
	
	# Create a mask for the rounded rectangle
	mask = create_rounded_corner_mask((image.shape[0], image.shape[1]), corner_radius)
	
	# Apply the mask to create rounded corners on the image
	rounded_image = cv2.bitwise_and(image, image, mask=mask)
	
	# Prepare the frame by ensuring it has an alpha channel
	if frame_image.shape[2] < 4:
		frame_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2BGRA)
	
	# Add the frame behind the image
	inv_mask = cv2.bitwise_not(mask)
	# SCALE FRAME IMG
	ref_height, ref_width = inv_mask.shape[:2]
	frame_image = frame_image[0:ref_height, 0:ref_width]
	frame_image = cv2.bitwise_and(frame_image, frame_image, mask=inv_mask)
	final_image = cv2.bitwise_or(rounded_image, frame_image)
	cv2.imwrite('frame0.png', final_image)
	if final_image.shape[2] == 4:
		final_image = cv2.cvtColor(final_image, cv2.COLOR_BGRA2BGR)
	return final_image


def add_border_and_center_in_frame(image, frame_image, border_size=30, corner_radius=50):
	"""
	# Shrink the image, add rounded corners, a border around it, and center it relative to the frame image.

	:param image: The original image as an np array.
	:param frame_image: The frame image as an np array.
	:param border_size: The size of the border to add around the image.
	:param corner_radius: The radius of the rounded corners for the image.
	:return: The image with rounded corners and a border, centered in the frame.
	"""
	# Calculate new size to accommodate the border
	new_width = image.shape[1] - (2 * border_size)
	new_height = image.shape[0] - (2 * border_size)
	
	# Resize the original image to fit the border
	image = cv2.resize(image, (new_width, new_height))
	
	# Apply rounded corners to the resized image
	# Mask for rounded corners on the resized image
	mask = np.zeros((new_height, new_width), dtype=np.uint8)
	cv2.rectangle(mask, (corner_radius, corner_radius), (new_width - corner_radius, new_height - corner_radius), 255,
				  -1)
	cv2.circle(mask, (corner_radius, corner_radius), corner_radius, 255, -1)
	cv2.circle(mask, (new_width - corner_radius, corner_radius), corner_radius, 255, -1)
	cv2.circle(mask, (corner_radius, new_height - corner_radius), corner_radius, 255, -1)
	cv2.circle(mask, (new_width - corner_radius, new_height - corner_radius), corner_radius, 255, -1)
	rounded_image = cv2.bitwise_and(image, image, mask=mask)
	
	# Create a new image with border size added to the resized image dimensions and same depth, fill with the frame
	bordered_image = cv2.resize(frame_image, (image.shape[1] + (2 * border_size), image.shape[0] + (2 * border_size)))
	
	# Place the rounded image in the center of the bordered frame
	start_y = border_size
	start_x = border_size
	bordered_image[start_y:start_y + new_height, start_x:start_x + new_width] = rounded_image
	
	return bordered_image


def debug_utils():
	from capture_cam import read_write_video
	cap = read_write_video(0)
	t, im = cap.read()
	img1 = cv2.imread('/Users/galgo/code/aalto-2/Tel Aviv_0.png')
	img2 = cv2.imread('/Users/galgo/code/aalto-2/Tel_Aviv_1.png')
	img3 = cv2.imread('/Users/galgo/code/aalto-2/Tel_Aviv_2.png')
	result = stitch_images_to_portrait(im, img2, img3, 'test text')
	cv2.imwrite(find_available_filename('stitched_image.png'), result)
	cap.release()

