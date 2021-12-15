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

def reciveListVideos():
    msg = service.listVideos()
    print(msg)
    listVideos = ttk.Label(text=msg)
    listVideos.place(x=20,y=70,width=100,height=100)


def playVideo():
    video = service.playVideos()


def playVideoButton():
    playButton = ttk.Button(text="Streamar Video", master=window, command = playVideo ,style="TButton")
    playButton.place(x=20,y=40,width=80,height=20)

def listVideoButton():
    listButton = ttk.Button(text="Listar Videos", master=window, command = reciveListVideos,style="C.TButton")
    listButton.place(x=20,y=20,width=80,height=20)

# Função que cria o loop da janela
def start():
    window.title("Redes 2")
    window.geometry("500x300")
    listVideoButton()
    playVideoButton()
    window.mainloop()

start()
