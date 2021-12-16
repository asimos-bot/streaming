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
                foreground = red,borderwidth=4,anchor="center")
style.configure('LabelList',fontColor=red)

def receiveListVideos():
    posX = 230
    posY = 200
    listOfVideos = service.listVideos()
    for video in listOfVideos:
        videoButton = ttk.Button(text=video, master=window)
        videoButton["command"] = lambda videoTitle=video: playVideo(videoTitle)
        videoButton.place(x=posX,y=posY,width=50,height=25)
        posY+=40

def playVideo(videoTitle):
    print('Titulo quando eu clico',videoTitle)
    playedVideo = service.playVideos(videoTitle)
    #renderizar o broadCast?

def listVideoButton():
    listButton = ttk.Button(text="Listar", master=window, command = receiveListVideos,style="TButton")
    listButton.place(width=80,height=20)
    listButton.pack(pady=6)

# Função que cria o loop da janela
def start():
    window.title("Redes 2")
    window.geometry("500x300")
    listVideoButton()
    window.mainloop()

start()
