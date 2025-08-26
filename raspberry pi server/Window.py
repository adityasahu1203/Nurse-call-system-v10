import tkinter
from tkinter import *
from tkinter import ttk
from functools import partial
from colorama import Fore,Back,Style
from PIL import *
#from PIL import Image
#from PIL import ImageTk
 

import tkinter,time,main

mygreen = "#d2ffd2"
myred = "#dd0202"
window = Tk()
window_width = 1024
window_height = 600
#window_width = 1000
#window_height = 1000
#window = Window.Master(None)
##window.title("Intelligent Nurse Call System")
window.configure(background="gray")
window.geometry("%dx%d+0+0"%(window_width,window_height))
style = ttk.Style()

#canvas=Canvas(window, width = 10, height = 10)
#canvas.pack()

style.theme_create( "mynote", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 7, 2, 0] } },
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": mygreen ,"font":("Helvetica", 40)},
            "map":       {"background": [("selected", myred)],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )

style.theme_use("mynote")
note = ttk.Notebook(window)

window.tab1 = ttk.Frame(note)
window.tab2 = ttk.Frame(note)
window.tab3 = ttk.Frame(note)
window.tab4 = ttk.Frame(note)
window.tab5 = ttk.Frame(note)

note.add(window.tab1, text = "Home ")
note.add(window.tab2, text = "Disconnected ")
#note.add(window.tab3, text = "Alarm ")
#note.add(window.tab4, text = "")
note.add(window.tab5, text = "Settings ")
note.pack()

disconncet_tracker=[]
label_width = 29
type_label_width = 17
type_text_size = 14
text_size = 37
my_tickers = StringVar()
walker_tickers = StringVar()
my_clock = StringVar()
my_date = StringVar()
my_clock.set("00:00")
my_date.set("00/00/0000")
my_tickers.set("Wellcome to Nurse Call System")



try:
    labeltickers=Label(window.tab1,textvariable=my_tickers,height=1,\
                       width=25,fg="white",bg="purple",\
                       font=("Helvetica", 25))   
    labeltickers.grid(column=0,columnspan=4,row=0,sticky='NSEW')
    
    clock =Label(window.tab1,textvariable = my_clock,height=1,\
                 width=5,fg="black",bg="pale green",font=("Sans", 25,"bold"))
    clock.grid(column=0,columnspan=2,row=0,sticky='SW')

    date =Label(window.tab1,textvariable = my_date,height=1,\
                 width=13,fg="black",bg="spring green",font=("Sans",10,"bold"))
    date.grid(column=0,columnspan=2,row=1,sticky='SW')
    
    clock.grid(row=7,column=0,sticky = "nw",)
    date.grid(row=8,column=0,sticky = "nw",)
    
    '''labeltickers=Label(window.tab1,textvariable=walker_tickers,height=1,\
                       width=25,fg="white",bg="grey",\
                       font=("Helvetica", 20))   
    labeltickers.grid(column=0,columnspan=4,row=8,sticky='NSEW')'''
    
    labelwalker=Label(window.tab1,text="MANMIND - Intelligent Nurse Call Monitoring System      ",height=2,\
                       width=25,fg="white",bg="grey",\
                       font=("Helvetica", 28))   
    labelwalker.grid(column=0,columnspan=4,row=9,sticky='NSEW')
    
    '''labelgap=Label(window.tab1,text="             ",height=1,\
                       width=25,fg="white",bg="grey",\
                       font=("Helvetica", 28))   
    labelgap.grid(column=1,columnspan=1,row=7,sticky='NW')'''
    
    #canvas.grid(row=0, column=2,columnspan=2)
    
