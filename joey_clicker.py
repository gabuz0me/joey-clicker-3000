#! /usr/bin/python
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from pynput.mouse import Controller, Button
from pynput import keyboard

verbose = False

class Clicker(Thread):
    def __init__(self, master, period):
        Thread.__init__(self)
        self.period = period
        self.master = master
        self.start()

    def run(self):
        mouse = Controller()
        # doubleclick won't trigger and additional click
        time.sleep(self.period)
        while self.master.isRunning:
            mouse.click(Button.left)
            self.master.clickCounter += 1
            if verbose: print("Click")
            time.sleep(self.period)
    

class KeyboardListener(Thread):
    def __init__(self, master, shortcut):
        Thread.__init__(self)
        self.shortcut = shortcut
        self.master = master
        self.start()

    def on_press(self):
        self.master.switchState()
    
    def run(self):
        with keyboard.GlobalHotKeys({self.shortcut:self.on_press}) \
        as self.listener:
            self.listener.join()

    def stop(self):
        self.listener.stop()


class JoeyClicker3000(tk.Tk):
    def __init__(self, cpm = 60, shortcut = "<ctrl>+<shift>+j", **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.name = "Joey Clicker 3000"
        self.isRunning = False
        self.shortcut = shortcut
        self._clickCounter = 0

        self.title(self.name)
        mainFrame=tk.Frame(self)
        mainFrame.pack()
        tk.Label(mainFrame, text=self.name, font=("default", 25)).pack()

        cpmFrame=tk.Frame(mainFrame)
        cpmFrame.pack()
        tk.Label(cpmFrame, text="Clicks Per Minute (CPM):").pack(side='left')
        vcmd = (self.register(self.isEntryValid), '%P')
        self.cpmEntry = tk.Entry(cpmFrame, validate='key', validatecommand=vcmd)
        self.cpmEntry.pack(side='right')
        self.cpm = cpm
        self.button = tk.Button(mainFrame, command=lambda:self.switchState())
        self.button.pack()

        tk.Label(mainFrame, text=f"(or press \"{shortcut}\" to start/stop)", font=("default", 8)).pack()
        self.clickLabel = tk.Label(mainFrame)
        self.clickLabel.pack()

        self.resizable(False, False)

        self.updateButtonStyle()
        self.updateClickLabel()

        self.listener = KeyboardListener(self, shortcut)
        self.protocol("WM_DELETE_WINDOW", lambda:self.onExit())

    def isEntryValid(self, P):
        return not P or P.isdigit() # and int(P) > 0

    @property
    def clickPeriod(self) -> float:
        """Seconds"""
        return 60 / self.cpm

    @property
    def cpm(self) -> int:
        return int(self.cpmEntry.get())

    @cpm.setter
    def cpm(self, cpm:int):
        self.cpmEntry.delete(0, tk.END)
        self.cpmEntry.insert(0, cpm)

    @property
    def clickCounter(self) -> int:
        return self._clickCounter

    @clickCounter.setter
    def clickCounter(self, value):
        self._clickCounter = value
        self.updateClickLabel()

    def switchState(self):
        try:
            cp = self.clickPeriod
        except:
            messagebox.showerror(self.name, "Invalid CPM")
            return

        if self.isRunning:
            if verbose: print("Stop")
            self.cpmEntry.configure(state='normal')
            self.isRunning = False
        else:
            if verbose: print("Start")
            self.cpmEntry.configure(state='disabled')
            self.isRunning = True
            self.clickCounter = 0
            Clicker(self, cp)
        self.updateButtonStyle()

    def updateButtonStyle(self):
        if self.isRunning:
            self.button.config(text="Stop", fg='red')
        else:
            self.button.config(text="Start", fg='green')

    def updateClickLabel(self):
        v = self._clickCounter
        self.clickLabel.config(text=f"{v} click{'' if v<=1 else 's'} so far !", font=("default", 12))

    def onExit(self):
        self.listener.stop()
        self.destroy()


if __name__ == '__main__':
    jc = JoeyClicker3000()
    jc.mainloop()