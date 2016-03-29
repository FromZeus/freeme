import Tkinter
from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import time


class Options:
   
    def __init__(self, root, theme):
    
        # Memorize arguments
        self.root = root
        self.theme = theme
        
        # Create main panel
        self.panel = Frame(self.root, **theme.FRAME)
        self.panel.pack(fill = BOTH, expand = True)
        
        # Configure GUI Grid
        Grid.columnconfigure(self.panel, 0, weight=1)
        Grid.rowconfigure(self.panel, 0, weight=0)
        Grid.rowconfigure(self.panel, 1, weight=1)
        
        # Add title frame
        self.title = Frame(self.panel, height = 50, **theme.FRAME)
        self.title.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = W+E)
        self.label = Label(self.title, text=". : O P T I O N S : .", **theme.LABEL)
        self.label.pack()
        
        
    # Hide panel
    def hide(self, *args):
        self.panel.pack_forget()
        
    # Show panel
    def show(self, *args):
        self.panel.pack(fill = BOTH, expand = True)
        