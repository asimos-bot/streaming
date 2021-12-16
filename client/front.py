import cv2
from client.service import streamVideo
import service
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from threading import Thread


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
    defaultValue = StringVar(window)
    defaultValue.set(listOfVideos[0])
    optionsVideos = OptionMenu(window,defaultValue,*listOfVideos,command=lambda videoTitle=listOfVideos : playVideo(videoTitle))
    optionsVideos.pack()

def showVideo(videoTitle):
    main_label = Label(window)
    main_label.pack()
    cap = cv2.VideoCapture(service.streamVideo(videoTitle))
    ret, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    tk_img = ImageTk.PhotoImage(image=img)
    main_label.configure(image=tk_img)
    main_label.tk_img = tk_img
    main_label.after(20, playVideo(videoTitle))

def playAudio(videoTitle):
    print(videoTitle)

def playVideo(videoTitle):
    Thread(target=showVideo(videoTitle)).start()
    Thread(target=playAudio(videoTitle)).start()
   
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
