from cgi import test
import tkinter
from tokenize import String
import frontClient
from tkinter import Button, Tk, ttk, StringVar, OptionMenu, Frame, Label
import service

class Login:
    backgroundColor = '#221F1F'
    fontColor = '#F5F5F1'
    red = '#E50914'

    def __init__(self,client_ip, client_port, streaming_ip, streaming_port, service_manager_ip, service_manager_port):
        self.client_ip = client_ip
        self.client_port = client_port
        self.streaming_ip = streaming_ip
        self.streaming_port = streaming_port
        self.service_manager_ip = service_manager_ip
        self.service_manager_port = service_manager_port

        self.setupWidgets()
        self.setupStyle()
        self.start()

    def login(self,login,typeUser):
        self.window.destroy()
        frontClient.ClientGUI(self.client_ip, self.client_port, self.streaming_ip, self.streaming_port, self.service_manager_ip, self.service_manager_port, login, typeUser)
    
    def setupWidgets(self):
        self.window = Tk()
        self.frame = Frame(self.window)
        self.label = Label(self.frame)
        values = {  "Pago" : "premium",
                    "Gratuito" : "guest",
                }

        self.width= 400 
        self.height= 200
        self.style = ttk.Style()
        self.typeUser = StringVar(self.window, "0")
        self.login_str = StringVar()
        self.mod_answer=''

        self.txtLogin = ttk.Entry(master=self.window,textvariable=self.login_str)
        self.txtLogin.pack(side=tkinter.TOP,pady=10)

        for (text, value) in values.items():
            ttk.Radiobutton(master=self.window, text = text, variable = self.typeUser,
                value = value).pack( ipady = 5)
 
        self.logarButton = ttk.Button(text="Logar",master=self.window,command=lambda : self.login(self.login_str.get(),self.typeUser.get())  ,style="TButton")
        self.logarButton.place(x=150,y=100)


    def setupStyle(self):
        # Criação da estilização da interface
        self.window.configure(background=Login.backgroundColor)
        self.style.configure("TButton", font =
                       ('calibri',10,'bold'),
                        foreground = Login.red,borderwidth=4,anchor="center")
        self.style.configure('LabelList',fontColor=Login.red)
   
    def start(self):
        self.window.title("Redes 2")
        self.window.geometry("%dx%d" % (self.width, self.height))    
        self.window.mainloop()

    def close(self):
        self.window.destroy()

if __name__ == "__main__":
    Login('127.0.0.1', 1101, '127.0.0.1', 6000, '127.0.0.1', 5000)
    
