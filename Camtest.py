import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se puede abrir la cámara USB")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar imagen")
        break

    cv2.imshow("Cámara USB", frame)


    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()