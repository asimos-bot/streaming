from tkinter import *
from tkinter import ttk
import service

window = Tk()

# Constantes de cor da interface
backgroundColor = 'E0E0CE'
fontColor = '#333333'
pressedButtonColor = '#474747'

# Criação da estilização da interface
ttk.Style().configure("BW.TLabel", foreground=fontColor)
ttk.Style().map("C.TButton",anchor="center")


def playVideoButton():
    searchButton = ttk.Button(text="Streamar Video", master=window, command = service.playVideos,style="TButton")
    searchButton.place(x=20,y=40,width=80,height=20)

def listVideoButton():
    saveButton = ttk.Button(text="Listar Videos", master=window, command = service.listVideos,style="C.TButton")
    saveButton.place(x=20,y=20,width=80,height=20)

# Função que cria o loop da janela
def start():
    window.title("Redes 2")
    window.geometry("500x300")
    listVideoButton()
    playVideoButton()
    window.mainloop()

start()
