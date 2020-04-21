import tkinter as tk

from view.database import DatabaseFrame
from view.home import HomeFrame
from view.schedule import ScheduleFrame


class CreateRoot(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frame = None

        self.switch_frame(ScheduleFrame)

    def switch_frame(self, frame_class):
        if self._frame is not None:
            self._frame.destroy()

        new_frame = frame_class(self)

        self._frame = new_frame
        self._frame.pack(expand=True, fill='both')

        if frame_class == HomeFrame:
            self._frame.winfo_toplevel().geometry('900x500')
        elif frame_class == ScheduleFrame:
            self._frame.winfo_toplevel().geometry('')
        elif frame_class == DatabaseFrame:
            self._frame.winfo_toplevel().geometry('')


if __name__ == '__main__':
    CreateRoot().mainloop()
