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

    def __init__(self):
        self.setupWidgets()
        self.setupStyle()
        self.start()

    def teste(self,login,typeUser):
        service.ClientService.entrarTeste(login,typeUser)
        self.window.destroy()
        frontClient.ClientGUI('127.0.0.1', 1100, '127.0.0.1', 6000, '127.0.0.1', 5000)
    
    def setupWidgets(self):
 
        values = {  "Pago" : "Premium",
                    "Gratuito" : "Guest",
                }

        self.window = Tk()
        self.width= 400 
        self.height= 200
        self.style = ttk.Style()
        self.typeUser = StringVar(self.window, "0")
        self.login = StringVar()
        self.mod_answer=''

        self.txtLogin = ttk.Entry(master=self.window,textvariable=self.login)
        self.txtLogin.pack(side=tkinter.TOP,pady=10)

        for (text, value) in values.items():
            ttk.Radiobutton(master=self.window, text = text, variable = self.typeUser,
                value = value).pack( ipady = 5)
 
        self.logarButton = ttk.Button(text="Logar",master=self.window,command=lambda : self.teste(self.login.get(),self.typeUser.get())  ,style="TButton")
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
    Login()
    
