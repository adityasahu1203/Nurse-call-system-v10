##****************************************************************************##
##  This code will control the flow of works of incms-R8 version
##  Project Name: incms-R8
##  Author:       Anup Sarkar
##  Date:         14/03/2019
##  Target Area:  Hospitals
##****************************************************************************##

import RPi.GPIO as GPIO
import threading,time,serial,os,dataWarehouse,tkinter,subprocess,\
       pygame,alsaaudio
import Window as window

from colorama import Fore,Back,Style
from tkinter import messagebox
from datetime import datetime
from PIL import *
#from PIL import Image
#from PIL import ImageTK

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
buzerpin,callpin,REpin,statuspin,TalkRelay,ready_pin = 10,18,23,22,17,25
GPIO.setup(ready_pin, GPIO.OUT)
GPIO.setup(buzerpin, GPIO.OUT)
GPIO.setup(callpin, GPIO.OUT)
GPIO.setup(REpin, GPIO.OUT)
GPIO.setup(TalkRelay, GPIO.OUT)
GPIO.setup(statuspin, GPIO.OUT)
GPIO.output(ready_pin, True)
GPIO.output(buzerpin, False)
GPIO.output(callpin, False)
GPIO.output(statuspin, False)
GPIO.output(TalkRelay, False)


##****************************************************************************##
##            Window Parameter Setting
##****************************************************************************##

window_width = 1024
window_height = 600

#window = Window.Master(None)
##window.title("Intelligent Nurse Call System")
##window.configure(background="gray65")
##window.geometry("%dx%d+0+0"%(window_width,window_height))

#comPort = "/dev/tty1"
#comPort = "/dev/ttyS0"
comPort = "/dev/ttyAMA0"
timeOut = .1#0.03

alsa_mixer = alsaaudio.Mixer('PCM')
#window.volumeController.set(alsa_mixer.getvolume())

##****************************************************************************##
##           Message pattern setting
##****************************************************************************##

Withdraw = 'W'
normalCall = 'S'
emergencyCall = 'E'
codeBlueCall = 'B'
presenceCall = 'P' #dev/8/21
remoteCall = 'N'
Broadcast = chr(0)
Response = chr(127)
dataAck = chr(126)
dataNAck = chr(125)
callAck = chr(124)
Dial = chr(123)
Engage = chr(122)
talkPermission = chr(121)
talkFinish = chr(120)

info_table=[]
disconncet_tracker=[]
disconUpdateTime = 20
sep = '\0'
terminatingCharacter = '\r'

pageIndex = 0
pageLength = 5
run = True
secondary_comm = permission = roomcontroller = ward = delay = \
                 announcement_timer = False
talkAddress = talkOnProcess  = timer_time = alarmNotification = call_picked_up=False

def doNothing():
    pass


##****************************************************************************##
##  get_pid method collects all the running program id of the input name
##  I/P: Name of the program
##  O/P: Live ID of all the program of the selected input
##****************************************************************************##

def get_pid(name):
    return subprocess.check_output(["pidof",name])

##****************************************************************************##
##  sounnd calibration
##  I/P: volume
##  O/P: None
##****************************************************************************##
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

##****************************************************************************##
##  set_vol methon changes the volune of the speaker
##  I/P: volume
##  O/P: None
##****************************************************************************##

def set_vol(val):
    #print("check")
    #print(type(val))
    audioVol = _map(int(val), 0, 100, 60, 100)
    alsa_mixer.setvolume(int(audioVol))
    #print("val")
    #print(val)
    #print("audioVol")
    #print(audioVol)

##****************************************************************************##
##  nextPage method changes the page number for the display
##  I/P: None
##  O/P: None
##****************************************************************************##

def nextPage():
    global pageIndex,pageLength
    
    if (len(info_table)-pageIndex) > pageLength:
        pageIndex = pageIndex + pageLength
        window.window.after(0,updateDisplay)

##****************************************************************************##
##  prieviousPage method changes the page number for the display
##  I/P: None
##  O/P: None
##****************************************************************************##
def previousPage():
    global pageIndex,pageLength

    if pageIndex >= pageLength:
        pageIndex = pageIndex - pageLength
        window.window.after(0,updateDisplay)


##****************************************************************************##
##  updateRoomBed method changes the Room and Bed number in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateRoomBed():
    status=dataWarehouse.update_roombedName(window.bed_entry_1.get(),
                                            window.bed_entry_2.get(),
                                            window.bed_entry_3.get(),
                                            window.bed_entry_4.get(),
                                            window.bedType.get())
    if status=="No Match":
        messagebox.showerror("Update Status","Invalid Room Bed Number Entered")
        window.bed_entry_1.delete(0,20)
        window.bed_entry_2.delete(0,20)
        window.bed_entry_3.delete(0,20)
        window.bed_entry_4.delete(0,20)
        window.bedType.set("bed")
    elif status:
        messagebox.showinfo("Update Status","Update Room Bed info Succesfully")
        window.bed_entry_1.delete(0,20)
        window.bed_entry_2.delete(0,20)
        window.bed_entry_3.delete(0,20)
        window.bed_entry_4.delete(0,20)
        window.bedType.set("bed")
    else:
        messagebox.showerror("Update Status","Could not Update Room Bed info")
        window.bed_entry_1.delete(0,20)
        window.bed_entry_2.delete(0,20)
        window.bed_entry_3.delete(0,20)
        window.bed_entry_4.delete(0,20)
        window.bedType.set("bed")

##****************************************************************************##
##  updateHospitalName method changes the Hospital Name in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateHospitalName():
    status=dataWarehouse.update_syatemdetails("HOSPITAL_NAME",window.hos_entry.get())
    if status:
        messagebox.showinfo("Update Status","Update Hostital Name Succesfully")
        window.hos_entry.insert=(0,window.hos_entry.get())
    else:
        messagebox.showerror("Update Status","Could not Update Hospital Name")
        window.hos_entry.insert=(0,dataWarehouse.get_value("HOSPITAL_NAME","SYSTEMDETAILS"))

        
##****************************************************************************##
##  updateWardName method changes the Ward Name in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateWardName():
    status=dataWarehouse.update_syatemdetails("WARD",window.ward_entry.get())
    if status:
        messagebox.showinfo("Update Status","Update Ward Succesfully")
        window.ward_entry.insert=(0,window.ward_entry.get())
    else:
        messagebox.showerror("Update Status","Could not Update Ward")
        window.ward_entry.insert=(0,dataWarehouse.get_value("WARD","SYSTEMDETAILS"))

##****************************************************************************##
##  updateBaudrate method changes the Baudrate in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
##def updateBaudrate():
##    status=dataWarehouse.update_syatemdetails("BAUDRATE",window.baud.get())
##    if status:
##        messagebox.showinfo("Update Status","Update Baudrate Succesfully")
##        window.baud.set=window.baud.get()
##    else:
##        messagebox.showerror("Update Status","Could not Update Baudrate")
##        window.baud.set=dataWarehouse.get_value("BAUDRATE","SYSTEMDETAILS")

##****************************************************************************##
##  updateLocalip method changes the Local ip address in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateLocalip():
    status=dataWarehouse.update_syatemdetails("LOCALIP",window.localip_entry.get())
    if status:
        messagebox.showinfo("Update Status","Update local ip address Succesfully")
        window.localip_entry.insert=(0,window.localip_entry.get())
    else:
        messagebox.showerror("Update Status","Could not Update local ip address")
        window.localip_entry.insert=(0,dataWarehouse.get_value("LOCALIP","SYSTEMDETAILS"))

