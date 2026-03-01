import cv2
import pytesseract
from pytesseract import Output

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:

    ret, frame= cap.read()
    d = pytesseract.image_to_data(frame, lang='spa', output_type=Output.DICT)
    cant_cajas= len(d['text'])
    for i in range(cant_cajas):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])

            if text and text.strip() != "":
                cuadro = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cuadro = cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
