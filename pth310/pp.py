import tkinter as tk

ventanai=tk.Tk()

ventanai.title("Casillero de pretamos")
ventanai.geometry("600x400")
ventanai.config(bg="CadetBlue1")

frame1= tk.Frame(ventanai)
frame1.configure(bg="sienna1", width=300, height=200, bd=5)



frame1.pack()



ventanai.mainloop()