##****************************************************************************##
##  updateCentralip method changes the Central ip address in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateCentralip():
    status=dataWarehouse.update_syatemdetails("CENTRALSERVER",window.centralip_entry.get())
    if status:
        messagebox.showinfo("Update Status","Update central ip address Succesfully")
        window.centralip_entry.insert=(0,window.centralip_entry.get())
    else:
        messagebox.showerror("Update Status","Could not Update Central ip address")
        window.centralip_entry.insert=(0,dataWarehouse.get_value("CENTRALSERVER","SYSTEMDETAILS"))


##****************************************************************************##
##  updateMaxbed method changes the Maximum bed number in the database
##  I/P: None
##  O/P: None
##****************************************************************************##
def updateMaxbed():
    status=dataWarehouse.update_syatemdetails("MAXROOM",window.maxbed_entry.get())
    if status:
        messagebox.showinfo("Update Status","Update Maximun bed number Succesfully")
        window.maxbed_entry.insert=(0,window.maxbed_entry.get())
    else:
        messagebox.showerror("Update Status","Could not Update Maximun bed number")
        window.maxbed_entry.insert=(0,dataWarehouse.get_value("MAXROOM","SYSTEMDETAILS"))

        
##****************************************************************************##
##  disconManage method checks and acknowledge call to respective bed
##  I/P: None
##  O/P: None
##****************************************************************************##

def disconManage():
    #print("disconManage function")
    global disconncet_tracker
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    window.discon_box.delete(0,tkinter.END)
    for r in range (1,(len(disconncet_tracker))):
        if disconncet_tracker[r]:
            room,bed,bed_type = dataWarehouse.get_bed_details(r)
            last_con_time = str(dataWarehouse.get_last_conTime(r))
            if bed_type == "bed":
                window.discon_box.insert(tkinter.END,("Room  "+room+"  "+"Bed "+\
                                                      bed+"          Since  "+\
                                                      last_con_time))
            elif bed_type == "room":
                window.discon_box.insert(tkinter.END,("Room  "+room+"  "+"C.M "+\
                                                      bed+"          Since  "+\
                                                      last_con_time))
            elif bed_type == "toilet":
                window.discon_box.insert(tkinter.END,("Toilet  "+room+"        "+\
                                                      "              Since  "+\
                                                      last_con_time))
        else:
            disconncet_tracker[r] = True
            dataWarehouse.set_last_conTime(r,datetime.now().strftime("%H:%M   %x"))
    threading.Timer(disconUpdateTime,disconManage).start()


##****************************************************************************##
##  updateWindow method checks if a call is going to emergency and update display 
##  I/P: None
##  O/P: None
##****************************************************************************##

def updateWindow():
    #print("updateWindow function")
    global delay,secondary_comm,permission,roomcontroller
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    timer_next = (int(delay[2]+delay[3])*60+int(delay[5]+delay[6]))
    fmt = "%H:%M:%S"
    call_type = "Emergency"
    for i in range(0,len(info_table)):
        if info_table[i]:
            retrive = info_table[i]
            room,bed,calltype,ack_type,bed_type = retrive.split(sep)[0],\
                                                  retrive.split(sep)[1],\
                                                  retrive.split(sep)[2],\
                                                  retrive.split(sep)[3],\
                                                  retrive.split(sep)[4]

            
            if calltype not in ('Code Blue','Emergency','Presence','Remote'):
                calltime = dataWarehouse.get_callTime(room,bed)
                current_delay = str(datetime.strptime(time.strftime(fmt),fmt) - \
                                datetime.strptime(calltime,fmt))
                if current_delay> delay:
                    info_table.pop(i)
                    info_table.insert (i,room+sep+bed+\
                                       sep+call_type+\
                                       sep+"nonack"+sep+bed_type)
                    secondary_comm = True
                    count = 0
                    while not permission:
                        time.sleep(.0001)
                        count = count+1
                        if count==1000:
                            secondary_comm = False
                            return
                    if bed_type == "bed" or bed_type == "room":
                        roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                              terminatingCharacter).encode())
                    else:
                        roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                              terminatingCharacter).encode())
                    secondary_comm = False
                    window.window.after(0,updateDisplay)
                    if not GPIO.input(buzerpin):
                        GPIO.output(buzerpin, True)
                    dataWarehouse.update_call(ward,room,bed,call_type)
                    timer_next = 2
                    break
                elif current_delay< delay:
##                    timer_next = datetime.strptime(delay,fmt) - \
##                                 datetime.strptime(str(current_delay),fmt)
                    timer_next = datetime.strptime(delay,fmt) - \
                                 datetime.strptime(current_delay,fmt)
                    timer_next = str(timer_next)
                    minute = int(timer_next[2]+timer_next[3])
                    second = int(timer_next[5]+timer_next[6])
                    timer_next = minute*60+second
                    break
                else:
                    timer_next = 2
                    break 
        else:
            break
    print (Fore.RED +"")
    #print("                  next window update ",timer_next)
    threading.Timer(timer_next,updateWindow).start()


##****************************************************************************##
##  ackCall method checks and acknowledge call to respective bed
##  I/P: labedid
##  O/P: None
##****************************************************************************##

def ackCall(labelid):
    global secondary_comm,permission,roomcontroller
    
    if labelid == 1:
        msg = window.label_1["text"]
    elif labelid == 2:
        msg = window.label_2["text"]
    elif labelid == 3:
        msg = window.label_3["text"]
    elif labelid == 4:
        msg = window.label_4["text"]
    elif labelid == 5:
        msg = window.label_5["text"]
#    elif labelid == 6:
#        msg = window.label_6["text"]

    #msg = msg.split("\n")[1]
#    print("test print one")
#    print(msg)
    bed_type = msg.split(" ")[1]
    if bed_type == "Room:":
        room = msg.split(" ")[2]
        bed = msg.split(" ")[7]
    else:
        room = msg.split(" ")[2]
        bed = '0'

    address = dataWarehouse.get_address(room,bed)
    #print("hellooooooooooooooooo        ",labelid,address,room,bed)

    if address:
        secondary_comm = True
        count = 0
        while not permission:
            time.sleep(.0001)
            count = count+1
            if count==1000:
                secondary_comm = False
                return
        
        roomcontroller.write((chr(int(address))+callAck).encode())
        for i in range(0,len(info_table)):
            retrive = info_table[i]
            ret_room,ret_bed,calltype,ack_type,bed_type = retrive.split(sep)[0],\
                                                          retrive.split(sep)[1],\
                                                          retrive.split(sep)[2],\
                                                          retrive.split(sep)[3],\
                                                          retrive.split(sep)[4]

            if ret_room == room and ret_bed == bed:
                info_table.pop(i)
                info_table.insert (i,room+sep+bed+\
                                    sep+calltype+\
                                    sep+"ack"+sep+bed_type)
        secondary_comm = False
        window.window.after(0,updateDisplay)
        if(calltype == 'Normal'):
            dataWarehouse.update_ack_details(ward,room,bed)

