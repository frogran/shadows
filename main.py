import cv2
import argparse
from location_utils import get_city
from location_image import generate_img, get_wood_prompt
from get_generated_text import generate_text
from capture_cam import read_write_video, YOLOSegmentation, person_to_texture
from utils import stitch_images_to_portrait, find_available_filename, scale_and_crop_center


def image(img2_path, img3_path, text, shadow_texture_path, bg_path, show=False):
    texture = cv2.imread(shadow_texture_path)
    bg = cv2.imread(bg_path)
    img2 = cv2.imread(img2_path)
    img3 = cv2.imread(img3_path)
    ys = YOLOSegmentation()
    cap = read_write_video(0)
    t, cam = cap.read()
    cam = scale_and_crop_center(cam, 512, 512)
    s, shadow = person_to_texture(cam, texture, bg, ys)
    cap.release()
    stitched_image = stitch_images_to_portrait(shadow, img2, img3, text)
    if show:
        cv2.imshow('Stitched Image', stitched_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    filename = find_available_filename('stitched_img.png')
    cv2.imwrite(filename, stitched_image)


def video(img2_path, img3_path, text, shadow_texture_path, bg_path, show=False):
    ys = YOLOSegmentation()
    texture = cv2.imread(shadow_texture_path)
    bg = cv2.imread(bg_path)
    cap, vw = read_write_video(0, find_available_filename('video.avi'), portrait=True)
    i = 0
    while True:
        t, cam = cap.read()
        if not t or i >= 120: break
        cam = scale_and_crop_center(cam, 512, 512)
        s, shadow = person_to_texture(cam, texture, bg, ys)
        stitched_image = stitch_images_to_portrait(shadow, cv2.imread(img2_path), cv2.imread(img3_path), text)
        if show:
            cv2.imshow('Video Frame', stitched_image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        vw.write(stitched_image)
        i += 1
    vw.release()
    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Process images and videos.")
    parser.add_argument('--mode', type=str, help='Mode: image or video', required=True)
    parser.add_argument('--city', type=str, help='Manually pick city', default=None)
    parser.add_argument('--shadow', type=str, help='Path to shadow image', default=None)
    parser.add_argument('--top_right', type=str, help='Path to top right image', default=None)
    parser.add_argument('--bottom_right', type=str, help='Path to bottom right image', default=None)
    parser.add_argument('--text', type=str, help='Text to overlay', default=None)
    parser.add_argument('--wood', type=str, help='Path to wood texture image', default=None)
    parser.add_argument('--paper', type=str, help='Path to paper texture image', default=None)
    parser.add_argument('--openai_apikey', type=str, help='Generation requires OpenAI API-key', default=None)
    parser.add_argument('--show', type=str, help='Show created image (True of False)', default=False)
    args = parser.parse_args()

    if not args.openai_apikey:
        if not args.text or not args.bottom_right or not args.top_right or not args.top_right or not args.wood or not args.paper:
            print("Please provide all inputs or OpenAI API-key")
            return
        
    if not args.city:
        args.city = get_city()
    city_filename = args.city.replace(" ", "_")
    if not args.text:
        args.text = generate_text(f"in very few words mention one special and unknown thing about {args.city}",
                                  args.openai_apikey).content
        with open('text.txt', 'a') as texts:
            texts.write(str(args.text) + '\n\n')
    if not args.bottom_right:
        image_prompt = f"a very simple image of {args.text} in the style of {args.city}"
        args.bottom_right = generate_img(city_filename, image_prompt, args.openai_apikey, 'dall-e-3')
    if not args.top_right:
        args.top_right = generate_img(city_filename, "prompt_for_top_right", args.openai_apikey, 'dall-e-3')
    if not args.wood:
        args.wood = generate_img('wood', get_wood_prompt(args.city), args.openai_apikey)
    if not args.paper:
        args.paper = generate_img('paper', f"prompt for paper texture based on {args.city}", args.openai_apikey)

    if args.mode == 'image':
        image(args.bottom_right, args.top_right, args.text, args.wood, args.paper, show=args.show)
    elif args.mode == 'video':
        video(args.bottom_right, args.top_right, args.text, args.wood, args.paper, show=args.show)


if __name__ == '__main__':
    main()
