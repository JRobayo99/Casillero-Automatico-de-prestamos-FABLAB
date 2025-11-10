from collections import defaultdict, deque

material_usuarios = defaultdict(lambda: deque (maxlen=2))


while True:
    

    
    usuario= input("Ingresa el nombre de usuario(o escribe salir para terminar): ").strip()
    
    if usuario.lower()== "salir":
        
        break
        
    materiales_input= input(f"Ingrese hasta materiales usados por {usuario}, separados por comas:   ")
    materiales= [m.strip() for m in materiales_input.split (",") if m.strip()]
    
    materiales = materiales[:3]
    
    for material in materiales:
        material_usuarios[material].append(usuario)
        
    print (f"Registro actulizado par {usuario}. ")
    
print ("\nConsulta de materiales (escribe 'salir' para terminar): ")

while True:
    
    material_consulta = input("Ingrese el material para ver los 2 últimos usarios: ").strip()
    
    if material_consulta.lower() == "salir":
    
        print("Programa termiando")
        break
    
    usuarios_que_usaron = material_usuarios.get(material_consulta)
    
    if usuarios_que_usaron:
        print(f"Los dos últimos usarios que usaron '{material_consulta}' son: {list(usuarios_que_usaron)}")
        
    else:
        
        print(f"No hay registro spar ale material'{material_consulta}'.")