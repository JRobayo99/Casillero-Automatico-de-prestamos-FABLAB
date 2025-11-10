import tkinter as tk
from collections import defaultdict, deque

materiales_usuarios = defaultdict(lambda: deque(maxlen=2))

MATERIALES =['Madera', 'Metal', 'Plástico','Vidrio', 'Cerámica']

def agregar_usuarios():
    usuario = entry_usuario.get().strip()
    if not usuario:
        label_status.config(text ="Ingrese un nombre de usuario. ")
        return
    
    materiales_seleccionados = [m for m, var in check_vars.items() if var.get()]
    if not materiales_seleccionados:
        label_status.config(text= "Seleccione al menos un material. ")
        return
    
    for material in materiales_seleccionados:
        materiales_usuarios[material].append(usuario)
        
    label_status.config(text=f"Registro actualizado para  {usuario}. ")
    entry_usuario.delete(0, tk.END)
    for var in check_vars.values():
        var.set(False)
        
def consultar_material():
    material = var_material_consulta.get()
    usuarios = materiales_usuarios.get(material)
    if usuarios:
        
        lista_usuarios = list(usuarios)
        label_resultado.config(text= f"Últimos usuarios de '{material}': {', '.join(lista_usuarios)}")
    else:
        label_resultado.config(text=f"No hay registro para le material '{material}'.")
        
root = tk.Tk()
root.title("Registro de Materiales")

root.attributes("-zoomed", True)

tk.Label(root, text="Nombre de usuario:").pack()
entry_usuario =tk.Entry(root)
entry_usuario.pack()


tk.Label(root, text="Seleccione materiales usados (hasta 3): ").pack()
check_vars = {}

for  material in MATERIALES:
    var = tk.BooleanVar()
    cb = tk.Checkbutton(root, text=material, variable=var)
    cb.pack(anchor= 'w')
    check_vars[material] = var
    
btn_agregar = tk.Button(root, text="Agregar Usuario", command =agregar_usuarios)
btn_agregar.pack(pady=5)

label_status = tk.Label(root,text= "")
label_status.pack()

tk.Label(root,text="").pack()

tk.Label(root, text="Consultar últimos usuarios por material:").pack()


var_material_consulta = tk.StringVar(value=MATERIALES[0])
dropdown = tk.OptionMenu (root, var_material_consulta, *MATERIALES)
dropdown.pack()

btn_consultar= tk.Button(root, text= "Consultar", command=consultar_material)
btn_consultar.pack(pady=5)

label_resultado = tk.Label(root, text="")
label_resultado.pack()

root.mainloop()