##****************************************************************************##
##  showCall method checks and display and store All the call related
##  informations
##  I/P: Address and Command
##  O/P: None
##****************************************************************************##

def showCall(address,command):
    global secondary_comm,permission,roomcontroller,ward
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    available = False
    position = 0
    
    room,bed,bed_type = dataWarehouse.get_bed_details(address)
    
    for i in range(0,len(info_table)):
        retrive = info_table[i]
        ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                             retrive.split(sep)[1],\
                                             retrive.split(sep)[2],\
                                             retrive.split(sep)[3]

        if ret_room == room and ret_bed == bed:
            available = True
            position = i
    
    if command in('c','C') and not available:
        if bed_type in("room","bed"):
            call_type = "Normal"
            #print("info table")
            #print(len(info_table))
            #print(info_table)     
            info_table.append (room+sep+bed+\
                                sep+call_type+\
                                sep+"nonack"+sep+bed_type)
            secondary_comm = True
            #print ("In show call ",address,command)
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            if bed_type == "bed" or bed_type == "room":
                roomcontroller.write((Broadcast+normalCall+room+sep+bed+\
                                      terminatingCharacter).encode())
            else:
                roomcontroller.write((Broadcast+normalCall+room+sep+bed+\
                                      terminatingCharacter).encode())
                #print("               send R")
            secondary_comm = False
            #print ("In show call ",address,command)
            window.window.after(0,updateDisplay)
            dataWarehouse.insert_call_details(ward,room,bed,call_type)
            
        elif not len(info_table):
            call_type = "Emergency"
            info_table.append (room+sep+bed+\
                                sep+call_type+\
                                sep+"nonack"+sep+bed_type)
            secondary_comm = True
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                  terminatingCharacter).encode())
            print("               send T")
            secondary_comm = False
            window.window.after(0,updateDisplay)
            if not GPIO.input(buzerpin):
                GPIO.output(buzerpin, True)
            dataWarehouse.insert_call_details(ward,room,bed,call_type)
        else:
            call_type ="Emergency"
            for i in range(0,len(info_table)):
                retrive = info_table[i]
                ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                     retrive.split(sep)[1],\
                                                     retrive.split(sep)[2],\
                                                     retrive.split(sep)[3]
                

                if calltype != "Code Blue" and calltype!= "Presence" and calltype != "Remote" and calltype != "Emergency":
                    info_table.insert (i,room+sep+bed+\
                                        sep+call_type+\
                                        sep+"nonack"+sep+bed_type)
                    secondary_comm = True
                    count = 0
                    while not permission:
                        time.sleep(.0001)
                        count = count+1
                        if count==1000:
                            secondary_comm = False
                            return
                    roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                          terminatingCharacter).encode())
                    print("               send T")
                    secondary_comm = False
                    window.window.after(0,updateDisplay)
                    if not GPIO.input(buzerpin):
                        GPIO.output(buzerpin, True)
                    dataWarehouse.insert_call_details(ward,room,bed,call_type)
                    break
                elif i == len(info_table)-1:
                    info_table.insert (len(info_table),room+sep+bed+\
                                        sep+call_type+\
                                        sep+"nonack"+sep+bed_type)
                    secondary_comm = True
                    count = 0
                    while not permission:
                        time.sleep(.0001)
                        count = count+1
                        if count==1000:
                            secondary_comm = False
                            return
                    roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                          terminatingCharacter).encode())
                    print("               send T")
                    secondary_comm = False
                    window.window.after(0,updateDisplay)
                    if not GPIO.input(buzerpin):
                        GPIO.output(buzerpin, True)
                    dataWarehouse.insert_call_details(ward,room,bed,call_type)

    elif command in('b','B') and available:
        
        call_type ="Code Blue"
        
        for i in range(0,len(info_table)):
            retrive = info_table[i]
            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                 retrive.split(sep)[1],\
                                                 retrive.split(sep)[2],\
                                                 retrive.split(sep)[3]

            
            if calltype != call_type:
                info_table.pop(position)
                info_table.insert (i,room+sep+bed+\
                                    sep+call_type+\
                                    sep+"nonack"+sep+bed_type)
                secondary_comm = True
                count = 0
                
                while not permission:
                    time.sleep(.0001)
                    count = count+1
                    if count==1000:
                        secondary_comm = False
                        return
                roomcontroller.write((Broadcast+codeBlueCall+room+sep+bed+\
                                      terminatingCharacter).encode())
                secondary_comm = False
                window.window.after(0,updateDisplay)
                dataWarehouse.update_call(ward,room,bed,call_type)
                
                break
            
    elif command in('p','P') and  available:
        call_type ="Presence"
        dataWarehouse.update_presence_details(ward,room,bed)
        for i in range(0,len(info_table)):
            retrive = info_table[i]
            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                 retrive.split(sep)[1],\
                                                 retrive.split(sep)[2],\
                                                 retrive.split(sep)[3]

            
            if calltype != call_type:
                info_table.pop(position)
                info_table.insert (i,room+sep+bed+\
                                    sep+call_type+\
                                    sep+"nonack"+sep+bed_type)
                
                secondary_comm = True
                count = 0
                while not permission:
                    time.sleep(.0001)
                    count = count+1
                    if count==1000:
                        secondary_comm = False
                        return
                roomcontroller.write((Broadcast+presenceCall+room+sep+bed+\
                                      terminatingCharacter).encode())
                secondary_comm = False
                window.window.after(0,updateDisplay)
                GPIO.output(buzerpin, False)
                '''emergencyStatus=True
                if not emergencyStatus and GPIO.input(buzerpin):
                    GPIO.output(buzerpin, False)'''
                
                break
    
    elif command in('n','N') and not available:
        if bed_type in("room","bed"):
            call_type = "Remote"     
            info_table.append (room+sep+bed+\
                                sep+call_type+\
                                sep+"nonack"+sep+bed_type)
            secondary_comm = True
            #print ("In show call ",address,command)
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            if bed_type == "bed" or bed_type == "room":
                roomcontroller.write((Broadcast+normalCall+room+sep+bed+\
                                      terminatingCharacter).encode())
            else:
                roomcontroller.write((Broadcast+normalCall+room+sep+bed+\
                                      terminatingCharacter).encode())
                #print("               send R")
            secondary_comm = False
            #print ("In show call ",address,command)
            window.window.after(0,updateDisplay)
            dataWarehouse.insert_call_details(ward,room,bed,call_type)
            
        elif not len(info_table):
            call_type = "Emergency"
            info_table.append (room+sep+bed+\
                                sep+call_type+\
                                sep+"nonack"+sep+bed_type)
            secondary_comm = True
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                  terminatingCharacter).encode())
            print("               send T")
            secondary_comm = False
            window.window.after(0,updateDisplay)
            if not GPIO.input(buzerpin):
                GPIO.output(buzerpin, True)
        #dataWarehouse.update_remote_details(ward,room,bed)
            dataWarehouse.insert_call_details(ward,room,bed,call_type)
        else:
            call_type ="Emergency"
            for i in range(0,len(info_table)):
                retrive = info_table[i]
                ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                     retrive.split(sep)[1],\
                                                     retrive.split(sep)[2],\
                                                     retrive.split(sep)[3]
                

                if calltype != "Code Blue" and calltype!= "Presence" and calltype != "Remote" and calltype != "Emergency":
                    info_table.insert (i,room+sep+bed+\
                                        sep+call_type+\
                                        sep+"nonack"+sep+bed_type)
                    secondary_comm = True
                    count = 0
                    while not permission:
                        time.sleep(.0001)
                        count = count+1
                        if count==1000:
                            secondary_comm = False
                            return
                    roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                          terminatingCharacter).encode())
                    print("               send T")
                    secondary_comm = False
                    window.window.after(0,updateDisplay)
                    if not GPIO.input(buzerpin):
                        GPIO.output(buzerpin, True)
                    dataWarehouse.insert_call_details(ward,room,bed,call_type)
                    break
                elif i == len(info_table)-1:
                    info_table.insert (len(info_table),room+sep+bed+\
                                        sep+call_type+\
                                        sep+"nonack"+sep+bed_type)
                    secondary_comm = True
                    count = 0
                    while not permission:
                        time.sleep(.0001)
                        count = count+1
                        if count==1000:
                            secondary_comm = False
                            return
                    roomcontroller.write((Broadcast+emergencyCall+room+sep+bed+\
                                          terminatingCharacter).encode())
                    print("               send T")
                    secondary_comm = False
                    window.window.after(0,updateDisplay)
                    
                    dataWarehouse.insert_call_details(ward,room,bed,call_type)
                    
                    if not GPIO.input(buzerpin):
                        GPIO.output(buzerpin, True)
                    
                    

