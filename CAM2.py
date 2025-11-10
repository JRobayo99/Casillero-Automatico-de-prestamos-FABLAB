import cv2

def main():

    cap= cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se uedo abrir la camra usb")
        exit()
        
        print("cerrar con q")



    while True:
        

        ret, frame = cap.read()
        if not ret:
            print("Error al capturar imagen")
            break
        
        cv2.imshow("Cámara USB", frame)
        
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindow()
    print("Cerrado con éxito")