##            clock =Label(self.tab1,textvariable = self.my_clock,height=1,\
##                         width=5,fg="black",bg="white",font=("Sans", 32,"bold"))
##            
##            clock.grid(column=0,row=0,sticky='SW')
##
    discon_label = Label(window.tab2,text = " Disconnected Devices",height=1,\
                       width=60,fg="Black",bg="red",\
                       font=("Helvetica", 30,'bold'))
    discon_label.grid(row = 2,column = 0,columnspan = 2,sticky='NSEW')
    
    discon_box = Listbox(window.tab2, width=41, height=15,fg="red4",\
                              bg="gray65",font=('Sans','20','bold'))
    
    discon_box.grid(row = 3,column = 0,columnspan = 2,\
                         rowspan=7,sticky='NSEW')
    scroll = Scrollbar(window.tab2,command=discon_box.yview,orient=tkinter.VERTICAL)
    scroll.grid(row=3,column=3,rowspan=7,sticky=tkinter.N+tkinter.S+tkinter.E)
    discon_box.configure (yscrollcommand=scroll.set)
    
    alarm_box = Listbox(window.tab3, width=29, height=5,fg="red4",\
                              bg="gray65",font=('Sans','30','bold'))
    
    alarm_box.grid(row = 1,column = 0,columnspan = 6,\
                         rowspan=1,sticky='NSEW')
    close_alarm = ttk.Button(window.tab3,style = "AlarmClose.TButton",\
                               command = main.alarmClose)

    next_button = ttk.Button(window.tab1,style = "next_disable.TButton",\
                               command = main.nextPage)
    previous_button = ttk.Button(window.tab1,style = "previous_disable.TButton",\
                               command = main.previousPage)
    
    logo1 = ttk.Button(window.tab1,style = "logo.TButton")

    button_1 = ttk.Button(window.tab1,style = "N.TButton",\
                               command = partial(main.ackCall,1))
    button_2 = ttk.Button(window.tab1,style = "N.TButton",\
                               command = partial(main.ackCall,2))
    button_3 = ttk.Button(window.tab1,style = "N.TButton",\
                               command = partial(main.ackCall,3))
    button_4 = ttk.Button(window.tab1,style = "N.TButton",\
                               command = partial(main.ackCall,4))
    button_5 = ttk.Button(window.tab1,style = "N.TButton",\
                               command = partial(main.ackCall,5))
##    button_6 = ttk.Button(window.tab1,style = "N.TButton",\
##                               command = partial(main.ackCall,6))
##    button_7 = ttk.Button(window.tab1,style = "N.TButton",\
##                               command = partial(main.ackCall,7))

    button_call = ttk.Button(window.tab4,style = "N.TButton",\
                               command = main.callPickup)
    button_alarm_1 = ttk.Button(window.tab4,style = "AlarmDisable.TButton",\
                                command = partial(main.alarmManage,1))
    button_alarm_2 = ttk.Button(window.tab4,style = "AlarmDisable.TButton",\
                                command = partial(main.alarmManage,2))
    button_alarm_3 = ttk.Button(window.tab4,style = "AlarmDisable.TButton",\
                                command = partial(main.alarmManage,3))
    

    label_1 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
    label_2 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
    label_3 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
    label_4 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
    label_5 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
##    label_6 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)
##    label_7 = ttk.Label(window.tab1,style = "N.TLabel",width = label_width)

    label_call_1 = ttk.Label(window.tab4,style = "N.TLabel",width = 15)
    label_call_2 = ttk.Label(window.tab4,style = "N.TLabel",width = 15)
    label_alarm_1 = ttk.Label(window.tab4,text = " Alarm 5-Min")
    label_alarm_2 = ttk.Label(window.tab4,text = " Alarm 10-Min")
    label_alarm_3 = ttk.Label(window.tab4,text = " Alarm 15-Min")
    

    label_11 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
    label_12 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
    label_13 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
    label_14 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
    label_15 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
##    label_16 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
##    label_17 = ttk.Label(window.tab1,style = "NT.TLabel",width = type_label_width)
            

    button_1.grid(row=1,column=0,sticky = "nsew")
    button_2.grid(row=2,column=0,sticky = "nsew")
    button_3.grid(row=3,column=0,sticky = "nsew")
    button_4.grid(row=4,column=0,sticky = "nsew")
    button_5.grid(row=5,column=0,sticky = "nsew")
