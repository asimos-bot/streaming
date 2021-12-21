import service
from tkinter import Tk, Variable, ttk, StringVar, OptionMenu, Frame, Label

class ClientGUI:

    # Constantes de cor da interface
    backgroundColor = '#221F1F'
    fontColor = '#F5F5F1'
    red = '#E50914'


    def __init__(self, client_ip, client_port, server_ip, server_port):
        self.setupWidgets()
        self.service = service.ClientService(client_ip, client_port, server_ip, server_port, self.label)
        self.setupStyle()
        self.start()

    def setupWidgets(self):

        self.window = Tk()
        self.width= self.window.winfo_screenwidth() 
        self.height= self.window.winfo_screenheight()
        self.style = ttk.Style()
        self.frame = Frame(self.window)
        self.label = Label(self.frame)
        self.frame.place(x=30, y=100)
        self.frame.config(bg="black")
        self.label.grid(row=600, column=0, padx=10, pady=2)
        self.label.pack()
        self.videoSelected = ''

    def setupStyle(self):
        # Criação da estilização da interface
        self.window.configure(background=ClientGUI.backgroundColor)
        self.style.configure("TButton", font =
                       ('calibri',10,'bold'),
                        foreground = ClientGUI.red,borderwidth=4,anchor="center")
        self.style.configure('LabelList',fontColor=ClientGUI.red)


    def receiveListVideos(self):
        listOfVideos = self.service.listVideos()
        listOfVideos = list(listOfVideos.values())
        listOfVideos = list(listOfVideos[0])
        defaultValue = StringVar(self.window)
        defaultValue.set(listOfVideos[0])
        optionsVideos = OptionMenu(self.window,defaultValue,*listOfVideos,command=lambda videoTitle=listOfVideos : self.service.showVideo(videoTitle))
        optionsVideos.pack()
        excludeButton = ttk.Button(text="Parar",master=self.window,command=lambda: self.service.stopVideo()  ,style="TButton")
        excludeButton.place(x=(self.width//2),y=100)

    def listVideoButton(self):
        listButton = ttk.Button(text="Listar", master=self.window, command = self.receiveListVideos,style="TButton")
        listButton.place(width=80,height=20)
        listButton.pack(pady=6)

    # Função que cria o loop da janela
    def start(self):
        self.window.title("Redes 2")
        self.window.geometry("%dx%d" % (self.width, self.height))    
        self.listVideoButton()
        self.window.mainloop()

if __name__ == "__main__":
    ClientGUI('127.0.0.1', 5050, '127.0.0.1', 6000)