##****************************************************************************##
##  serviceCall method checks and display and store All the call related
##  informations
##  I/P: Address and Command
##  O/P: None
##****************************************************************************##
            
def serviceCall(address,command):
    global secondary_comm,permission,roomcontroller,ward
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    available = False
    position = 0
    room,bed,bed_type = dataWarehouse.get_bed_details(address)
    emergencyStatus=False
    for i in range(0,len(info_table)):
        retrive = info_table[i]
        ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                             retrive.split(sep)[1],\
                                             retrive.split(sep)[2],\
                                             retrive.split(sep)[3]

        if ret_room == room and ret_bed == bed:
            available = True
            position = i
        
    if command in('s','S') and available:
        #print("i",i)
        #print("position ", position)
        #print("info table", info_table)
        info_table.pop(position)
        secondary_comm = True
        count = 0
        while not permission:
            time.sleep(.0001)
            count = count+1
            if count==1000:
                secondary_comm = False
                return
        if bed_type == "bed":
            roomcontroller.write((Broadcast+Withdraw+room+sep+bed+\
                                  terminatingCharacter).encode())
        elif bed_type == "room":
            roomcontroller.write((Broadcast+Withdraw+room+sep+bed+\
                                  terminatingCharacter).encode())
        elif bed_type == "toilet":
            roomcontroller.write((Broadcast+Withdraw+room+sep+bed+\
                                  terminatingCharacter).encode())
        secondary_comm = False
        window.window.after(0,updateDisplay)
        dataWarehouse.reset_call(ward,room,bed)
    for i in range(0,len(info_table)):
        retrive = info_table[i]
        if retrive.split(sep)[2]== "Emergency":
            emergencyStatus=True
    if not emergencyStatus and GPIO.input(buzerpin):
        GPIO.output(buzerpin, False)

##****************************************************************************##
##  updateDisplay method checks and display All the call related
##  informations
##  I/P: None
##  O/P: None
##****************************************************************************##

def announcementanage():
    global announcement_timer,alarmNotification
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    FNULL = open(os.devnull,'w')
    if len(info_table) == 0:
        announcement_timer = False


    if window.button_call["style"] in ("DOC_Call.TButton","NS_Call.TButton"):
        window.note.select(window.window.tab4)
        pygame.init()
        tone_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(tone_end)
        pygame.mixer.music.load("/home/pi/NurseCall/ring_tone.mp3")
        pygame.mixer.music.play()
        break_event = False
        while True:
            for event in pygame.event.get():
                if event.type == tone_end:
                    announcement_timer = True
                    threading.Timer(2,announcementanage).start()
                    pygame.quit()
                    break_event = True
                    break
            if break_event:
                break
        return
    
    elif window.button_call["style"] in ("DOC_Cancel.TButton","NS_Cancel.TButton"):
        announcement_timer = True
        window.note.select(window.window.tab4)
        threading.Timer(2,announcementanage).start()
        return
    
    if alarmNotification and window.alarm_box.size():
        window.note.select(window.window.tab3)
        pygame.init()
        tone_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(tone_end)
        pygame.mixer.music.load("/home/pi/NurseCall/ring_tone.mp3")
        pygame.mixer.music.play()
        break_event = False
        while True:
            for event in pygame.event.get():
                if event.type == tone_end:
                    announcement_timer = True
                    threading.Timer(2,announcementanage).start()
                    pygame.quit()
                    break_event = True
                    break
            if break_event:
                break
        
        return
    
    for i in range(0,len(info_table)):
        retrive = info_table[i]
        if retrive:
            window.note.select(window.window.tab1)
            ret_room,ret_bed,calltype,ack_type,bed_type = retrive.split(sep)[0],\
                                                          retrive.split(sep)[1],\
                                                          retrive.split(sep)[2],\
                                                          retrive.split(sep)[3],\
                                                          retrive.split(sep)[4]

            if bed_type == "bed" and calltype != "Remote":
                msg = "    Please Attend Call: "
            elif bed_type == "toilet":
                msg = "    Emergency: "
            elif bed_type == "room":
                msg =  "    Please Attend Call: "
            elif bed_type == "bed" and calltype == "Remote":
                msg = " Remote disconnected: "                
            if ack_type != "ack" and calltype != "Presence":
                if calltype == "Code Blue":
                    msg = "Code "+"Blue "
                elif calltype == "Emergency":
                    msg = "    Emergency "
            
                retcode=subprocess.call(['espeak','-ven-us+f3',\
                                         '-a 300','-g 10',msg],\
                                        stdout=FNULL,stderr=subprocess.STDOUT)
                announcement_timer = True
                msg = False
                threading.Timer(3,announcementanage).start()
                break
            elif i == (len(info_table)-1):
                announcement_timer = False
        else:
            announcement_timer = False
            break
    window.note.select(window.window.tab1)

                

##****************************************************************************##
##  updateDisplay method checks and display All the call related
##  informations
##  I/P: None
##  O/P: None
##****************************************************************************##

def updateDisplay():
    #print("updateDisplay function")
    global announcement_timer,pageIndex,pageLength
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)

    if len(info_table) <= pageIndex and pageIndex != 0:
        pageIndex = pageIndex - pageLength

    if pageIndex > 0:
        if  window.previous_button["style"] == "previous_disable.TButton":
            window.previous_button.config(style = "previous_enable.TButton")

    elif window.previous_button["style"] == "previous_enable.TButton":
        window.previous_button.config(style = "previous_disable.TButton")
        
    if (len(info_table)-pageIndex) > pageLength and \
       window.next_button["style"] == "next_disable.TButton":
        window.next_button.config(style = "next_enable.TButton")
    elif (len(info_table)-pageIndex) <= pageLength and \
         window.next_button["style"] == "next_enable.TButton":
        window.next_button.config(style = "next_disable.TButton")
    
    window.button_1.config(style = "N.TButton")
    window.button_2.config(style = "N.TButton")
    window.button_3.config(style = "N.TButton")
    window.button_4.config(style = "N.TButton")
    window.button_5.config(style = "N.TButton")