##    button_6.grid(row=6,column=0,sticky = "nsew")
##    button_7.grid(row=7,column=0,sticky = "nsew")

    button_call.grid(row=2,rowspan=9,column=1,sticky = "nsew")
    button_alarm_1.grid(row=2,column=5,sticky = "nsew")
    button_alarm_2.grid(row=2,column=6,sticky = "nsew")
    button_alarm_3.grid(row=2,column=7,sticky = "nsew")
    close_alarm.grid(row=2,column=1,sticky = "nsew")


    label_1.grid(row=1,column=1,sticky = "nsew",pady=1)
    label_2.grid(row=2,column=1,sticky = "nsew",pady=1)
    label_3.grid(row=3,column=1,sticky = "nsew",pady=1)
    label_4.grid(row=4,column=1,sticky = "nsew",pady=1)
    label_5.grid(row=5,column=1,sticky = "nsew",pady=1)
 ##   label_6.grid(row=6,column=1,sticky = "nsew",pady=1)
##    label_7.grid(row=7,column=1,sticky = "nsew",pady=1)

    label_call_1.grid(row=0,column=0,columnspan = 4,sticky = "nsew",pady=1)
    label_call_2.grid(row=1,column=0,columnspan = 4,sticky = "nsew",pady=20)
    label_alarm_1.grid(row=3,column=5,sticky = "nsew",pady=3)
    label_alarm_2.grid(row=3,column=6,sticky = "nsew",pady=3)
    label_alarm_3.grid(row=3,column=7,sticky = "nsew",pady=3)


    label_11.grid(row=1,column=2,sticky = "nsew",pady=1)
    label_12.grid(row=2,column=2,sticky = "nsew",pady=1)
    label_13.grid(row=3,column=2,sticky = "nsew",pady=1)
    label_14.grid(row=4,column=2,sticky = "nsew",pady=1)
    label_15.grid(row=5,column=2,sticky = "nsew",pady=1)
