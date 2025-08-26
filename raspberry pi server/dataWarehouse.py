##Project Name: incms-R8
##Target Area:  Hospitals
##Created Date: 21/02/2019
##Author:       Anup Sarkar
##
##This file will manage all the database related operation for incms-R8
##
##********************************************************************

#!/usr/bin/env/ python

import datetime,time,pymysql,pymysql.cursors
from datetime import datetime
from colorama import Fore,Back,Style

HOST = "localhost"
PORT = 3306
USER = "admin"
PASSWORD = "anup"
DB = "NursecallDB"

csuser = "Admin"
cspass = "iNCMS-R9@2024"
csname = "NursecallDB"

fmt="%H:%M:%S"

##Input: Table Name and required field
##Output: The field data
##***********************************************************

def get_value(field,table):
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= ("select %s from %s"%(field,table))
        cursor.execute(sql)
        db.close()
        data = cursor.fetchone()
        if data:
            #print("Returned ",str(data[0]))
            return(data[0])
    except Exception as e:
        print (e)

##Input: Room and Bed Number
##Output: The Bed Address
##***********************************************************

def get_address(room,bed):
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= ("select BEDID from RBNAME where ROOM_NO = '%s' and BED_NO ='%s'"%(room,bed))
        cursor.execute(sql)
        db.close()
        data = cursor.fetchone()
        if data:
            return(data[0])
    except Exception as e:
        print (e)

        
##***********************************************************##
##Input: Parameter name,Value
##Output: None
##***********************************************************##

def update_syatemdetails(field,value):
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "UPDATE SYSTEMDETAILS SET %s='%s'"%(field,value)
        cursor.execute(sql)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print (e)
        return False


##***********************************************************##
##Input: old room and bed no,new Room and bed no and type
##Output: None
##***********************************************************##

def update_roombedName(oldroom,oldbed,newroom,newbed,newtype):
    
    try:
        address = get_address(oldroom,oldbed)
        if address:
            db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                                passwd=PASSWORD, db=DB)
            cursor=db.cursor()
            sql= "UPDATE RBNAME SET ROOM_NO='%s', BED_NO='%s',BED_TYPE='%s'\
                  WHERE ROOM_NO='%s'AND BED_NO='%s'"%\
                  (newroom,newbed,newtype,oldroom,oldbed)
            cursor.execute(sql)
            db.commit()
            db.close()
            return True
        else:
            return ("No Match")
    except Exception as e:
        print (e)
        return False

##***********************************************************
##Input:  Address of the Bed
##Output: Details of the Bed
##***********************************************************

def get_bed_details(address):
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "SELECT ROOM_NO,BED_NO,BED_TYPE FROM RBNAME WHERE BEDID='%d'"%address
        cursor.execute(sql)
        db.close()
        data = cursor.fetchall()
        if data:
            return data[0][0],data[0][1],data[0][2]
    except Exception as e:
        print (e)

##***********************************************************
##Input:  Address of the Bed
##Output: Details of the Bed
##***********************************************************

def get_callTime(room,bed):
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= ("select CALL_AT from CALLRECORD where ROOM_NO = '%s' and BED_NO ='%s' and STATUS='S'"%(room,bed))
        cursor.execute(sql)
        db.close()
        data = cursor.fetchone()
        if data:
            return(data[0])
    except Exception as e:
        print (e)

##***********************************************************
##Input:  ward,room,bed,call_type of the Bed
##Output: None
##***********************************************************

def insert_call_details(ward,room,bed,call_type):
    status = 'S'
    time_now = time.strftime(fmt)
    date_today = datetime.now().strftime("%d/%m/%Y")
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "INSERT INTO CALLRECORD(DATE,CALLTYPE,ROOM_NO,BED_NO,WARD,CALL_AT,STATUS)\
              VALUES('%s','%s','%s','%s','%s','%s','%s')"%(date_today,call_type,room,bed,\
                                                           ward,time_now,status)
        cursor.execute(sql)
        db.commit()
        db.close()
        #print (Fore.CYAN+"Data Inserted Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        #print(Fore.YELLOW+"Data Could Not Insert into Local Database")
        
    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        #print("centralserver ip " , centralserver)
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname, connect_timeout=2)
            cursor=db.cursor()
            sql= "INSERT INTO callrecord(DATE,CALLTYPE,ROOM_NO,BED_NO,WARD,CALL_AT,STATUS)\
                  VALUES('%s','%s','%s','%s','%s','%s','%s')"%(date_today,call_type,room,bed,\
                                                               ward,datetime.now(),status)
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Inserted Into Central database")     

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW+"Data Could Not Insert into Central Database")

##***********************************************************
##Input:  ward,room,bed,call_type of the Bed
##Output: None
##***********************************************************
    
def update_call(ward,room,bed,call_type):

    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "UPDATE CALLRECORD SET CALLTYPE='%s' WHERE WARD='%s'\
              AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (call_type,ward,room,bed )
        cursor.execute(sql)
        db.commit()
        db.close()
        #print (Fore.CYAN+"Data Updated Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        #print(Fore.YELLOW +"Data Could Not Update into Local Database")
        
    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname,connect_timeout=2)
            cursor=db.cursor()
            sql= "UPDATE callrecord SET CALLTYPE='%s' WHERE WARD='%s'\
                  AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
                 (call_type,ward,room,bed )
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Updated Into Central database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW +"Data Could Not Update into Central Database")

##***********************************************************
##Input:  ward,room,bed of the Bed
##Output: None
##***********************************************************

