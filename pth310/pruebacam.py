import cv2
cap = cv2.VideoCapture(0)
print("Camara abierta:", cap.isOpened())


print("WIDTH:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("HEIGHT:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()