from PIL import Image
import cv2
import numpy as np
import os
import time
import argparse

def merge_images(image1, image2):
    """Merge two images into one, along the longer axis (assumes images of same size)
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    if width1 < height1:
        result_width = width1 + width2
        result_height = max(height1, height2)

        result = Image.new('RGB', (result_width, result_height))
        result.paste(im=image1, box=(0, 0))
        result.paste(im=image2, box=(width1, 0))
    else:
        result_height = height1 + height2
        result_width = max(width1, width2)

        result = Image.new('RGB', (result_width, result_height))
        result.paste(im=image1, box=(0, 0))
        result.paste(im=image2, box=(0, height1))

    return np.array(result)

if __name__ == '__main__':
    start = time.time()
    print("Merging video with bb path...")

    # vid_path = "Barpath_Lasha225SnatchClip.mp4"
    # im_path = "Barpath_Lasha225SnatchClip.png"
    parser = argparse.ArgumentParser()
    parser.add_argument("vid_path", help="Path to video")
    parser.add_argument("im_path", help="Path to image")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.vid_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if frame_width < frame_height:
        final_size = (frame_width * 2, frame_height)
    else:
        final_size = (frame_width, frame_height * 2)

    bar_path = np.empty((frame_count, frame_height, frame_width, 3), np.dtype('uint8'))
    fc = 0
    ret = True
    while (fc < frame_count  and ret):
        ret, bar_path[fc] = cap.read()
        fc += 1

    vid_name = os.path.splitext(os.path.basename(args.vid_path))[0]
    writer = cv2.VideoWriter(f"Combined_{vid_name}.mp4", cv2.VideoWriter.fourcc(*'mp4v'), fps, final_size, True)

    im = Image.open(args.im_path)
    for f in bar_path:
        vid_frame = Image.fromarray(f.astype('uint8'), 'RGB')
        writer.write(merge_images(vid_frame, im))
    writer.release()
    cap.release()

    print(f" - Done in {time.time() - start :.2f} sec")