#    window.button_6.config(style = "N.TButton")

    window.label_1.config(style = "N.TLabel",text = "")
    window.label_2.config(style = "N.TLabel",text = "")
    window.label_3.config(style = "N.TLabel",text = "")
    window.label_4.config(style = "N.TLabel",text = "")
    window.label_5.config(style = "N.TLabel",text = "")
#    window.label_6.config(style = "N.TLabel",text = "")

    window.label_11.config(style = "NT.TLabel",text = "")
    window.label_12.config(style = "NT.TLabel",text = "")
    window.label_13.config(style = "NT.TLabel",text = "")
    window.label_14.config(style = "NT.TLabel",text = "")
    window.label_15.config(style = "NT.TLabel",text = "")
#    window.label_16.config(style = "NT.TLabel",text = "")
    #print("announcement timer  ",announcement_timer)
    if not announcement_timer:
        announcement_timer = True
        announcement = threading.Thread(target = announcementanage)
        announcement.daemon
        announcement.start()
    #print(len(infotable))
    for i in range(0,len(info_table)):
        #print(len(info_table))
        #print(info_table)
        retrive = info_table[i+pageIndex]
        if retrive:
            ret_room,ret_bed,calltype,ack_type,bed_type = retrive.split(sep)[0],\
                                                          retrive.split(sep)[1],\
                                                          retrive.split(sep)[2],\
                                                          retrive.split(sep)[3],\
                                                          retrive.split(sep)[4]
            #print("line 877 room",room)
            #print("line 877 room",bed)
            #print(retrive)
            if bed_type == "bed":
                msg = " Room: "+ret_room+"    Bed: "+ret_bed
            elif bed_type == "toilet":
                msg = " Toilet: "+ret_room
            elif bed_type == "room":
                msg = " Room: "+ret_room+"    Bed: "+ret_bed
                
            if i == 0:
                if calltype == "Code Blue":
                    window.label_1.config(style = "CodeBlue.TLabel",text = msg)
                    window.label_11.config(style = "TCodeBlue.TLabel",text = "Code Blue")

                    if ack_type == "ack":
                        window.button_1.config(style = "Disable.TButton")
                    else:
                        window.button_1.config(style = "Blue.TButton")
                
                elif calltype == "Presence":
                    window.label_1.config(style = "Presence.TLabel",text = msg)
                    window.label_11.config(style = "TPresence.TLabel",text = "Present")

                    if ack_type == "ack":
                        window.button_1.config(style = "Disable.TButton")
                    else:
                        window.button_1.config(style = "Presence.TButton")

                elif calltype == "Remote":
                    window.label_1.config(style = "Remote.TLabel",text = msg)
                    window.label_11.config(style = "TRemote.TLabel",text = "Remote Call")

                    if ack_type == "ack":
                        window.button_1.config(style = "Disable.TButton")
                    else:
                        window.button_1.config(style = "Remote.TButton")                        
                        
                elif calltype == "Emergency":
                    window.label_1.config(style = "Emergency.TLabel",text = msg)
                    window.label_11.config(style = "TEmergency.TLabel",text = "Emergency")

                    if ack_type == "ack":
                        window.button_1.config(style = "Disable.TButton")
                    else:
                        window.button_1.config(style = "Emergency.TButton")

                else:
                    window.label_1.config(style = "Normal.TLabel",text = msg)
                    window.label_11.config(style = "TNormal.TLabel",text = "Normal Call")

                    if ack_type == "ack":
                        window.button_1.config(style = "Disable.TButton")
                    else:
                        window.button_1.config(style = "Normal.TButton")

            elif i == 1:
                if calltype == "Code Blue":
                    window.label_2.config(style = "CodeBlue.TLabel",text = msg)
                    window.label_12.config(style = "TCodeBlue.TLabel",text = "Code Blue")

                    if ack_type == "ack":
                        window.button_2.config(style = "Disable.TButton")
                    else:
                        window.button_2.config(style = "Blue.TButton")
                
                elif calltype == "Presence":
                    window.label_2.config(style = "Presence.TLabel",text = msg)
                    window.label_12.config(style = "TPresence.TLabel",text = "Present")

                    if ack_type == "ack":
                        window.button_2.config(style = "Disable.TButton")
                    else:
                        window.button_2.config(style = "Presence.TButton")

                elif calltype == "Remote":
                    window.label_2.config(style = "Remote.TLabel",text = msg)
                    window.label_12.config(style = "TRemote.TLabel",text = "Remote Call")

                    if ack_type == "ack":
                        window.button_2.config(style = "Disable.TButton")
                    else:
                        window.button_2.config(style = "Remote.TButton")
                        
                elif calltype == "Emergency":
                    window.label_2.config(style = "Emergency.TLabel",text = msg)
                    window.label_12.config(style = "TEmergency.TLabel",text = "Emergency")

                    if ack_type == "ack":
                        window.button_2.config(style = "Disable.TButton")
                    else:
                        window.button_2.config(style = "Emergency.TButton")

                else:
                    window.label_2.config(style = "Normal.TLabel",text = msg)
                    window.label_12.config(style = "TNormal.TLabel",text = "Normal Call")

                    if ack_type == "ack":
                        window.button_2.config(style = "Disable.TButton")
                    else:
                        window.button_2.config(style = "Normal.TButton")

            elif i == 2:
                if calltype == "Code Blue":
                    window.label_3.config(style = "CodeBlue.TLabel",text = msg)
                    window.label_13.config(style = "TCodeBlue.TLabel",text = "Code Blue")

                    if ack_type == "ack":
                        window.button_3.config(style = "Disable.TButton")
                    else:
                        window.button_3.config(style = "Blue.TButton")
                
                elif calltype == "Presence":
                    window.label_3.config(style = "Presence.TLabel",text = msg)
                    window.label_13.config(style = "TPresence.TLabel",text = "Present")

                    if ack_type == "ack":
                        window.button_3.config(style = "Disable.TButton")
                    else:
                        window.button_3.config(style = "Presence.TButton")

                elif calltype == "Remote":
                    window.label_3.config(style = "Remote.TLabel",text = msg)
                    window.label_13.config(style = "TRemote.TLabel",text = "Remote Call")

                    if ack_type == "ack":
                        window.button_3.config(style = "Disable.TButton")
                    else:
                        window.button_3.config(style = "Remote.TButton")


                elif calltype == "Emergency":
                    window.label_3.config(style = "Emergency.TLabel",text = msg)
                    window.label_13.config(style = "TEmergency.TLabel",text = "Emergency")

                    if ack_type == "ack":
                        window.button_3.config(style = "Disable.TButton")
                    else:
                        window.button_3.config(style = "Emergency.TButton")

                else:
                    window.label_3.config(style = "Normal.TLabel",text = msg)
                    window.label_13.config(style = "TNormal.TLabel",text = "Normal Call")

                    if ack_type == "ack":
                        window.button_3.config(style = "Disable.TButton")
                    else:
                        window.button_3.config(style = "Normal.TButton")

            elif i == 3:
                if calltype == "Code Blue":
                    window.label_4.config(style = "CodeBlue.TLabel",text = msg)
                    window.label_14.config(style = "TCodeBlue.TLabel",text = "Code Blue")

                    if ack_type == "ack":
                        window.button_4.config(style = "Disable.TButton")
                    else:
                        window.button_4.config(style = "Blue.TButton")
                
                elif calltype == "Presence":
                    window.label_4.config(style = "Presence.TLabel",text = msg)
                    window.label_14.config(style = "TPresence.TLabel",text = "Present")

                    if ack_type == "ack":
                        window.button_4.config(style = "Disable.TButton")
                    else:
                        window.button_4.config(style = "Presence.TButton")

                elif calltype == "Remote":
                    window.label_4.config(style = "Remote.TLabel",text = msg)
                    window.label_14.config(style = "TRemote.TLabel",text = "Remote Call")

                    if ack_type == "ack":
                        window.button_4.config(style = "Disable.TButton")
                    else:
                        window.button_4.config(style = "Remote.TButton")


                elif calltype == "Emergency":
                    window.label_4.config(style = "Emergency.TLabel",text = msg)
                    window.label_14.config(style = "TEmergency.TLabel",text = "Emergency")

                    if ack_type == "ack":
                        window.button_4.config(style = "Disable.TButton")
                    else:
                        window.button_4.config(style = "Emergency.TButton")

                else:
                    window.label_4.config(style = "Normal.TLabel",text = msg)
                    window.label_14.config(style = "TNormal.TLabel",text = "Normal Call")

                    if ack_type == "ack":
                        window.button_4.config(style = "Disable.TButton")
                    else:
                        window.button_4.config(style = "Normal.TButton")

            elif i == 4:
                if calltype == "Code Blue":
                    window.label_5.config(style = "CodeBlue.TLabel",text = msg)
                    window.label_15.config(style = "TCodeBlue.TLabel",text = "Code Blue")

                    if ack_type == "ack":
                        window.button_5.config(style = "Disable.TButton")
                    else:
                        window.button_5.config(style = "Blue.TButton")
                
                elif calltype == "Presence":
                    window.label_5.config(style = "Presence.TLabel",text = msg)
                    window.label_15.config(style = "TPresence.TLabel",text = "Present")

                    if ack_type == "ack":
                        window.button_5.config(style = "Disable.TButton")
                    else:
                        window.button_5.config(style = "Presence.TButton")

                elif calltype == "Remote":
                    window.label_5.config(style = "Remote.TLabel",text = msg)
                    window.label_15.config(style = "TRemote.TLabel",text = "Remote Call")

                    if ack_type == "ack":
                        window.button_5.config(style = "Disable.TButton")
                    else:
                        window.button_5.config(style = "Remote.TButton")


                elif calltype == "Emergency":
                    window.label_5.config(style = "Emergency.TLabel",text = msg)
                    window.label_15.config(style = "TEmergency.TLabel",text = "Emergency")

                    if ack_type == "ack":
                        window.button_5.config(style = "Disable.TButton")
                    else:
                        window.button_5.config(style = "Emergency.TButton")

                else:
                    window.label_5.config(style = "Normal.TLabel",text = msg)
                    window.label_15.config(style = "TNormal.TLabel",text = "Normal Call")

                    if ack_type == "ack":
                        window.button_5.config(style = "Disable.TButton")
                    else:
                        window.button_5.config(style = "Normal.TButton")

