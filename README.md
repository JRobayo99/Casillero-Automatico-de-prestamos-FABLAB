# Proyecto de Casillero Automático de Prestamos de FABLAB. 🗂️​​📋​​🧰​​

## Introducción:

El proposito de la automatización de procesos es beneficiar la porductividad y calidad de vida de los colaboradores, cuando se realicen prestamos de herramientas,
en si los tableros de automáticos no solo tienen un uso de préstamo si no también en usos comerciales como uso alternitvo principal, este programa hacer parte de un proyecto de naturaleza similar,
casillero automático de préstamos para el FABLAB, es utiliza una serie de tecnológias asociadas entre si para dar una mejor experiencia al usuario final que es el estudiante.
 
# Especificaciones técnicas. ⚙️🛠️


### Hadware. ⚙️​🔧​

- Raspebrry PI 4 model B 🍇​🍓​
- Módulo MCP23017 (Módulo extensor de 16 pines)
- Pantalla touch de (1024x600) 🖥️​
- Cámara web de alta definición con enfoque manual (1920x1080) 📷​
- Cámara web cam con autoenfoque 📷​ 
- Solenoides 5V - 12V
- Módulo rele 5V - 12V

### Software. 💻👨‍💻​​👩‍💻​​​
- Python version 3.9.2 🐍​
- Raspios arm_g4 (Bullseye-arm64) --> descargar aquí ( https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2023-05-03/ )
#### Librerías de Python. 🗂️​🐍​
  - Zxingcpp (Lector de código de barras)
  - Opencv (procesador de imagenes)
  - Adafruit, Adafruit blinka (Soporte de módulos de extensión MCP2027)
  - Tkinter (interfaz gráfica)
  - Pandas (Gestión de base de datos)
  - IC2 (IC2 tools, IC2-dev, IC2-bcm2835)
  - Módulo MCP23017IO (0X23 0X25 0X26 0X27)
  - Tesseract OCR --> (pytesseract)
    
## Diagrama flujo. 🔁​​🔀

<img width="1920" height="1080" alt="Inicio" src="https://github.com/user-attachments/assets/c8a4a485-e111-44e5-b297-43684054ba1d" />



## Digrama de conexiones. ⚡​➡️​📟​

<img width="1210" height="642" alt="image" src="https://github.com/user-attachments/assets/a7fd8dea-197c-4a25-8b83-6328b62cd04b" />






### Raspberry 🍇​🍓 ---> MCP23017 

<img width="636" height="414" alt="image" src="https://github.com/user-attachments/assets/9292bde8-d1f4-4e8d-9818-8eda22ccd902" />




 |Conectores MCP23017|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |       VCC(5V)   | PIN 2 (5V POWER)                  | 
 |  GND |  PIN 6 (GND) |
 | SDA | PIN 3 (GPIO 2 (SDA))|
 | SCL | PIN 5 (GPIO 3 (SCL)) |
 | INT A | No es necesario conectar|
 |INT B | No es necesario conectar |

### Raspberry 🍇​🍓 ---> Tira led 🔦

 |Conectores Tira LED|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |GND| PIN 39 (GND) |
 |5 VCC| PIN 4 (5 VCC power)| 
 |Signal| PIN 12 (GPIO 18 (PCM_CLK))|


### Raspberry 🍇​🍓 ---> Cámaras web y pantalla touch 🖥️📷​

 |Conectores Tira LED|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |Conector UBS de (Cámara web de alta definición con enfoque manual (1920x1080) 📷)| Puerto USB 3.0|
 |Cámara web cam con autoenfoque 📷​ |Puerto USB 3.0|
 |Puerto HDMI Pantalla touch de (1024x600)🖥️| Puerto HDMI - 0|
 |Puerto Touch Pantalla touch de (1024x600)🖥️ | Puerto USB 2.0|



