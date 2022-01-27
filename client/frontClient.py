from cgitb import text
from distutils import command
import service
import tkinter
from tkinter import Tk, ttk, StringVar, OptionMenu, Frame, Label
from tkinter.messagebox import askyesno, showinfo, showwarning

class ClientGUI:
    
    quality = 240

    def __init__(self, client_ip, client_port, server_ip, server_port, service_manager_ip,service_manager_port, login, userType):
        self.login = login
        self.userType = userType
        self.setupFrame()

        self.service = service.ClientService(client_ip, client_port, server_ip, server_port, self.label, service_manager_ip,service_manager_port)
        self.service.entrarNaApp(login, userType)
        if(userType == 'premium'):
            self.setupWidgets()
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

        self.exitButton = ttk.Button(text="Sair",master=self.window,command=lambda: self.exitAplication() )
        self.exitButton.pack(side=tkinter.TOP, pady = 10)

    def exitAplication(self):
        self.service.stopVideo()
        self.service.exitApp(self.login)
        self.window.destroy()

    def setupWidgets(self):
        self.style = ttk.Style()
    
        self.excludeButton = ttk.Button(text="Parar",master=self.window,command=lambda: self.service.stopVideo()  )
        self.excludeButton.pack(side=tkinter.TOP, pady = 10)

        self.optionsVideos = OptionMenu(self.window, StringVar(), "--")
        self.optionsVideos.pack(side=tkinter.TOP, pady = 10)

        self.qualityMenu = OptionMenu(self.window,StringVar(),"--")
        self.qualityMenu.pack(side=tkinter.TOP, pady = 20)

        self.playToGroupButton = ttk.Button(text="Streamar para o Grupo",master=self.window,command=self.service.playToGroup)
        self.playToGroupButton.pack(side=tkinter.TOP, pady = 10)



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
        defaultQuality = StringVar(self.window)
        defaultQuality.set(listOfVideos[0])
        qualities = ['240p','480p','720p']
        videoQuality = StringVar(self.window)
        videoQuality.set(qualities[0])
        self.optionsVideos.destroy()
        self.qualityMenu.destroy()
        self.qualityMenu = OptionMenu(self.window,videoQuality,*qualities,command=lambda videoQuality=videoQuality: self.change_quality(videoQuality))
        self.qualityMenu.pack(side=tkinter.TOP,pady=10)
        self.optionsVideos = OptionMenu(self.window,defaultQuality,*listOfVideos,command=lambda videoTitle=listOfVideos : self.service.showVideo(videoTitle,self.quality))
        self.optionsVideos.pack(side=tkinter.TOP, pady = 10)

    def serviceManager(self):
        self.seeGroupButton = ttk.Button(text="Ver Grupo",master=self.window,command=lambda: self.seeGroup()  ,style="TButton")
        self.seeGroupButton.pack(side=tkinter.TOP, pady = 10)

        self.createGroupButton = ttk.Button(text="Criar Grupo",master=self.window,command=lambda: self.createGroup()  ,style="TButton")
        self.createGroupButton.pack(side=tkinter.TOP, pady = 10)
        
        listsUser = self.service.listUsers(self.login)

        self.selectedUser = StringVar()
        if not listsUser['LIST_USERS']:
            self.selectUsers = OptionMenu(self.window, self.selectedUser ,"--")
            self.selectUsers.pack(side=tkinter.TOP, pady = 20)
        else:
            self.selectUsers = OptionMenu(self.window, self.selectedUser, *listsUser['LIST_USERS'])
            self.selectUsers.pack(side=tkinter.TOP, pady = 20)

        self.refreshButton = ttk.Button(text="Atualizar Lista de usuários", master=self.window, command=lambda: self.getAvaliableUsers(self.service.listUsers(self.login)))
        self.refreshButton.pack(side=tkinter.TOP, pady = 20)

        self.addUserButton = ttk.Button(text="Adicionar usuário ao Grupo", master=self.window, command=self.addUserToGroup, style="TButton")
        self.addUserButton.pack(side=tkinter.TOP, pady = 10)
        
        self.removeUserButton = ttk.Button(text="Remover usuário do Grupo", master=self.window, command=lambda: self.removeUserFromGroup  ,style="TButton")
        self.removeUserButton.pack(side=tkinter.TOP, pady = 10)

    def addUserToGroup(self):
        packet = self.service.addUserToGroup(self.login, self.selectedUser.get())

        if not 'msg' in packet:
            packet = packet['ADD_USUARIO_GRUPO_ACK']
            msg = "Usuário '{}' adicionado ao Grupo {}".format(packet[0], packet[1])
        else:
            msg = packet['msg']    

        self.selectedUser.set("--")
        self.getAvaliableUsers(self.service.listUsers(self.login))
        showinfo(title="Informação do Grupo", message=msg)


    def removeUserFromGroup(self):
        packet = self.service.removeUserFromGroup(self.login)

        if not 'msg' in packet:
            packet = packet['REMOVE_USUARIO_GRUPO_ACK']
            msg = "Usuário '{}' removido do Grupo {}".format(packet[0], packet[1])
        else:
            msg = packet['msg']    

        showinfo(title="Informação do Grupo", message=msg)

    def getAvaliableUsers(self,listUsers):
        print(listUsers)
        menu = self.selectUsers["menu"]
        menu.delete(0, 'end')

        for eachUser in sorted(listUsers['LIST_USERS']):
            
            menu.add_command(label=eachUser,value=self.selectedUser.set(eachUser))

    def seeGroup(self):
        packet = self.service.seeGroup(self.login)

        if not 'msg' in packet:
            packet = packet['GRUPO_DE_STREAMING']
            msg = "ID do Grupo: {}\nProprietário: {}\nMembros: {}\n".format(packet['id'], packet['owner'], packet['members'])
        else:
            msg = packet['msg']

        showinfo(title="Informação do Grupo", message=msg)

    def createGroup(self):
        packet = self.service.createGroup(self.login)
        self.getAvaliableUsers(self.service.listUsers(self.login))

        if not 'msg' in packet:
            msg = "GRUPO CRIADO: " + packet['CRIAR_GRUPO_ACK']
        else:
            msg = packet['msg']
        
        showinfo(title="Sucesso!", message=msg)

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
