from tkinter import *


def data():
    j = 0
    col = 0
    for i in range(30):
        day_area = LabelFrame(frame, text=i + 1, width=150, height=150)
        day_area.grid(row=j, column=col, padx=2, pady=2)
        col += 1
        if (i + 1) % 7 == 0:
            col = 0
            j += 1
        # Label(frame, text=i).grid(row=i, column=0)
        # Label(frame, text="my text" + str(i)).grid(row=i, column=1)
        # Label(frame, text="..........").grid(row=i, column=2)


def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"), width=400, height=400)


if __name__ == "__main__":
    root = Tk()
    sizex = 800
    sizey = 600
    posx = 100
    posy = 100
    # root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))

    # frame1 = LabelFrame(root, text=" Schedule ", width=1050, height=850)
    # frame1.grid(row=0, column=0, padx=10, pady=10)
    # frame1.pack(expand=True, padx=20, pady=20, fill='both')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    # frame.rowconfigure(0, weight=1)
    # frame.columnconfigure(3, weight=1)

    myframe = Frame(root, relief=GROOVE, width=50, height=100, bd=1)
    # myframe.place(x=10, y=10)
    # myframe.pack(fill=BOTH, expand=YES)
    myframe.grid(row=0, column=1, padx=10, pady=10)

    canvas = Canvas(myframe)
    frame = Frame(canvas)
    frame.grid(row=0, column=0)
    frame.rowconfigure(1, weight=1)
    myscrollbar = Scrollbar(myframe, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)

    myscrollbar.pack(side="right", fill="y")
    canvas.pack(fill=BOTH, expand=YES)
    canvas.create_window((0, 0), window=frame, anchor='nw')
    frame.bind("<Configure>", myfunction)
    canvas.addtag_all("all")
    data()
    root.mainloop()
