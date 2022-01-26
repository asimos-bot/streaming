from glob import glob
import tkinter
import os, shutil
from tkinter import Tk, ttk, StringVar, OptionMenu, Frame, Label, Text
from tkinter.filedialog import askopenfile
from tkinter.messagebox import askyesno, showerror
from video_resizer import VideoResizer


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
        self.frame = Frame(self.window)
        self.label = Label(self.frame)
        self.frame.pack(side=tkinter.BOTTOM, pady = 10, padx = 10, fill='both')
        self.frame.config(bg="black")
        self.label.pack()

        #self.excludeButton = ttk.Button(text="Parar",master=self.window,command=lambda: self.service.stopVideo()  ,style="TButton")
        #self.excludeButton.pack(side=tkinter.TOP, pady = 10)

        self.optionsVideos = OptionMenu(self.window, StringVar(), "--")
        self.optionsVideos.pack(side=tkinter.TOP, pady = 10)

        self.upload_button = ttk.Button(text="Upload", master=self.window, command=lambda : self.uploadFile(), style="TButton")
        self.upload_button.pack()

        # self.qualityMenu = OptionMenu(self.window,StringVar(),"--")
        # self.qualityMenu.pack(side=tkinter.TOP, pady = 20)

    
    def setupStyle(self):
        # Criação da estilização da interface
        self.window.configure(background=ClientGerenciador.backgroundColor)
        self.style.configure("TButton", font =
                       ('calibri',10,'bold'),
                        foreground = ClientGerenciador.red,borderwidth=4,anchor="center")
        self.style.configure('LabelList',fontColor=ClientGerenciador.red)

    def removeVideo(self):
        pass
   
    def getAvaliableVideos(self):
        streaming_dir = next(os.walk('.'))[1].index('streaming')
        file_list = os.listdir(next(os.walk('.'))[1][streaming_dir] + '/videos') # TODO: revisar
        file_list = filter(lambda f: f[-3:] == 'mp4', file_list)
        file_list = list(set([f.split("_")[0] + "   (X)" for f in file_list]))
        menu = self.optionsVideos["menu"]
        menu.delete(0, 'end')

        for filename in sorted(file_list):
            menu.add_command(label=filename, command=lambda: self.confirmExclusion(filename.split()[0]))

    def uploadFile(self):
        cur_dir = os.getcwd()
        file_path = askopenfile(initialdir=cur_dir, mode='r', filetypes=[('Video Files', '*mp4')])
        if file_path and os.path.getsize(file_path.name) <= 8000000:
            # converter vídeos p/ a pasta raiz
            for resolution in [(1280, 720), (640, 480), (360, 240)]:
                fn = r'"{}"'.format(file_path.name.split(os.sep)[-1].split(".")[0])
                print("./streaming/videos/{}.mp4".format(fn.replace("_","") + "_" + str(resolution[1])))
                VideoResizer.convert(file_path.name, "./streaming/videos/{}.mp4".format(fn.replace("_","") + "_" + str(resolution[1]), resolution[1]), resolution)
        else:
            showerror(title="Erro!", message="Arquivo maior do que o limite suportado (8 MB)")
        self.getAvaliableVideos() # refresh videos
    # TODO: add progress bar

    def confirmExclusion(self, filename):
        answer = askyesno('Confirmar Exclusão', 'Deseja remover o vídeo {} do catálogo?'.format(filename))
        print(answer)
        if answer:
            self.removeFile(filename)

    def removeFile(self, filename):
        files = glob('./streaming/videos/{}*'.format(filename))
        for file in files:
            os.remove(file)
        self.getAvaliableVideos()

    def start(self):
        self.window.title("Gerenciar Vídeos")
        self.window.geometry("%dx%d" % (self.width, self.height))    
        self.getAvaliableVideos() # refresh videos
        self.window.mainloop()


if __name__ == "__main__":
    ClientGerenciador()
