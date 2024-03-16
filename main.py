import cv2

from location_utils import get_city
from location_image import generate_img, get_wood_prompt
from get_generated_text import generate_text
from capture_cam import read_write_video, YOLOSegmentation, person_to_texture
from utils import stitch_images_to_portrait, find_available_filename, scale_and_crop_center


def run_main():
	# TODO add outlines
	city = get_city()
	city_filename = city.replace(" ", "_")
	model = 'dall-e-3'
	prompt1 = f"one thing representing {city}, " \
			  f"thing in center and small, " \
			  f"background is only ocean, " \
			  f"ocean is in style of Ochiai Yoshiiku, " \
			  f"style of Kumanaki kagi"
	print('generating city rep image')
	img3_filename = generate_img(city_filename, prompt1, model)
	
	text_prompt = f"in very few words mention one special and uncommon thing about {city}. " \
				  f"The output should be similar to 'You may not know this, but near you...'"
	text = generate_text(text_prompt)
	text = text.content
	with open('text.txt', 'a') as texts:
		texts.write(str(text) + '\n\n')
	prompt2 = f"a very simple image of {text} in the style of {city}"
	print('generating special thing in city image')
	img2_filename = generate_img(city_filename, prompt2, model)
	
	paper_prompt = f"the texture of a very fine light paper made in {city}"
	paper_filename = generate_img('paper', paper_prompt)
	wood_prompt = get_wood_prompt(city)
	wood_filename = generate_img('wood', wood_prompt)
	
	
	
	show_stitch(img2_filename, img3_filename, str(text), shadow_texture_path=wood_filename, bg_path=paper_filename)
	
	# print(cv2.waitKey(0))
	# cv2.destroyAllWindows()
	# for i in range(2):
	# 	cv2.waitKey(1)
	
	return


def debug_single_stitching():
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
	text_prompt = f"You are a local tour guide in Barcelona." \
				  f"In very few words mention one thing that would surprise a local about Barcelona." \
				  f"Think of something special!" \
				  f"The output should be similar to 'You may not know this, but near you...'"
	text = generate_text(text_prompt)
	stitched_image = stitch_images_to_portrait(shadow, img2, img3, text.content)
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


def debug_video_without_generation():
	paper_img_path = f'/Users/galgo/code/aalto-2/paper1.jpeg'
	wood_image_path = f'/Users/galgo/code/aalto-2/black_wood_5.png'
	
	img2_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_9.png'
	img3_filename = '/Users/galgo/code/aalto-2/Tel_Aviv_6.png'
	
	show_stitch(img2_filename, img3_filename)
	return


def debug_p2t():
	ys = YOLOSegmentation()
	shadow_texture_path = f'/Users/galgo/code/aalto-2/black_wood_5.png'
	bg_path = f'/Users/galgo/code/aalto-2/paper1.jpeg'
	bg = cv2.imread(bg_path)
	texture = cv2.imread(shadow_texture_path)
	cap, vw = read_write_video(0, find_available_filename(f'/Users/galgo/code/aalto-2/test_p2t.avi'), portrait=True)
	t, cam = cap.read()
	cv2.startWindowThread()
	i = 0
	while t:
		cam = scale_and_crop_center(cam, 512, 512)
		s, shadow = person_to_texture(cam, texture, bg, ys)
		
		print(shadow.shape)
		# cv2.imshow('screen1', stitched_image)
		# print(stitched_image)
		vw.write(shadow)
		
		t, cam = cap.read()
		i = i + 1
		print(i)
		if i > 50:
			break
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break
	vw.release()
	cap.release()
	cv2.destroyAllWindows()


def show_stitch(bottom_right_img_path, top_right_img_path, text,
				shadow_texture_path=f'/Users/galgo/code/aalto-2/black_wood_5.png',
				bg_path=f'/Users/galgo/code/aalto-2/paper1.jpeg',
				ys=None):
	texture = cv2.imread(shadow_texture_path)
	bg = cv2.imread(bg_path)
	if not ys:
		ys = YOLOSegmentation()
	
	bottom_right_img = cv2.imread(bottom_right_img_path)
	top_right_img = cv2.imread(top_right_img_path)
	cap, vw = read_write_video(0, find_available_filename(f'/Users/galgo/code/aalto-2/test_shadow.avi'), portrait=True)
	t, cam = cap.read()
	cv2.startWindowThread()
	i = 0
	while t:
		cam = scale_and_crop_center(cam, 512, 512)
		s, shadow = person_to_texture(cam, texture, bg, ys)

		print(shadow.shape)
		stitched_image = stitch_images_to_portrait(shadow, bottom_right_img, top_right_img, text)
		# cv2.imshow('screen1', stitched_image)
		# print(stitched_image)
		vw.write(stitched_image)
		
		t, cam = cap.read()
		i = i + 1
		print(i)
		if i > 120:
			break
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break
	vw.release()
	cap.release()
	cv2.destroyAllWindows()


if __name__ == '__main__':
	debug_p2t()
