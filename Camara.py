import cv2

def main():
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("No se conecto la camara")
        return
    
    print("Cámara abierta correctamente")
    
    while True:
        
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar imagen")
            break
        
        cv2.imshow('Vista de la Cámara', frame)
        
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        
        elif key == ord('s'):
            cv2.imwrite('Captura.jpg', frame)
            print("Imagen guardada como 'Captura.jpg")
            
    cap.release()
    cv2.destroyAllWindows()
    
if __name__=='__main__':
    
    main()
