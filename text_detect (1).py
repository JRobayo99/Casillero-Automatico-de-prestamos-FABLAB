import cv2
import easyocr
import numpy as np

import sys

reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

video = cv2.VideoCapture(0)
ret, _ = video.read()

frame_count = 0

def filtro(mask):
    
    #fill gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    #particles
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel2)
    
    inv = cv2.bitwise_not(clean)#invert image
    return inv

while ret:
    ret, frame = video.read()
    if ret == False:
        sys.log("Error de sispositivo de video")

    height, width, _ = frame.shape
    #frame = cv2.flip(frame, 1)
    frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #Filters
    blur = cv2.GaussianBlur(frame_g, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8, 8))
    contrast = clahe.apply(blur)
    frame_gth = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 1, 11, 2)
    frame_gth = cv2.medianBlur(frame_gth, 5)
    frame_gth = filtro(frame_gth)

    frame_clear = filtro(frame_g)
    
    #detect Text
    result = reader.readtext(frame_clear)
    for detection in result:
        box, text, conf = detection
        box = [[int(x) for x in subl] for subl in box]

        #drawing
        x_center = box[0][0] + round((box[2][0] - box[0][0])/2)
        y_center = box[0][1] + round((box[2][1] - box[0][1])/2)
        cv2.circle(frame, (x_center, y_center), 4, (0,0,255), 10)
        cv2.putText(frame, text, box[0],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 0),
                    2,
                    cv2.LINE_AA
                    )
        cv2.putText(frame, str(round(conf, 3)), (box[3][0], box[3][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0), 
                    1,
                    cv2.LINE_AA
                    )
        cv2.rectangle(frame, 
                      (box[0]), #vertex 1
                      (box[2]), #vertex 2
                      (0, 255, 255), 2)
        #trace
        if frame_count == 10:
            last_c = (x_center, y_center)
        if frame_count > 10:
            cv2.line(frame, last_c, (x_center, y_center), (0, 0, 255), 3)
            last_c = (x_center, y_center)
        else:
            frame_count = frame_count + 1

    fr_up = np.hstack((frame, cv2.cvtColor(frame_g, cv2.COLOR_GRAY2BGR)))
    fr_down = np.hstack((cv2.cvtColor(frame_gth, cv2.COLOR_GRAY2BGR),
                         cv2.cvtColor(frame_clear, cv2.COLOR_GRAY2BGR)))
    frames = np.vstack((fr_up, fr_down))
    cv2.imshow("Frames", frames)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        break
cv2.destroyAllWindows()
