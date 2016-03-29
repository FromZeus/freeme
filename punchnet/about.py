import Tkinter
from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import time
from mixer import *


class About:

    ABOUT = dict(
        VERSION = '12',
        AUTHORS = 'TERNSIP, NULL, NYANPEPSI',
        COPYRIGHT = 'No rights left to reserve',
        CONTACT = 'test@gmail.com',
    )
   
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
        self.label = Label(self.title, text=". : A B O U T : .", **theme.LABEL)
        self.label.pack()
        
        # Add text
        self.text = Text(self.panel, **theme.ENRTY)
        self.text.grid(row = 1, column = 0, padx = 0, pady = 0, sticky = W+E+N+S)
        
        # Generate message
        message = '\tP U N C H N E T\n'
        for key, value in About.ABOUT.iteritems():
            message += '\n' + key + ' : ' + value
        self.text.insert(END, message)
        self.text.tag_configure("center", justify = 'center', font = ('Tempus Sans ITC', 12, 'bold'))
        self.text.tag_add("center", 1.0, "end")
        
    # Hide panel
    def hide(self, *args):
        self.panel.pack_forget()
        
    # Show panel
    def show(self, *args):
        self.panel.pack(fill = BOTH, expand = True)
        