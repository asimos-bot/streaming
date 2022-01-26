from cgitb import text
from distutils import command
import service
import tkinter
from tkinter import Tk, ttk, StringVar, OptionMenu, Frame, Label

class ClientGUI:

    # Constantes de cor da interface
    backgroundColor = '#221F1F'
    fontColor = '#F5F5F1'
    red = '#E50914'
    quality = 240

    def __init__(self, client_ip, client_port, server_ip, server_port, service_manager_ip,service_manager_port, login, userType):
        self.login = login
        self.userType = userType
        self.setupFrame()
        if(userType == 'premium'):
            self.setupWidgets()
            self.setupStyle()
        self.service = service.ClientService(client_ip, client_port, server_ip, server_port, self.label, service_manager_ip,service_manager_port)
        self.service.entrarNaApp(login, userType)
        self.start()
    
    def setupFrame(self):
        self.window = Tk()
        self.width= self.window.winfo_screenwidth() 
        self.height= self.window.winfo_screenheight()
        self.frame = Frame(self.window)
        self.label = Label(self.frame)
        self.frame.pack(side=tkinter.BOTTOM, pady = 10, padx = 10, fill='both')
        self.frame.config(bg="black")
        self.label.pack()

        self.exitButton = ttk.Button(text="Sair",master=self.window,command=lambda: self.exitAplication()  ,style="TButton")
        self.exitButton.pack(side=tkinter.TOP, pady = 10)

    def exitAplication(self):
        self.service.exitApp()


    def setupWidgets(self):
        self.style = ttk.Style()
    
        self.excludeButton = ttk.Button(text="Parar",master=self.window,command=lambda: self.service.stopVideo()  ,style="TButton")
        self.excludeButton.pack(side=tkinter.TOP, pady = 10)

        self.optionsVideos = OptionMenu(self.window, StringVar(), "--")
        self.optionsVideos.pack(side=tkinter.TOP, pady = 10)

        self.qualityMenu = OptionMenu(self.window,StringVar(),"--")
        self.qualityMenu.pack(side=tkinter.TOP, pady = 20)



    def setupStyle(self):
        # Criação da estilização da interface
        self.window.configure(background=ClientGUI.backgroundColor)
        self.style.configure("TButton", font =
                       ('calibri',10,'bold'),
                        foreground = ClientGUI.red,borderwidth=4,anchor="center")
        self.style.configure('LabelList',fontColor=ClientGUI.red)

    def change_quality(self,choice):
        if choice =='480p':
            self.quality = 480
        if choice =='240p':
            self.quality = 240
        if choice == '720p':
            self.quality =  720        

    def receiveListVideos(self):
        listOfVideos = self.service.listVideos()
        listOfVideos = list(listOfVideos.values())
        listOfVideos = list(listOfVideos[0])
        defaultValue = StringVar(self.window)
        defaultValue.set(listOfVideos[0])
        qualities = ['240p','480p','720p']
        videoQuality = StringVar(self.window)
        videoQuality.set(qualities[0])
        self.optionsVideos.destroy()
        self.qualityMenu.destroy()
        self.qualityMenu = OptionMenu(self.window,videoQuality,*qualities,command=lambda videoQuality=videoQuality: self.change_quality(videoQuality))
        self.qualityMenu.pack(side=tkinter.TOP,pady=10)
        self.optionsVideos = OptionMenu(self.window,defaultValue,*listOfVideos,command=lambda videoTitle=listOfVideos : self.service.showVideo(videoTitle,self.quality))
        self.optionsVideos.pack(side=tkinter.TOP, pady = 10)

    def serviceManager(self):
        self.seeGroupButton = ttk.Button(text="Ver Grupo",master=self.window,command=lambda: self.service.seeGroup(self.login)  ,style="TButton")
        self.seeGroupButton.pack(side=tkinter.TOP, pady = 10)

        self.seeGroupButton = ttk.Button(text="Criar Grupo",master=self.window,command=lambda: self.service.createGroup(self.login)  ,style="TButton")
        self.seeGroupButton.pack(side=tkinter.TOP, pady = 10)
        
        listsUser = self.service.listUsers(self.login)

        self.selectedUser = StringVar()
        if not listsUser['LIST_USERS']:
            self.selectUsers = OptionMenu(self.window, self.selectedUser ,"--")
            self.selectUsers.pack(side=tkinter.TOP, pady = 20)
        else:
            self.selectUsers = OptionMenu(self.window, self.selectedUser, *listsUser['LIST_USERS'])
            self.selectUsers.pack(side=tkinter.TOP, pady = 20)

        print("selected user:", self.selectedUser.get())
        
        self.refreshButton = ttk.Button(text="Atualizar Lista de usuários", master=self.window, command=lambda: self.getAvaliableUsers(self.service.listUsers(self.login)))
        self.refreshButton.pack(side=tkinter.TOP, pady = 20)

        self.addUserButton = ttk.Button(text="Adicionar  usuário do Grupo", master=self.window, command=lambda: self.addUserToGroup(self.selectedUser) ,style="TButton")
        self.addUserButton.pack(side=tkinter.TOP, pady = 10)
        
        self.removeUserButton = ttk.Button(text="Remover usuário do Grupo", master=self.window, command=lambda: self.service.removeUserFromGroup(self.login)  ,style="TButton")
        self.removeUserButton.pack(side=tkinter.TOP, pady = 10)

    def addUserToGroup(self, selectedUser):
        self.service.addUserToGroup(self.login, selectedUser.get())
        selectedUser.set("--")
        self.getAvaliableUsers(self.service.listUsers(self.login))

    def getAvaliableUsers(self,listUsers):
        print(listUsers)
        menu = self.selectUsers["menu"]
        menu.delete(0, 'end')

        for eachUser in sorted(listUsers['LIST_USERS']):
            menu.add_command(label=eachUser)

    # Função que cria o loop da janela
    def start(self):
        self.window.title("Redes 2")
        self.window.geometry("%dx%d" % (self.width, self.height))   
        if(self.userType == 'premium'):
            self.receiveListVideos()
            self.serviceManager()
        self.window.mainloop()

if __name__ == "__main__":
    ClientGUI('127.0.0.1', 1100, '127.0.0.1', 6000, '127.0.0.1', 5000)
