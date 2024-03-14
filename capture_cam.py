import cv2
import numpy as np
from ultralytics import YOLO


def read_write_video(inpath, outpath=None, portrait=False):
    cap = cv2.VideoCapture(inpath)

    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    if portrait:
        w = 800
        h = 1200
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frm = cv2.VideoWriter_fourcc(*'MJPG')
    if outpath:
        vw = cv2.VideoWriter(outpath, frm, 25.0, (w,h), )
        return cap, vw
    return cap


class YOLOSegmentation:
  def __init__(self, model_path='/Users/galgo/code/pythonProject/yolov8m-seg.pt'):
    self.model = YOLO(model_path)

  def detect(self, img):
    h, w, c = img.shape

    results = self.model.predict(source=img.copy(), save=False, save_txt=False)
    result = results[0]
    segmentation_contours_idx = []
    if not result:
        print('if not result')
        return
    for seg in result.masks.xyn:
      seg[:, 0] *= w
      seg[:, 1] *= h
      segment = np.array(seg, dtype=np.int32)
      segmentation_contours_idx.append(segment)

    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    class_ids = np.array(result.boxes.cls.cpu(), dtype="int")
    scores = np.array(result.boxes.conf.cpu(), dtype="float").round(2)
    return bboxes, class_ids, segmentation_contours_idx, scores


def person_to_texture(image, texture, bg, yolo_instance: YOLOSegmentation):
    # yolo on image
    # person to contour
    from utils import scale_and_crop_center
    # TODO darken surface
    # TODO track center of person
    y, x, _ = image.shape

    scaled_texture = scale_and_crop_center(texture, x, y)
    shadow_image = scale_and_crop_center(bg, x, y)

    detections = yolo_instance.detect(image)
    if not detections:
        print('not detections')
        return False, scaled_texture
    
    bboxes, class_ids, segmentation_contours_idx, scores = detections
    mask = np.zeros_like(image)
    # shadow_image = np.zeros(image.shape)
    for bb, id, seg, sc in zip(bboxes, class_ids, segmentation_contours_idx, scores):
        if id == 0:
            cv2.drawContours(mask, [seg], 0, (255, 255, 255), -1)
    bool_mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY) > 0
    # for c in range(3):
    shadow_image[bool_mask] = scaled_texture[bool_mask]
    
    return True, shadow_image


def debug_capture_cam():
    ys = YOLOSegmentation()
    
    cap = read_write_video(0)
    t, im = cap.read()
    texture = cv2.imread(f'/Users/galgo/code/aalto-2/black_wood_5.png')
    bg = cv2.imread(f'/Users/galgo/code/aalto-2/paper1.jpeg')
    cv2.startWindowThread()
    while t:
        cv2.imshow('shadow_cam', person_to_texture(im, texture, bg, ys))
        t, im = cap.read()
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()