##            elif i == 5:
##                if calltype == "Code Blue":
##                    window.label_6.config(style = "CodeBlue.TLabel",text = msg)
##                    window.label_16.config(style = "TCodeBlue.TLabel",text = "Code Blue")
##
##                    if ack_type == "ack":
##                        window.button_6.config(style = "Disable.TButton")
##                    else:
##                        window.button_6.config(style = "Blue.TButton")
##
##                elif calltype == "Emergency":
##                    window.label_6.config(style = "Emergency.TLabel",text = msg)
##                    window.label_16.config(style = "TEmergency.TLabel",text = "Emergency")
##
##                    if ack_type == "ack":
##                        window.button_6.config(style = "Disable.TButton")
##                    else:
##                        window.button_6.config(style = "Emergency.TButton")
##
##                else:
##                    window.label_6.config(style = "Normal.TLabel",text = msg)
##                    window.label_16.config(style = "TNormal.TLabel",text = "Normal Call")
##
##                    if ack_type == "ack":
##                        window.button_6.config(style = "Disable.TButton")
##                    else:
##                        window.button_6.config(style = "Normal.TButton")

            else:
                break
        else:
            break


##****************************************************************************##
##  monitorcallPickup method checks if call is picked within time
##  I/P: None
##  O/P: None
##****************************************************************************##


def monitorcallPickup():
    global talkAddress,talkOnProcess,secondary_comm,permission,roomcontroller,call_picked_up

    talkFinish = chr(120)
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)

    if not talkOnProcess and not call_picked_up:
        secondary_comm = True
        count = 0
        while not permission:
            time.sleep(.0001)
            count = count+1
            if count==1000:
                secondary_comm = False
                return
        roomcontroller.write((chr(talkAddress)+talkFinish).encode())
        secondary_comm = False
        talkAddress = False
        GPIO.output(TalkRelay, False)
        window.label_call_1.config(style = "N.TLabel",text="")
        window.label_call_2.config(style = "N.TLabel",text="")
        window.button_call.config(style = "N.TButton")
        window.note.select(window.window.tab1)
        
##****************************************************************************##
##  talkManage method performs call related  operations
##  I/P: address,command
##  O/P: None
##****************************************************************************##


def talkManage(address,command):
    global talkAddress,talkOnProcess,secondary_comm,permission,roomcontroller,\
           timer_time,announcement_timer,call_picked_up
    
    if command in ('DC','NC'):
        if talkAddress:
            secondary_comm = True
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            roomcontroller.write((chr(address)+Engage).encode())
            secondary_comm = False
        else:
            secondary_comm = True
            count = 0
            while not permission:
                time.sleep(.0001)
                count = count+1
                if count==1000:
                    secondary_comm = False
                    return
            roomcontroller.write((chr(address)+Dial).encode())
            secondary_comm = False
            talkAddress = address
            #print ("In talkManage          ",talkAddress,command)
            room,bed,bed_type = dataWarehouse.get_bed_details(address)

            if command == "DC":
                msg1 = " Doctor's Call   "
                msg2 = " Room    "+room
                window.label_call_1.config(style = "Normal.TLabel",text = msg1)
                window.label_call_2.config(style = "Normal.TLabel",text = msg2)
                window.button_call.config(style = "DOC_Call.TButton")
                window.note.select(window.window.tab4)
                threading.Timer(120,monitorcallPickup).start()
                if not announcement_timer:
                    announcement = threading.Thread(target = announcementanage)
                    announcement.daemon
                    announcement.start()
            else:
                msg1 = " Nurse Call   "
                msg2 = " Room    "+room
                window.label_call_1.config(style = "Normal.TLabel",text = msg1)
                window.label_call_2.config(style = "Normal.TLabel",text = msg2)
                window.button_call.config(style = "NS_Call.TButton")
                window.note.select(window.window.tab4)
                threading.Timer(70,monitorcallPickup).start()
                if not announcement_timer:
                    announcement = threading.Thread(target = announcementanage)
                    announcement.daemon
                    announcement.start()


    elif command in ('DS','NS'):
        if talkAddress == address:
            GPIO.output(TalkRelay, False)
            talkAddress = talkOnProcess = False
            
            if timer_time:
                window.alarm_box.insert(tkinter.END,(window.label_call_2["text"]+\
                                                     "         Time  "+\
                                                     time.strftime("%H:%M")))
                window.button_alarm_1.config(style = "AlarmDisable.TButton")
                window.button_alarm_2.config(style = "AlarmDisable.TButton")
                window.button_alarm_3.config(style = "AlarmDisable.TButton")
                threading.Timer(timer_time,alarmShow).start()
                timer_time = False
            window.label_call_1.config(style = "N.TLabel",text="")
            window.label_call_2.config(style = "N.TLabel",text="")
            window.button_call.config(style = "N.TButton")
            if call_picked_up:
                call_picked_up=False
            window.note.select(window.window.tab1)

            
