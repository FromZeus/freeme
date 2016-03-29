import Tkinter
from Tkinter import *
import tkFileDialog
import tkMessageBox
import time
from home import *
from terminal import Terminal
from connections import Connections
from authenticity import Authenticity
from about import About
from theme import Theme
from mixer import Mixer
from conversations import Conversations
from options import Options
from info import Info

class Punchnet:
    
    #return tkFileDialog.askopenfilename(parent = root, title = 'Select a file')
    #return tkFileDialog.asksaveasfilename(parent = root)

    def __init__(self, theme):
    
        # Add functional
        apps = {}
        beep = lambda : Mixer.play('data/click.wav')
        select = lambda name : [[app.hide() for key, app in apps.iteritems()], apps[name].show()]
        exit = lambda : root.destroy()
        hide = lambda : root.iconify()
        
        # Create window
        root = Tkinter.Tk(className = 'Punchnet')
        root.geometry('800x600')
        root.iconbitmap(r'data/icon.ico')
        
        # Add menu tape
        tape = Menu(root, **theme.MENU)
        root.config(menu = tape)

        # Add main sub-menu
        main = Menu(tape, **theme.MENU)
        main.add_command(label = 'Home', command = lambda : [beep(), select('home')])
        main.add_command(label = 'Hide', command = lambda : [beep(), hide()])
        main.add_command(label = 'Exit', command = lambda : [beep(), exit()])
        tape.add_cascade(label = 'Main', menu = main)

        # Add security sub-menu
        scrmenu = Menu(tape, **theme.MENU)
        tape.add_cascade(label = 'Security', menu = scrmenu)
        scrmenu.add_command(label = 'Authenticity', command = lambda : [beep(), select('authenticity')])
        scrmenu.add_command(label = 'Connections', command = lambda : [beep(), select('connections')])
        
        # Add Tools sub-menu
        toolsmenu = Menu(tape, **theme.MENU)
        tape.add_cascade(label='Tools', menu = toolsmenu)
        toolsmenu.add_command(label = 'Terminal', command = lambda : [beep(), select('terminal')])
        toolsmenu.add_command(label = 'Conversations', command = lambda : [beep(), select('conversations')])
        toolsmenu.add_command(label = 'Options', command = lambda : [beep(), select('options')])
        
        # Add help sub-menu
        helpmenu = Menu(tape, **theme.MENU)
        tape.add_cascade(label = 'Help', menu = helpmenu)
        helpmenu.add_command(label = 'Info', command = lambda : [beep(), select('info')])
        helpmenu.add_command(label = 'About', command = lambda : [beep(), select('about')])
        
        # Add applications
        apps['terminal'] = Terminal(root, theme)
        apps['connections'] = Connections(root, theme)
        apps['authenticity'] = Authenticity(root, theme)
        apps['about'] = About(root, theme)
        apps['home'] = Home(root, theme)
        apps['conversations'] = Conversations(root, theme)
        apps['options'] = Options(root, theme)
        apps['info'] = Info(root, theme)
        
        # Register terminal API commands
        apps['terminal'].register(['exit', 'quit'], exit, 'Exit punchnet')
        apps['terminal'].register(['play'], Mixer.play, 'Play <path> sound')
        
        # Select initial window
        select('home')
        
        # Start GUI
        root.mainloop()

        

if __name__ == '__main__':
    punchnet = Punchnet(Theme.Dark)



