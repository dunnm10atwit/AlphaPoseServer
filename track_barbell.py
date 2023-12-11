from ultralytics import YOLO
import time
import numpy as np
import cv2
import os
import argparse

model = YOLO("custom_bb_detection.pt")
color_order = [(255,0,0), (255,125,0), (255,255,0), (125,255,0), (0,255,0), (0,255,125), (0,255,255), (0,125,255), (0,0,255), (125,0,255), (255,0,255), (255,0,125)]

def predict_vid(vid_path):
    results = model.predict(source=vid_path, save=False, stream=True)
    return results


def infer_points(results, threshold=50):
    # threshold: max number of frames with no prediction before inference stops
    def _average_box(xyxy):
        return (((xyxy[0] + xyxy[2]) / 2), (xyxy[1] + xyxy[3]) / 2)

    i = -1
    last_found_index = -1
    barbell_end_points = []
    for result in results:
        i += 1
        if result.boxes.cls.tolist().count(1) > 0:
            # find most confident barbell end and average box to a single point that is saved in barbell_end_points
            conf = result.boxes.conf.tolist()
            cls = result.boxes.cls.tolist()
            max_in = -1
            max_val = -1
            for j in range(len(cls)):
                if cls[j] == 1 and conf[j] > max_val:
                    max_in = j
                    max_val = conf[j]
            
            xyxy = result.boxes.xyxy.tolist()[max_in]
            barbell_end_points.append(_average_box(xyxy))

            # back fill inferred results from last found index to current index
            if last_found_index != -1 and i != last_found_index + 1 and i - last_found_index < threshold:
                m_y = (barbell_end_points[i][1] - barbell_end_points[last_found_index][1]) / (i - last_found_index)
                m_x = (barbell_end_points[i][0] - barbell_end_points[last_found_index][0]) / (i - last_found_index)
                for k in range(last_found_index + 1, i):
                    y = m_y * (k - i) + barbell_end_points[i][1]
                    x = m_x * (k - i) + barbell_end_points[i][0]
                    barbell_end_points[k] = (x, y)
            last_found_index = i
        else:
            barbell_end_points.append((0, 0))
    return np.array(barbell_end_points)


def create_barpath(vid_path):
    start = time.time()
    print("Processing...")

    points = infer_points(predict_vid(vid_path))

    cap = cv2.VideoCapture(vid_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    bar_path = np.empty((frame_count, frame_height, frame_width, 3), np.dtype('uint8'))
    fc = 0
    ret = True
    while (fc < frame_count  and ret):
        ret, bar_path[fc] = cap.read()
        fc += 1

    vid_name = os.path.splitext(os.path.basename(vid_path))[0]
    writer = cv2.VideoWriter(f"Barpath_{vid_name}.mp4", cv2.VideoWriter.fourcc(*'mp4v'), fps, (frame_width, frame_height), True)

    # trace bar path and output
    i = 0
    for f in bar_path:
        j = 0
        for k in range(i):
            if j >= len(color_order):
                j = 0
            if int(points[k][0]) != 0 and int(points[k][1]) != 0:
                cv2.circle(f, (int(points[k][0]), int(points[k][1])), radius=3, color=color_order[j], thickness=-1)
            j += 1
        writer.write(f)
        i += 1
    writer.release()
    cap.release()
    
    bar_path[frame_count - 1].fill(0)
    j = 0
    for k in range(i - 1):
        if j >= len(color_order):
            j = 0
        if int(points[k][0]) != 0 and int(points[k][1]) != 0:
            cv2.circle(bar_path[frame_count - 1], (int(points[k][0]), int(points[k][1])), radius=3, color=color_order[j], thickness=-1)
        if k != 0 and (int(points[k][0]) != 0 and int(points[k][1]) != 0) and int(points[k -1 ][0]) != 0 and int(points[k - 1][1]) != 0:
            cv2.line(bar_path[frame_count - 1], (int(points[k][0]), int(points[k][1])), (int(points[k - 1][0]), int(points[k - 1][1])), color=(255, 0, 0), thickness=1) 
        j += 1
    cv2.imwrite(f"Barpath_{vid_name}.png", bar_path[frame_count - 1])
    
    print(f"Done in {time.time() - start:.2f} sec")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("vid_path", help="Path to video")
    args = parser.parse_args()
    create_barpath(args.vid_path)
    