##****************************************************************************##
##  Monitor method checks and control All the call related information
##  I/P: None
##  O/P: None
##****************************************************************************##


def callPickup():
    global talkAddress,talkOnProcess,secondary_comm,permission,roomcontroller,\
           callWindow,label_call,button_call,cancel,timer_time,call_picked_up

    talkPermission = chr(121)
    talkFinish = chr(120)

    if not talkOnProcess and not window.button_call["style"] == "N.TButton":
        talkOnProcess = True
        secondary_comm = True
        if not call_picked_up:
            call_picked_up=True
        count = 0
        while not permission:
            time.sleep(.0001)
            count = count+1
            if count==1000:
                secondary_comm = False
                return
        roomcontroller.write((chr(talkAddress)+talkPermission).encode())
        secondary_comm = False
        GPIO.output(TalkRelay, True)
        window.label_call_1.config(text = "Call On Progress")
        if window.button_call["style"] == "DOC_Call.TButton":
            window.button_call.config(style = "DOC_Cancel.TButton")
        else:
            window.button_call.config(style = "NS_Cancel.TButton")
    else:
        secondary_comm = True
        count = 0
        while not permission:
            time.sleep(.0001)
            count = count+1
            if count==1000:
                secondary_comm = False
                return
        roomcontroller.write((chr(talkAddress)+talkFinish).encode())
        secondary_comm = False
        talkAddress = talkOnProcess = False
        GPIO.output(TalkRelay, False)
        
        if timer_time:
            window.alarm_box.insert(tkinter.END,(window.label_call_2["text"]+\
                                                 "         Time  "+\
                                                 time.strftime("%H:%M")))
            window.button_alarm_1.config(style = "AlarmDisable.TButton")
            window.button_alarm_2.config(style = "AlarmDisable.TButton")
            window.button_alarm_3.config(style = "AlarmDisable.TButton")
            threading.Timer(timer_time,alarmShow).start()
            timer_time = False
        window.label_call_1.config(style = "N.TLabel",text="")
        window.label_call_2.config(style = "N.TLabel",text="")
        window.button_call.config(style = "N.TButton")
        window.note.select(window.window.tab1)

##****************************************************************************##
##  Monitor method checks and control All the call related information
##  I/P: None
##  O/P: None
##****************************************************************************##

def alarmShow():
    global alarmNotification,announcement_timer
    alarmNotification = True
    if not announcement_timer:
        announcement = threading.Thread(target = announcementanage)
        announcement.daemon
        announcement.start()
    
def alarmClose():
    global alarmNotification
    alarmNotification = False
    window.alarm_box.delete(0)
    

##****************************************************************************##
##  Monitor method checks and control All the call related information
##  I/P: None
##  O/P: None
##****************************************************************************##

def alarmManage(button_number):
    global timer_time
    for i in threading.enumerate():
        if i.name == "MainThread":
            run = i.is_alive()

    if not run:
        val = get_pid("python3")
        val = val.decode()
        command = "sudo kill -9 "+val
        os.system(command)
    
    if button_number == 1:
        if timer_time and window.button_alarm_1["style"] == "AlarmEnable.TButton":
            timer_time = False
            window.button_alarm_1.config(style = "AlarmDisable.TButton")
        elif window.button_call["style"] == "DOC_Cancel.TButton" or \
             window.button_call["style"]=="NS_Cancel.TButton":
            timer_time = 5*60
            window.button_alarm_1.config(style = "AlarmEnable.TButton")
            window.button_alarm_2.config(style = "AlarmDisable.TButton")
            window.button_alarm_3.config(style = "AlarmDisable.TButton")
    elif button_number == 2:
        if timer_time and window.button_alarm_2["style"] == "AlarmEnable.TButton":
            timer_time = False
            window.button_alarm_2.config(style = "AlarmDisable.TButton")
        elif window.button_call["style"] == "DOC_Cancel.TButton" or \
             window.button_call["style"]=="NS_Cancel.TButton":
            timer_time = 10*60
            window.button_alarm_2.config(style = "AlarmEnable.TButton")
            window.button_alarm_1.config(style = "AlarmDisable.TButton")
            window.button_alarm_3.config(style = "AlarmDisable.TButton")
    elif button_number == 3:
        if timer_time and window.button_alarm_3["style"] == "AlarmEnable.TButton":
            timer_time = False
            window.button_alarm_3.config(style = "AlarmDisable.TButton")
        elif window.button_call["style"] == "DOC_Cancel.TButton" or \
             window.button_call["style"]=="NS_Cancel.TButton":
            timer_time = 15*60
            window.button_alarm_3.config(style = "AlarmEnable.TButton")
            window.button_alarm_1.config(style = "AlarmDisable.TButton")
            window.button_alarm_2.config(style = "AlarmDisable.TButton")

##****************************************************************************##
##  Monitor method checks and control All the call related information
##  I/P: None
##  O/P: None
##****************************************************************************##