##    label_16.grid(row=6,column=2,sticky = "nsew",pady=1)
##    label_17.grid(row=7,column=2,sticky = "nsew",pady=1)

        
    next_button.grid(row=6,column=2,rowspan=7,sticky = "new",pady=0)
    previous_button.grid(row=6,column=1,rowspan=7,sticky = "ne",pady=0)
    logo1.grid(row=0,column=2,rowspan=7,sticky = "nw",pady=0)



    ## setup of setting page
    vol_label = Label(window.tab5,text = " Volume",height=1,\
                       width=10,fg="black",bg="white",\
                       font=("Helvetica", 10,'bold'))
    vol_label.grid(row = 12,column = 9,columnspan = 3, padx=15, pady=5, sticky='NSEW')

    volumeController = Scale(window.tab5,from_=100,to=0,orient = VERTICAL,\
                             command = main.set_vol)
    volumeController.set(main.alsa_mixer.getvolume())
    volumeController.grid(row = 1, column = 10, rowspan=11, sticky='NSEW')

    bed_label_1 = Label(window.tab5,text = " Old Room No",height=1,\
                       width=12,fg="black",bg="pale green",padx=30,\
                       font=("Helvetica", 15,'bold'))
    bed_label_1.grid(row=1, column=0, pady=2,columnspan=3, sticky='NSEW')

    bed_entry_1 = Entry(window.tab5,bd=2,width = 10)
    bed_entry_1.grid(row = 1, column = 3, pady=2,columnspan=2,sticky='NSEW')

    bed_label_2 = Label(window.tab5,text = " Old Bed No",height=1,\
                       width=12,fg="black",bg="pale green",padx=30,\
                       font=("Helvetica", 15,'bold'))
    bed_label_2.grid(row = 2,column = 0, pady=2,columnspan=3, sticky='NSEW')

    bed_entry_2 = Entry(window.tab5,bd=2,width = 10)
    bed_entry_2.grid(row = 2,column = 3, pady=2,columnspan=2, sticky='NSEW')

    bed_label_3 = Label(window.tab5,text = " New Room No",height=1,\
                       width=12,fg="black",bg="tan1",padx=30,\
                       font=("Helvetica", 15,'bold'))
    bed_label_3.grid(row = 3,column = 0, pady=2,columnspan=3, sticky='NSEW')

    bed_entry_3 = Entry(window.tab5,bd=2,width = 10)
    bed_entry_3.grid(row = 3,column = 3, pady=2,columnspan=2, sticky='NSEW')

    bed_label_4 = Label(window.tab5,text = " New Bed No",height=1,\
                       width=12,fg="black",bg="tan1",padx=30,\
                       font=("Helvetica", 15,'bold'))
    bed_label_4.grid(row = 4,column = 0, pady=2,columnspan=3, sticky='NSEW')

    

    bed_entry_4 = Entry(window.tab5,bd=2,width = 10)
    bed_entry_4.grid(row = 4,column = 3, pady=2,columnspan=2, sticky='NSEW')

    bedType = StringVar(window)
    bedType.set('Bed')
    choices = {'Room','Bed','Toilet'}
    popupMenu = OptionMenu(window.tab5,bedType, *choices)
    popupMenu.grid(row=3, column=5, pady=5, sticky='NSEW')

    rbUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
                               command = main.updateRoomBed)
    rbUpdate.grid(row=4, column=5, padx=2, sticky='NSEW')

    hos_label = Label(window.tab5,text = " Hospital Name ",height=1,\
                       width=12,fg="black",bg="pale green",padx=30,\
                       font=("Helvetica", 15,'bold'))
    hos_label.grid(row = 9,column = 0, pady=2, columnspan=3, sticky='NSEW')

    hos_entry = Entry(window.tab5,bd=2,width = 10)
    hos_entry.grid(row = 9,column = 3, pady=2, padx=3, columnspan=2, sticky='NSEW')

    hosUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
                               command = main.updateHospitalName)
    hosUpdate.grid(row=9, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')

    ward_label = Label(window.tab5,text = " Ward Name ",height=1,\
                       width=12,fg="black",bg="pale green",padx=30,\
                       font=("Helvetica", 15,'bold'))
    ward_label.grid(row = 8,column = 0, pady=2, columnspan=3, sticky='NSEW')

    ward_entry = Entry(window.tab5,bd=2,width = 10)
    ward_entry.grid(row = 8,column = 3, pady=2, padx=3, columnspan=2, sticky='NSEW')

    wardUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
                               command = main.updateWardName)
    wardUpdate.grid(row=8, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')

    gap = Label(window.tab5,text = " ",height=1,\
                       width=12,fg="black",padx=30,\
                       font=("Helvetica", 15,'bold'))
    gap.grid(row = 10,column = 0, pady=60, columnspan=3, sticky='NSEW')
##    baud_label = Label(window.tab5,text = " Baudrate ",height=1,\
##                       width=12,fg="black",bg="pale green",padx=30,\
##                       font=("Helvetica", 15,'bold'))
##    baud_label.grid(row = 7,column = 0, pady=2, columnspan=3, sticky='NSEW')
##
##    baud = StringVar(window)
##    baud.set('9600')
##    baudChoices = {'2400','4800','9600','10417','14400','19200','38400','57600','115200','128000','256000'}
##    baudMenu = OptionMenu(window.tab5, baud, *baudChoices)
##    baudMenu.grid(row = 7,column = 3, pady=2, padx=3, columnspan=1, sticky='NSEW')
##
##    baudUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
##                               command = main.updateBaudrate)
##    baudUpdate.grid(row=7, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')
##
##    localip_label = Label(window.tab5,text = " Local ip ",height=1,\
##                       width=12,fg="black",bg="pale green",padx=30,\
##                       font=("Helvetica", 15,'bold'))
##    localip_label.grid(row = 10,column = 0, pady=2, columnspan=3, sticky='NSEW')
##
##    localip_entry = Entry(window.tab5,bd=2,width = 10)
##    localip_entry.grid(row = 10,column = 3, pady=2, padx=3, columnspan=2, sticky='NSEW')
##
##    localipUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
##                               command = main.updateLocalip)
##    localipUpdate.grid(row=10, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')
##
##    centralip_label = Label(window.tab5,text = " Central server ip ",height=1,\
##                       width=12,fg="black",bg="pale green",padx=30,\
##                       font=("Helvetica", 15,'bold'))
##    centralip_label.grid(row = 11,column = 0, pady=2, columnspan=3, sticky='NSEW')
##
##    centralip_entry = Entry(window.tab5,bd=2,width = 10)
##    centralip_entry.grid(row = 11,column = 3, pady=2, padx=3, columnspan=2, sticky='NSEW')
##
##    centralipUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
##                               command = main.updateCentralip)
##    centralipUpdate.grid(row=11, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')
##
##    maxbed_label = Label(window.tab5,text = " Total Bed No ",height=1,\
##                       width=12,fg="black",bg="pale green",padx=30,\
##                       font=("Helvetica", 15,'bold'))
##    maxbed_label.grid(row = 12,column = 0, pady=2, columnspan=3, sticky='NSEW')
##
##    maxbed_entry = Entry(window.tab5,bd=2,width = 10)
##    maxbed_entry.grid(row = 12,column = 3, pady=2, padx=3, columnspan=2, sticky='NSEW')
##
##    maxbedUpdate=ttk.Button(window.tab5, text="Update", style = "Update.TButton",\
##                               command = main.updateMaxbed)
##    maxbedUpdate.grid(row=12, column=5, columnspan=3, pady=2, padx=3, sticky='NSEW')



except Exception as e:
    print (Fore.RED +"")
    print (e)
    print (Fore.CYAN+"Initialization Error")

nextPage_enable = PhotoImage(file="/home/pi/image/next_enable.gif")
nextPage_disable = PhotoImage(file="/home/pi/image/next_disable.gif")
previousPage_enable = PhotoImage(file="/home/pi/image/previous_enable.gif")
previousPage_disable = PhotoImage(file="/home/pi/image/previous_disable.gif")
    
none=PhotoImage(file="/home/pi/image/none.gif")
nack=PhotoImage(file="/home/pi/image/n.ack.gif")
eack=PhotoImage(file="/home/pi/image/e.ack.gif")
cack=PhotoImage(file="/home/pi/image/c.ack.gif")
psack=PhotoImage(file="/home/pi/image/ps.ack.gif")
rack=PhotoImage(file="/home/pi/image/r.ack.gif")
disable=PhotoImage(file="/home/pi/image/d.ack.gif")
logobtn=PhotoImage(file="/home/pi/image/logo.gif")
#ack = self.ack.subsample(1,1)
ns_call=PhotoImage(file="/home/pi/image/ns_call.gif")
ns_cancel=PhotoImage(file="/home/pi/image/ns_cancel.gif")
doc_call=PhotoImage(file="/home/pi/image/doc_call.gif")
doc_cancel=PhotoImage(file="/home/pi/image/doc_cancel.gif")
speaker=PhotoImage(file="/home/pi/image/speaker.gif")
alarm_disable = PhotoImage(file="/home/pi/image/alarm_disable.gif")
alarm_enable = PhotoImage(file="/home/pi/image/alarm_enable.gif")
alarm_close = PhotoImage(file="/home/pi/image/alarm_close.gif")

style.configure("Update.TButton",
                foreground = "black",
                background = "white",
                paddind=6,
                width=12,
                anchor=CENTER,
                relief = "RIDGE")
style.configure("N.TButton",
                foreground = "black",
                background = "gray65",
                relief = "RIDGE",
                image = none)

style.configure("Normal.TButton",
                background = "white",
                relief = "RIDGE",
                image = nack)

style.configure("Emergency.TButton",
                background = "white",
                relief = "RIDGE",
                image = eack)

style.configure("Blue.TButton",
                background = "white",
                relief = "RIDGE",
                image = cack)

style.configure("Presence.TButton",
                background = "white",
                relief = "RIDGE",
                image = psack)

style.configure("Remote.TButton",
                background = "white",
                relief = "RIDGE",
                image = rack)

style.configure("NS_Call.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = ns_call)

style.configure("NS_Cancel.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = ns_cancel)
style.configure("DOC_Call.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = doc_call)

style.configure("DOC_Cancel.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = doc_cancel)

style.configure("Disable.TButton",
                background = "white",
                relief = "RIDGE",
                image = disable)

        
style.configure("AlarmDisable.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = alarm_disable)
style.configure("AlarmEnable.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = alarm_enable)
style.configure("AlarmClose.TButton",
                background = "white",
                relief = "RIDGE",
                bd= 10,
                image = alarm_close)
style.configure("Speaker.TButton",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,
                image = speaker)
style.configure("next_disable.TButton",
                background = "light gray",
                relief = "RIDGE",
                bd= 0,
                image = nextPage_disable)
style.configure("logo.TButton",
                background = "purple",
                relief = "RIDGE",
                bd= 10,
                image = logobtn)
style.configure("next_enable.TButton",
                background = "light gray",
                relief = "RIDGE",
                bd= 0,
                image = nextPage_enable)
style.configure("previous_disable.TButton",
                background = "light gray",
                relief = "RIDGE",
                bd= 0,
                image = previousPage_disable)
style.configure("previous_enable.TButton",
                background = "light gray",
                relief = "RIDGE",
                bd= 0,
                image = previousPage_enable)

style.configure("N.TLabel",
                foreground = "black",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("NT.TLabel",
                foreground = "black",
                background = "gray65",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

style.configure("Normal.TLabel",
                foreground = "black",
                background = "green",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("TNormal.TLabel",
                foreground = "black",
                background = "green",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

style.configure("Emergency.TLabel",
                foreground = "yellow",
                background = "red",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("TEmergency.TLabel",
                foreground = "yellow",
                background = "red",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

style.configure("CodeBlue.TLabel",
                foreground = "white",
                background = "blue",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("TCodeBlue.TLabel",
                foreground = "white",
                background = "blue",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

style.configure("Presence.TLabel",
                foreground = "white",
                background = "yellow2",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("TPresence.TLabel",
                foreground = "white",
                background = "yellow2",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

style.configure("Remote.TLabel",
                foreground = "white",
                background = "gray",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',text_size,'bold'))
style.configure("TRemote.TLabel",
                foreground = "white",
                background = "gray",
                relief = "RIDGE",
                bd= 10,                        
                font = ('Helvetica',type_text_size,'bold'))

'''img=ImageTk.PhotoImage(Image.open("/home/pi/image/logo.jpg"))
self.logo = tkinter.Label(self, image = img)
self.logo.image = img
self.logo.grid(column=0,row=0,sticky='NW') '''          


window.grid()   
window.grid_columnconfigure(0,weight=1)
window.grid_columnconfigure(1,weight=1)
window.grid_columnconfigure(2,weight=1)
window.grid_columnconfigure(3,weight=1)
window.grid_columnconfigure(4,weight=1)
window.grid_rowconfigure(0,weight=1)
window.grid_rowconfigure(1,weight=1)
window.grid_rowconfigure(2,weight=1)
window.grid_rowconfigure(3,weight=1)
window.grid_rowconfigure(4,weight=1)
window.grid_rowconfigure(5,weight=1)
window.grid_rowconfigure(6,weight=1)
#window.grid_rowconfigure(7,weight=1)
#window.grid_rowconfigure(8,weight=1)
#window.grid_rowconfigure(9,weight=1)
##window.grid_rowconfigure(10,weight=1)
##window.grid_rowconfigure(11,weight=1)
##

#window.config(cursor="none")
window.mainloop()
