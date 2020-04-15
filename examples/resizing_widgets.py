import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("ariel", 20)  # dont know what you had here


class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)  # this needed to be added
        self.grid_columnconfigure(0, weight=1)  # as did this

        main_container = tk.Frame(self)
        main_container.grid(column=0, row=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        menu_bar = tk.Menu(main_container)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save settings", command=lambda: popupmsg("Not supported yet!"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        tk.Tk.config(self, menu=menu_bar)

        self.frames = {}

        for fr in (MainPage,):
            frame = fr(main_container, self)
            self.frames[fr] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)

    def show_frame(self, pointer):
        frame = self.frames[pointer]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # uncommented these lines
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        label = tk.Label(self, text="Main Page", font=LARGE_FONT)
        label.grid(row=0, padx=10, pady=10)

        button1 = ttk.Button(self, text="Graphs", command=lambda: controller.show_frame(GraphsPage))
        button1.grid(row=1, sticky='nswe')

        button2 = ttk.Button(self, text="Page 2", command=lambda: controller.show_frame(Page2))
        button2.grid(row=2, sticky='nswe')

        button3 = ttk.Button(self, text="Exit", command=quit)
        button3.grid(row=3, sticky='nswe')


app = Main()
app.geometry("1280x720")
app.mainloop()
