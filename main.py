import cv2

from location_utils import get_city
from location_image import generate_img
from get_generated_text import generate_text
from capture_cam import read_write_video, YOLOSegmentation, person_to_texture
from utils import stitch_images_to_portrait, find_available_filename


def debug_main():
	# V get location - ip to location
	# V get image one - location representation
	# V get text -
	# V get image two - pictionary / meaningful image
	# V generate texture
	# V capture cam
	# V img -> shadow
	# V place
	# V show
	# V add info
	# V add picture frames
	#   add outlines
	# V save text
	
	
	city = get_city()
	city_filename = city.replace(" ", "_")
	model = 'dall-e-3'
	prompt1 = f"one thing representing {city}, " \
			  f"thing in center and small, " \
			  f"background is only ocean, " \
			  f"ocean is in style of Ochiai Yoshiiku, " \
			  f"style of Kumanaki kagi"
	
	img1_filename = generate_img(city_filename, prompt1, model)
	
	text_prompt = f"in very few words mention one special and uncommon thing about {city}"
	text = generate_text(text_prompt)
	with open('text.txt', 'a') as texts:
		texts.write(text + '\n\n')
	prompt2 = f"a very simple image of {text} in the style of {city}"
	img2_filename = generate_img(city_filename, prompt2, model)
	
	paper_img_path = f'/Users/galgo/code/aalto-2/paper1.jpeg'
	wood_image_path = f'/Users/galgo/code/aalto-2/black_wood_5.png'
	
	show_stitch(img2_filename, img1_filename)
	
	# print(cv2.waitKey(0))
	# cv2.destroyAllWindows()
	# for i in range(2):
	# 	cv2.waitKey(1)
	
	return


def debug_single_image():
	img2_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_9.png'
	img3_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_6.png'
	# texture = cv2.imread(f'/Users/galgo/code/aalto-2/black_wood_5.png')
	# bg = cv2.imread(f'/Users/galgo/code/aalto-2/paper1.jpeg')
	# ys = YOLOSegmentation()
	shadow = cv2.imread('/Users/galgo/code/pythonProject/shadow.png')
	img2 = cv2.imread(img2_filename)
	img3 = cv2.imread(img3_filename)
	# cap = read_write_video(0)
	# t, cam = cap.read()
	# s, shadow = person_to_texture(cam, texture, bg, ys)
	# i = 0
	# while not s:
	# 	t, cam = cap.read()
	# 	s, shadow = person_to_texture(cam, texture, bg, ys)
	# 	i = i + 1
	# 	if i > 49:
	# 		print('failed to detect')
	# 		return
	#
	# cv2.startWindowThread()
	print(shadow.shape)
	# cv2.imwrite('shadow.png', shadow)

	stitched_image = stitch_images_to_portrait(shadow, img2, img3,
											   "i am a lovely person and fight fear every day, there's a shadow in "
											   "all of us, but that's fine and we're going to do the best to light the world up")
	# cv2.imshow('screen1', stitched_image)
	filename = find_available_filename(f'/Users/galgo/code/aalto-2/stitched_img.png')
	print(filename)
	cv2.imwrite(filename, stitched_image)
	# s_filename = find_available_filename(f'/Users/galgo/code/aalto-2/shadow.png')
	# cv2.imwrite(s_filename, stitched_image)
	# print(f'stitched image shape: {stitched_image.shape}')
	return
	
	# cv2.waitKey(0)
	cap.release()
	cv2.destroyAllWindows()


def fast_debug():
	paper_img_path = f'/Users/galgo/code/aalto-2/paper1.jpeg'
	wood_image_path = f'/Users/galgo/code/aalto-2/black_wood_5.png'
	
	img2_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_9.png'
	img3_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_6.png'
	
	show_stitch(img2_filename, img3_filename)
	return


def show_stitch(img2_filename, img3_filename, texture=None, bg=None, ys=None):
	if not texture:
		texture = cv2.imread(f'/Users/galgo/code/aalto-2/black_wood_5.png')
	if not bg:
		bg = cv2.imread(f'/Users/galgo/code/aalto-2/paper1.jpeg')
	if not ys:
		ys = YOLOSegmentation()
	
	img2 = cv2.imread(img2_filename)
	img3 = cv2.imread(img3_filename)
	cap, vw = read_write_video(0, find_available_filename(f'/Users/galgo/code/aalto-2/test_shadow.avi'), portrait=True)
	t, cam = cap.read()
	cv2.startWindowThread()
	i = 0
	while t:
		s, shadow = person_to_texture(cam, texture, bg, ys)
		# cv2.imshow('screen', shadow)
		# cv2.waitKey(0)
		print(shadow.shape)
		stitched_image = stitch_images_to_portrait(shadow, img2, img3)
		# cv2.imshow('screen1', stitched_image)
		# print(stitched_image)
		vw.write(stitched_image)
		
		t, cam = cap.read()
		i = i + 1
		if i > 100:
			break
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break
	vw.release()
	cap.release()
	cv2.destroyAllWindows()


if __name__ == '__main__':
	debug_single_image()