def reset_call(ward,room,bed):
    
    servicetime=time.strftime(fmt)
    

    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= ("SELECT CALL_AT FROM CALLRECORD WHERE ROOM_NO='%s' AND BED_NO='%s' \
               AND STATUS='S'"%(room,bed))
        cursor.execute(sql)
        calltime=cursor.fetchone()
        for row in calltime:
            calltime="".join(row)
        delay =datetime.strptime(servicetime, fmt) - datetime.strptime(calltime, fmt)
        sql="UPDATE CALLRECORD SET SERVED_AT='%s', TIME_TAKEN='%s', STATUS='R' \
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (servicetime,delay,ward,room,bed )
        cursor.execute(sql)
        db.commit()
        db.close()
        #print (Fore.CYAN+"Data Updated Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        #print(Fore.YELLOW +"Data Could Not Update into Local Database")
        
    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname,connect_timeout=2)
            cursor=db.cursor()
            sql= ("SELECT CALL_AT FROM CALLRECORD WHERE ROOM_NO='%s' AND BED_NO='%s' AND WARD='%s'\
               AND STATUS='S'"%(room,bed,ward))
            cursor.execute(sql)
            calltime=cursor.fetchone()
            if not calltime:
                print("No matching record found")
                return
            call_at = calltime[0] if isinstance(calltime[0], datetime) else datetime.strptime(calltime[0],"%Y-%m-%d %H:%M:%S")
            served_at = datetime.now()
            delay = served_at - call_at
            sql="UPDATE callrecord SET SERVED_AT='%s', TIME_TAKEN='%s', STATUS='R' \
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (served_at,delay,ward,room,bed )
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Updated Into Central database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW +"Data Could Not Update into Central Database")

##***********************************************************
##Input:  ward,room,bed of the Bed
##Output: None
##***********************************************************

def get_last_conTime(address):
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "SELECT LAST_CON FROM RBNAME WHERE BEDID='%d'"%address
        cursor.execute(sql)
        db.close()
        data = cursor.fetchall()
        if data:
            return (data[0][0])
    except Exception as e:
        print (e)

##***********************************************************
##Input:  ward,room,bed of the Bed
##Output: None
##***********************************************************

def set_last_conTime(address,time):
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "UPDATE RBNAME SET LAST_CON ='%s' WHERE BEDID='%d'"%(time,address)
        cursor.execute(sql)
        db.commit()
        db.close()
    except Exception as e:
        print (e)

##***********************************************************
##Input:  None
##Output: Details of the Pending Calls
##***********************************************************

def get_pendingalls():
    
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql= "SELECT ROOM_NO,BED_NO,CALLTYPE FROM CALLRECORD WHERE STATUS='S'"
        cursor.execute(sql)
        db.close()
        data = cursor.fetchall()
        if data:
            return data
    except Exception as e:
        print (e)


##***********************************************************
##Input:  ward,room,bed
##Output: None
##***********************************************************

def update_ack_details(ward,room,bed):
    status = 'S'
    time_now = time.strftime(fmt)
    #date_today = datetime.now().strftime("%d/%m/%Y")
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql="UPDATE CALLRECORD SET ACK_AT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (time_now,ward,room,bed )
        cursor.execute(sql)
        db.commit()
        db.close()
        #print (Fore.CYAN+"Data Inserted Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        #print(Fore.YELLOW+"Data Could Not Insert into Local Database")

    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname,connect_timeout=2)
            cursor=db.cursor()
            sql="UPDATE callrecord SET ACK_AT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (time_now,ward,room,bed )
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Updated Into Central database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW +"Data Could Not Update into Central Database")

##***********************************************************
##Input:  ward,room,bed
##Output: None
##***********************************************************
        
def update_presence_details(ward,room,bed):
    status = 'S'
    time_now = time.strftime(fmt)
    #date_today = datetime.now().strftime("%d/%m/%Y")
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql="UPDATE CALLRECORD SET PRESENCE_AT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (time_now,ward,room,bed )
        cursor.execute(sql)
        db.commit()
        db.close()
        print (Fore.CYAN+"Presence Data Inserted Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW+"Presence Data Could Not Insert into Local Database")

    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname,connect_timeout=2)
            cursor=db.cursor()
            sql="UPDATE callrecord SET PRESENCE_AT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (time_now,ward,room,bed )
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Updated Into Central database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW +"Data Could Not Update into Central Database")

##***********************************************************
##Input:  ward,room,bed
##Output: None
##***********************************************************
        
def update_remote_details():
    status = 'S'
    time_now = time.strftime(fmt)
    #date_today = datetime.now().strftime("%d/%m/%Y")
    try:
        db= pymysql.connect(host=HOST, port=PORT,user=USER,\
                            passwd=PASSWORD, db=DB)
        cursor=db.cursor()
        sql="UPDATE CALLRECORD SET disConAT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s'"%\
             (time_now,ward,room,bed )
        cursor.execute(sql)
        db.commit()
        db.close()
        print (Fore.CYAN+"remote Data Inserted Into Local database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW+"remote Data Could Not Insert into Local Database")
        
    try:
        centralserver = get_value("CENTRALSERVER","SYSTEMDETAILS")
        if centralserver:
            db= pymysql.connect(host=centralserver, user=csuser,\
                                passwd=cspass, db=csname,connect_timeout=2)
            cursor=db.cursor()
            sql="UPDATE callrecord SET disConAT='%s'\
             WHERE WARD='%s' AND ROOM_NO='%s' AND BED_NO='%s' AND STATUS='S'"%\
             (time_now,ward,room,bed )
            cursor.execute(sql)
            db.commit()
            db.close()
            print (Fore.CYAN+"Data Updated Into Central database")

    except Exception as e:
        print (Fore.RED +"")
        print (e)
        print(Fore.YELLOW +"Data Could Not Update into Central Database")
