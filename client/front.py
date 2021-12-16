from tkinter import *
from tkinter import ttk
from tkinter import font
import service

window = Tk()
style= ttk.Style()

# Constantes de cor da interface
backgroundColor = '#221F1F'
fontColor = '#F5F5F1'
red = '#E50914'

# Criação da estilização da interface
window.configure(background=backgroundColor)
style.configure("TButton", font =
               ('calibri',10,'bold'),
                foreground = red,borderwidth=4,anchor="center",_Padding='10')
style.configure('LabelList',fontColor=red)

def reciveListVideos():
    posX = 200
    posY = 200
    listVideos = service.listVideos()
    for video in listVideos:
        videoButton = ttk.Button(textvariable=video, master=window, command = playVideo(video) ,style="TButton")
        videoButton.place(posX,posY,width=100,height=100)
        posX+=20
        posY+=20

def playVideo(videoTitle):
    playedVideo = service.playVideos(videoTitle)
    #renderizar o broadCast?


def playVideoButton():
    playButton = ttk.Button(text="Streamar", master=window, command = playVideo ,style="TButton")
    playButton.place(width=80,height=20)
    playButton.pack(pady=4)

def listVideoButton():
    listButton = ttk.Button(text="Listar", master=window, command = reciveListVideos,style="TButton")
    listButton.place(width=80,height=20)
    listButton.pack(pady=6)

# Função que cria o loop da janela
def start():
    window.title("Redes 2")
    window.geometry("500x300")
    listVideoButton()
    playVideoButton()
    window.mainloop()

start()
