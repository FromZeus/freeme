class Theme:
    
    class Dark:
        
        ENRTY = dict(
            insertwidth = 1,
            selectborderwidth = 0,
            selectbackground = "#0099FF",
            font = "Helvetica 9 bold",
            bg = "#000000",
            fg = "#FFFFFF",
            insertbackground = "#FFFFFF",
            borderwidth = 2, 
            state = 'normal',
            relief = 'ridge',
        )
        
        BUTTON = dict(
            font = "Helvetica 10",
            bg = "#000000",
            fg = "#FFFFFF",
            borderwidth = 2, 
            state = 'normal',
            relief = 'ridge',
        )
        
        MENU = dict(
            tearoff = 0,
            font = "Helvetica 10",
            bg = "#000000",
            fg = "#FFFFFF",
            borderwidth = 2, 
            relief = 'ridge',
            activebackground='#004c99', 
            activeforeground='white'
        )
        
        FRAME = dict(
            bg = "#000000",
            borderwidth = 2, 
            relief = 'ridge',
        )
        
        LABEL = dict(
            font = "Helvetica 9 bold",
            bg = "#000000",
            fg = "#FFFFFF",
            borderwidth = 0, 
            state = 'normal',
            relief = 'ridge',
        )