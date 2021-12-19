import cv2
import service
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import base64
import numpy as np

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
    listOfVideos = service.listVideos()
    listOfVideos = list(listOfVideos.values())
    listOfVideos = list(listOfVideos[0])
    defaultValue = StringVar(window)
    defaultValue.set(listOfVideos[0])
    optionsVideos = OptionMenu(window,defaultValue,*listOfVideos,command=lambda videoTitle=listOfVideos : showVideo(videoTitle))
    optionsVideos.pack()

def showVideo(videoTitle):
    service.video_stream(videoTitle)

    
   
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
