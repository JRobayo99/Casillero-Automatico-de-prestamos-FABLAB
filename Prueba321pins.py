import tkinter as tk
import busio
import board
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c= busio.I2C(board.SCL, board.SDA)

mcpA = MCP23017(i2c, address=0x27)
mcpB = MCP23017(i2c, address=0x23)

pinsA = {}
pinsB = {}

for i in range(16):
    pA= mcpA.get_pin(i)
    pA.switch_to_output(value=True)
    pinsA[i] = pA

    pB= mcpB.get_pin(i)
    pB.switch_to_output(value=True)
    pinsB[i] = pB

stateA= [False]*16
stateB= [False]*16

def activar_por_numero(n):
    if n < 1 or n > 32:
        print("Número fuera de rango")
        return
    if n <= 16:
        pinsA[n-1].value = False
        
    else:
        pinsB[n-17].value = False
        

root = tk.Tk()
root.title("Control de MCP23017 (0x23)(0x27)")
root.geometry("600x700")

tk.Label(root, text= "MCP23017 0X27 (A)", font=("Arial", 14)).pack()

frameA = tk.Frame(root)
frameA.pack(pady=10)

for i in range(16):
    b = tk.Button(frameA, text=f"A{i}", width=6, height=2, bg="gray",
                  command=lambda p=i, btn=None: None)
    b.grid(row=i//8, column=i%8, padx=5, pady=5)
    b.config(command=lambda p=i, btn=b: toggle_A(p, btn))

tk.Label(root, text= "MCP23017 0X23 (B)", font=("Arial", 14)).pack()

frameB = tk.Frame(root)
frameB.pack(pady=10)

for i in range(16):
    b = tk.Button(frameB, text=f"B{i}", width=6, height=2, bg="gray",
                  command=lambda p=i, btn=None: None)
    b.grid(row=i//8, column=i%8, padx=5, pady=5)

root.mainloop()