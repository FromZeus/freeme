import Tkinter
from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import time
from mixer import *


class Terminal:
   
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
        self.label = Label(self.title, text=". : T E R M I N A L : .", **theme.LABEL)
        self.label.pack()
        
        # Add board
        self.board = ScrolledText(self.panel, **theme.ENRTY)
        self.board.configure(state = DISABLED)
        self.board.grid(row = 1, column = 0, padx = 0, pady = 0, sticky = W+N+E+S)

        # Add Text enrty
        self.editbox = Entry(self.panel, text = '', **theme.ENRTY)
        self.editbox.bind('<Return>', self.submit)
        self.editbox.grid(row = 2, column = 0, padx = 0, pady = 0, sticky = W+N+S+E)
        
        # Add Submit button
        self.submitbtn = Button(self.panel, text = 'Submit', width = 15, command = self.submit, **theme.BUTTON)
        self.submitbtn.grid(row = 2, column = 0, padx = 0, pady = 0, sticky = N+S+E)
        
        # Console command -> (method, description)
        self.commands = {}
        self.register(['help', '?'], self.help, 'Show help')
        self.register(['clr', 'clear'], self.clr, 'Clear console')
        
    # Hide panel
    def hide(self, *args):
        self.panel.pack_forget()
        
    # Show panel
    def show(self, *args):
        self.panel.pack(fill = BOTH, expand = True)
        
    # Register console commands and bind method with description
    def register(self, commands, method, description):
        pack = (method, description)
        for cmd in commands:
            self.commands[cmd.lower()] = pack
        
    # Console commands handler
    def submit(self, event = None):
        Mixer.play('data/send.wav')
        message = self.editbox.get()
        self.editbox.delete(0, END)
        if not message:
            return
        self.execute(None)
        for msg in message.split(';'):
            self.execute(msg)
    
    # Execute command string
    def execute(self, message):
        if not message:
            return
        tokens = message.split()
        if len(tokens) == 0:
            return
        cmd = tokens[0]
        args = tokens[1:]
        time_prefix = lambda : time.strftime("[%Y.%m.%d][%H:%M:%S]")
        out_prefix = lambda : time_prefix() + ' => '
        in_prefix = lambda : time_prefix() + ' <= '
        self.add(out_prefix() + message.replace('\n', '\n' + out_prefix()) + '\n')
        result = 'Unknown command: ' + cmd
        if cmd.lower() in self.commands:
            try:
                result = self.commands[cmd.lower()][0](*args)
            except TypeError as te:
                result = str(te)
        if result:
            self.add(in_prefix() + result.replace('\n', '\n' + in_prefix()) + '\n')
        
    # Returns terminal help
    def help(self, *args):
        cmdnames = {v: k for k, v in self.commands.iteritems()}
        return '\n'.join("{!s} : {!r}".format(value, key[1]) for (key, value) in cmdnames.iteritems())

    # Get console text 
    def get(self):
        return self.board.get('1.0', END+'-1c')
        
    # Set console text
    def set(self, data):
        self.board.configure(state = NORMAL)
        self.board.delete('1.0', END)
        self.board.insert(1.0, data)
        self.board.configure(state = DISABLED)
        
    # Insert text to console index = (row, col) 
    def ins(self, data, index):
        self.board.configure(state = NORMAL)
        self.board.insert(index, data)
        self.board.configure(state = DISABLED)
        
    # Add text to the end
    def add(self, data):
        self.board.configure(state = NORMAL)
        self.board.insert(END, data)
        self.board.configure(state = DISABLED)
       
    # Clear console
    def clr(self):
        self.board.configure(state = NORMAL)
        self.board.delete('1.0', END)
        self.board.configure(state = DISABLED)
        