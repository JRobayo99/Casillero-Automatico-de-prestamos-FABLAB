# Proyecto de casillero de fablab. 🗂️​​📋​​🧰​​

## Introducción:

El proposito de la automatización de porcesos es beneficiar la porductividad y calidad de vida de los colaboradores, cuando se realicen prestamos de hermamientas,
en si los tableros de automaticos no solo tienen un uso de prestamo si no también en usos comerciales como uso alternitvo principal, este program hacer parte de un proyecto de naturaleza similar,
casillero automatico de prestamos para el FABLAB, es utiliza una serie de tecnológias asociadas entre si para dar uan mejor experiencia al usuario final que es el estudiante.
 
# Especificaciones técnicas ⚙️🛠️


### Hadware. ⚙️​🔧​

- Raspebrry PI 4 model B 🍇​🍓​
- Modulo MCP23017 (Modulo extensor de 16 pines)
- Pantalla touch de (1024x600) 🖥️​
- Camara web de alta definición con enfoque manual (1920x1080) 📷​
- Camara web cam con autoenfoque 📷​ 
- Solenoides
- Módulo rele 5V -12

### Software. 💻👨‍💻​​👩‍💻​​​
- Python version 3.10 🐍​
- Rapios arm_g4 (Bullseye-arm64)
#### Librerías de Python. 🗂️​🐍​
  - zxingcpp (Lector de código de barras)
  - opencv (procesador de imagenes)
  - adafruit (Soporte de modulos de extensión MCP2027)
  - Tkinter (interfaz gráfica)
  - Pandas (Gestión de base de datos)
  - IC2 (IC2 tools, IC2-dev, IC2-bcm2835)
  - Módulo MCP23017IO (0X23 0X25 0X26 0X27)
    
## Diagrama flujo. 🔁​​🔀

<img width="1920" height="1080" alt="Inicio" src="https://github.com/user-attachments/assets/c8a4a485-e111-44e5-b297-43684054ba1d" />

## Digrama de conexiones. ⚡​➡️​📟​

### Raspberry 🍇​🍓 ---> MCP23017 

 |Conectores MCP23017|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |       VCC(5V)   | PIN 2 (5V POWER)                  | 
 |  GND |  PIN 6 (GND) |
 | SDA | PIN 3 (GPIO 2 (SDA))|
 | SCL | PIN 5 (GPIO 3 (SCL)) |
 | INTA | No es necesario conectar|
 |INT B | No es necesario conectar |

### Raspberry 🍇​🍓 ---> Tira led 🔦

 |Conectores Tira LED|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |GND| PIN 39 (GND) |
 |5 VCC| PIN 4 (5 VCC power)| 
 |Signal| PIN 12 (GPIO 18 (PCM_CLK))|


### Raspberry 🍇​🍓 ---> Camaras web y pantalla touch 🖥️📷​

 |Conectores Tira LED|Conectores Rasberry pi 4 Model B|
 | ----------------- | ------------------------------- |
 |Conector UBS de (Camara web de alta definición con enfoque manual (1920x1080) 📷)| Puerto USB 3.0|
 |Camara web cam con autoenfoque 📷​ |Puerto USB 3.0|
 |Puerto HDMI Pantalla touch de (1024x600)🖥️| Puerto HDMI0|
 |Puerto Touch Pantalla touch de (1024x600)🖥️ | Puerto USB 2.0|