def Monitor():
    global secondary_comm,permission,roomcontroller,ward,delay,\
           disconncet_tracker,run,talkAddress,talkOnProcess,callWindow
    update = threading.Thread(target = doNothing)
    update.daemon
    update.start()

    talkThread = threading.Thread(target = doNothing)
    talkThread.daemon
    talkThread.start()
    
    try:
        ip = dataWarehouse.get_value("LOCALIP","SYSTEMDETAILS")
        totalbed = int(dataWarehouse.get_value("MAXROOM","SYSTEMDETAILS"))
        centralserver = dataWarehouse.get_value("CENTRALSERVER","SYSTEMDETAILS")
        ward = dataWarehouse.get_value("WARD","SYSTEMDETAILS")
        hospitalName = dataWarehouse.get_value("HOSPITAL_NAME","SYSTEMDETAILS")
        baudRate = int(dataWarehouse.get_value("BAUDRATE","SYSTEMDETAILS"))
        delay = dataWarehouse.get_value("DELAY","ALARM")

        msg = "  "+hospitalName+"   " +"Ward: "+ward+ "                    "

        try:
            time.sleep(.3)
            window.my_tickers.set(msg)
            window.hos_entry.insert(0,hospitalName)
            window.ward_entry.insert(0,ward)
        except Exception as e:
            print(e)

        
        os.system('sudo ifconfig eth0 down')
        os.system('sudo ifconfig eth0 %s'%ip)
        os.system('sudo ifconfig eth0 up')
        

        roomcontroller=serial.Serial(comPort,baudrate=baudRate,timeout=timeOut)

        for r in range(0,totalbed+1):
            disconncet_tracker.append(True)
        
    except Exception as e:
        print (Fore.RED +"")
        print (e)
        exit()

    try:
        pendingCalls = dataWarehouse.get_pendingalls()
        if pendingCalls:
            for row in pendingCalls:
                room,bed,call_type = row[0],row[1],row[2]
                address = dataWarehouse.get_address(room,bed)
                ret_room,ret_bed,bed_type = dataWarehouse.get_bed_details(address)
                if room == ret_room and bed == ret_bed:
                    if call_type == "Code Blue":
                        inserted = False
                        for i in range(0,len(info_table)):
                            retrive = info_table[i]
                            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                                 retrive.split(sep)[1],\
                                                                 retrive.split(sep)[2],\
                                                                 retrive.split(sep)[3]

                            
                            if calltype != "Code Blue":
                                info_table.insert (i,room+sep+bed+\
                                                    sep+call_type+\
                                                    sep+"nonack"+sep+bed_type)
                                inserted = True
                                break
                        if inserted == False:
                            info_table.append (room+sep+bed+\
                                                sep+call_type+\
                                                sep+"nonack"+sep+bed_type)
                            continue
                    
                    elif call_type == "Presence":
                        inserted = False
                        for i in range(0,len(info_table)):
                            retrive = info_table[i]
                            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                                 retrive.split(sep)[1],\
                                                                 retrive.split(sep)[2],\
                                                                 retrive.split(sep)[3]

                            
                            if calltype != "Presence" and calltype != "Code Blue" :
                                info_table.insert (i,room+sep+bed+\
                                                    sep+call_type+\
                                                    sep+"nonack"+sep+bed_type)
                                inserted = True
                                break
                        if inserted == False:
                            info_table.append (room+sep+bed+\
                                                sep+call_type+\
                                                sep+"nonack"+sep+bed_type)
                            continue   
                    

                    elif call_type == "Remote":
                        inserted = False
                        for i in range(0,len(info_table)):
                            retrive = info_table[i]
                            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                                 retrive.split(sep)[1],\
                                                                 retrive.split(sep)[2],\
                                                                 retrive.split(sep)[3]

                            
                            if calltype != "Presence" and calltype != "Remote"  and calltype != "Code Blue" :
                                info_table.insert (i,room+sep+bed+\
                                                    sep+call_type+\
                                                    sep+"nonack"+sep+bed_type)
                                inserted = True
                                break
                        if inserted == False:
                            info_table.append (room+sep+bed+\
                                                sep+call_type+\
                                                sep+"nonack"+sep+bed_type)
                            continue  

                    elif call_type == "Emergency":
                        inserted = False
                        
                        for i in range(0,len(info_table)):
                            retrive = info_table[i]
                            ret_room,ret_bed,calltype,ack_type = retrive.split(sep)[0],\
                                                                 retrive.split(sep)[1],\
                                                                 retrive.split(sep)[2],\
                                                                 retrive.split(sep)[3]
                            
                            if calltype != "Code Blue" and calltype != "Emergency" and calltype != "Remote" and calltype != "Presence":
                                info_table.insert (i,room+sep+bed+\
                                                    sep+call_type+\
                                                    sep+"nonack"+sep+bed_type)
                                inserted = True
                                break
                        if inserted == False:
                            info_table.append (room+sep+bed+\
                                                sep+call_type+\
                                                sep+"nonack"+sep+bed_type)
                            continue
                    else:
                        info_table.append (room+sep+bed+\
                                            sep+call_type+\
                                            sep+"nonack"+sep+bed_type)
            window.window.after(0,updateDisplay)
    except Exception as e:
        print (Fore.RED +"")
        print (e)   

    while True:
        for i in threading.enumerate():
            if i.name == "MainThread":
                run = i.is_alive()

        if not run:
            val = get_pid("python3")
            val = val.decode()
            command = "sudo kill -9 "+val
            os.system(command)

        window.my_clock.set(time.strftime("%H:%M"))
        window.my_date.set(datetime.now().strftime("%d/%m/%Y"))

        for address in range(1,(totalbed+1)):
            #print("total bed", totalbed)
            try:
                #time.sleep(.002)
                GPIO.output(REpin, False)
                
                while (secondary_comm):
                    if not permission:
                        permission = True
                    time.sleep(.01)
                if permission:
                    permission = False
                roomcontroller.flushInput()
                ##serialData1 = serial.read(24)
                ##print("print flush1", serialData1)
                time.sleep(.001)
                roomcontroller.write((chr(address)+Response).encode())
                
                print (Fore.CYAN +"")
                print ("Address ",address)

                time.sleep(.001)#
                GPIO.output(REpin, True)

                receiveddata= roomcontroller.read(24) #receiveddata= roomcontroller.readline()

               
                GPIO.output(REpin, False)

                if not receiveddata:
                    print (Fore.YELLOW+"                No Data ")
                    continue
                elif len(receiveddata)>1 and receiveddata[0] == address:
                    if chr(receiveddata[1]) == 'l' or chr(receiveddata[1]) == 'L':
                        print ("                                ",\
                               str(receiveddata[0])+chr(receiveddata[1]))
                        roomcontroller.write((chr(address)+dataAck).encode())
                        disconncet_tracker[address] = False
                        continue
                    elif chr(receiveddata[1]) in ('C','c','B','b','P','p','n','N'):
                        print ("                                             ",\
                               str(receiveddata[0])+chr(receiveddata[1]))
                        disconncet_tracker[address] = False
                        roomcontroller.write((chr(address)+dataAck).encode())
                        while update.is_alive():
                            if not permission:
                                permission = True
                            time.sleep(.001)
                        update = threading.Thread(target = showCall,\
                                                  args=(address,chr(receiveddata[1])))
                        update.daemon
                        update.start()
                       
                    elif chr(receiveddata[1]) in ('s','S'):
                        print ("                                             ",\
                               str(receiveddata[0])+chr(receiveddata[1]))
                        roomcontroller.write((chr(address)+dataAck).encode())
                        disconncet_tracker[address] = False
                        while update.is_alive():
                            if not permission:
                                permission = True
                            time.sleep(.001)
                        update = threading.Thread(target = serviceCall,\
                                                  args=(address,chr(receiveddata[1])))
                        update.daemon
                        update.start()
                    elif len(receiveddata) == 3:
                    
                        print ("                                             ",\
                               str(receiveddata[0])+chr(receiveddata[1])+chr(receiveddata[2]))
                        roomcontroller.write((chr(address)+dataAck).encode())
                        disconncet_tracker[address] = False
                        command = chr(receiveddata[1]) + chr(receiveddata[2])

                        while talkThread.is_alive():
                            if not permission:
                                permission = True
                            time.sleep(.001)
                        talkThread = threading.Thread(target = talkManage,\
                                                      args=(address,command))
                        talkThread.daemon
                        talkThread.start()
                        
                    else:
                        roomcontroller.write((chr(address)+dataNAck).encode())
                        print ("                          Data Corrupted           ",receiveddata)
                
            except Exception as e:
                print (Fore.RED +"")
                print (e)
        
##****************************************************************************##
##  Start Monitor Thread
##****************************************************************************##


monitor = threading.Thread(target = Monitor)
monitor.daemon
monitor.start()

threading.Timer(3,disconManage).start()
threading.Timer(10,updateWindow).start()

#window.mainloop()



