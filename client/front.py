import service
from tkinter import Tk, Variable, ttk, StringVar, OptionMenu, Frame, Label

# Definição de constantes da janela e do frame de exibição do video
window = Tk()
width= window.winfo_screenwidth() 
height= window.winfo_screenheight()
style= ttk.Style()
f1 = Frame(window)
l1 = Label(f1)
f1.place(x=30, y=100)
f1.config(bg="black")
l1.grid(row=600, column=0, padx=10, pady=2)
l1.pack()

# Constantes de cor da interface
backgroundColor = '#221F1F'
fontColor = '#F5F5F1'
red = '#E50914'
videoSelected = ''


# Criação da estilização da interface
window.configure(background=backgroundColor)
style.configure("TButton", font =
               ('calibri',10,'bold'),
                foreground = red,borderwidth=4,anchor="center")
style.configure('LabelList',fontColor=red)

# Receber a listagem de videos disponiveis no servidors
def receiveListVideos():
    listOfVideos = service.listVideos()
    listOfVideos = list(listOfVideos.values())
    listOfVideos = list(listOfVideos[0])
    defaultValue = StringVar(window)
    defaultValue.set(listOfVideos[0])
    optionsVideos = OptionMenu(window,defaultValue,*listOfVideos, command=setVideoSelected(defaultValue))
    optionsVideos.pack()
    excludeButton = ttk.Button(text="Excluir",master=window,command=lambda: excluir()  ,style="TButton")
    excludeButton.place(x=(width//2),y=100)
    playButton = ttk.Button(text="Play",master=window,command= service.showVideo(videoSelected,l1))
    playButton.place(x=(width//2)+ 100,y=100)


def excluir():
    print(videoSelected)

# Criação do botão na tela
def listVideoButton():
    listButton = ttk.Button(text="Listar", master=window, command = receiveListVideos,style="TButton")
    listButton.place(width=80,height=20)
    listButton.pack(pady=6)

def setVideoSelected(valueSelected):
    videoSelected = valueSelected.get()

# Função que cria o loop da janela
def start():
    window.title("Redes 2")
    window.geometry("%dx%d" % (width, height))    
    listVideoButton()
    window.mainloop()


start()