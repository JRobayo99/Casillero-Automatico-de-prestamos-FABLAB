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
        usuarios_anteriores = list(material_usuarios.get(material, []))
        if usuarios_anteriores:
        
            print(f"Antes de agregar a '{usuario}', los últimos 2 usuarios que usaron '{material}' son: {usuarios_anteriores}")
            
        else:
            print(f"'{material}' no tiene usuarios anterios registrados. ")
            
    for material in materiales:
        material_usuarios[material].append(usuario)
        
    print(f"Registro actualizado para {usuario}.\n")
print ("Programa terminado.")