from ctypes import string_at
import tkinter
import service
from tkinter import Button, Tk, ttk, StringVar, OptionMenu, Frame, Label


class ClientGerenciador:
    # Constantes de cor da interface
    backgroundColor = '#221F1F'
    fontColor = '#F5F5F1'
    red = '#E50914'
    quality = 0
   

    def __init__(self):
        self.setupWidgets()
        self.setupStyle()
        self.start()

    def setupWidgets(self):
        self.window = Tk()
        self.width= self.window.winfo_screenwidth() 
        self.height= self.window.winfo_screenheight()
        self.style = ttk.Style()
        login = StringVar()
        password = StringVar()

        self.loginTxt = ttk.Entry(self.window,textvariable=login)
        self.loginTxt.pack(side=tkinter.TOP, pady = 10)

        self.passwordTxt = ttk.Entry(self.window,textvariable=password)
        self.passwordTxt.pack(side=tkinter.TOP, pady = 10)

        self.loginBtn = ttk.Button(text="Logar",master=self.window,command=lambda: service.login(login.get(),password.get())  ,style="TButton")
        self.loginBtn.pack(side=tkinter.TOP, pady = 20)

    def setupStyle(self):
        # Criação da estilização da interface
        self.window.configure(background=ClientGerenciador.backgroundColor)
        self.style.configure("TButton", font =
                       ('calibri',10,'bold'),
                        foreground = ClientGerenciador.red,borderwidth=4,anchor="center")
        self.style.configure('LabelList',fontColor=ClientGerenciador.red)

    def start(self):
        self.window.title("Redes 2")
        self.window.geometry("%dx%d" % (self.width, self.height))    
        self.window.mainloop()


if __name__ == "__main__":
    ClientGerenciador()
