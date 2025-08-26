#!/usr/bin/idle-python2.7
import pymysql
import pymysql.cursors
#Create database
db= pymysql.connect("localhost","admin","anup")
cursor=db.cursor()
try:
    cursor.execute("CREATE DATABASE NursecallDB")
    print ("NursecallDB database created")
except Exception as e:
    print (e)
    print ("can't create database NursecallDB")

#open database connection
db= pymysql.connect("localhost","admin","anup","NursecallDB")
#prepare a cursor object using cursor() method
cursor=db.cursor()
#drop table if already exists using execute() method.
cursor.execute("DROP TABLE IF EXISTS CALLRECORD")
#Create table as per requirement
sql="""CREATE TABLE CALLRECORD(
       DATE CHAR(12) NOT NULL,
       ROOM_NO CHAR(20) NOT NULL,
       BED_NO CHAR(20) NOT NULL,
       WARD CHAR(25),
       STATUS CHAR(3),
       CALLTYPE CHAR(10),
       CALL_AT CHAR(13),
       SERVED_AT CHAR(13),
       TIME_TAKEN CHAR(13))"""
try:
    cursor.execute(sql)
    print ("CALLRECORD table created")
except:
   print ("can't create CALLRECORD table")
cursor.execute("DROP TABLE IF EXISTS ALARM")
sql="""CREATE TABLE ALARM(
       DELAY CHAR(8) NOT NULL)"""

try:
    #execute sql command
    cursor.execute(sql)
    print ("alarm table created")
except:
    print ("cann't create alarm table")
    
sql="""INSERT INTO ALARM(DELAY)
       VALUES('0:03:00')"""
try:
    #execute sql command
    cursor.execute(sql)
    #commit your changes into database
    db.commit()
    print ("Data inserted to ALARM table")
except:
    #roleback if there is an error
    db.rollback()
    print ("Data cann't be inserted into ALARM table")

cursor.execute("DROP TABLE IF EXISTS DISPLAY")
#Create table as per requirement
sql="""CREATE TABLE DISPLAY(
       TEXTSIZE CHAR(3) NOT NULL)"""
try:
    #execute sql command
    cursor.execute(sql)
    print ("DISPLAY table created")
except:
    print ("cann't create DISPLAY table")
#INSERT VALUES
sql="""INSERT INTO DISPLAY(TEXTSIZE)
       VALUES('35')"""
try:
    #execute sql command
    cursor.execute(sql)
    #commit your changes into database
    db.commit()
    print ("Data inserted to DISPLAY table")
except:
    #roleback if there is an error
    db.rollback()
    print ("Data cann't be inserted into DISPLAY table")

cursor.execute("DROP TABLE IF EXISTS USER")
#Create table as per requirement
sql="""CREATE TABLE USER(
       ID  INT(12) NOT NULL AUTO_INCREMENT,
       USERNAME VARCHAR(20) NOT NULL,
       PASSWORD VARCHAR(20) NOT NULL,
       PRIMARY KEY (ID))"""
try:
    #execute sql command
    cursor.execute(sql)
    print ("USER table created")
except:
    print ("cann't create USER table")
sql="""INSERT INTO USER(USERNAME,
       PASSWORD)
       VALUES('admin','12345'),
             ('bps','123'),
             ('anup','9433915687')"""
try:
    #execute sql command
    cursor.execute(sql)
    #commit your changes into database
    db.commit()
    print ("Data is inserted into USER table")
except:
    #roleback if there is an error
    db.rollback()
    print ("Data cann't be inserted into USER table")

cursor.execute("DROP TABLE IF EXISTS SYSTEMDETAILS")
#Create table as per requirement
sql="""CREATE TABLE SYSTEMDETAILS(
       BAUDRATE VARCHAR(8),
       WARD VARCHAR(25),
       HOSPITAL_NAME VARCHAR(50),
       LOGO CHAR(30),
       CENTRALSERVER CHAR(16),
       ONLINESTATUS CHAR(5),
       ONLINEUSERNAME CHAR(25),
       ONLINEPASSWORD CHAR(21),
       GSMSTATUS CHAR(5),
       CBMSGSTATUS CHAR(5),
       MAXROOM CHAR(5),
       DELAY CHAR(8),
       HOST1 CHAR(16),
       HOST2 CHAR(16),
       HOST3 CHAR(16),
       ADMIN_NAME CHAR(20),
       START_AT CHAR(13),
       CLOSE_AT CHAR(13),
       DURATION CHAR(13),
       MASTERKEY CHAR(20),
       LOCALIP CHAR(16))"""
try:
    #execute sql command
    cursor.execute(sql)
    print ("SYSTEMDETAILS table created")
except:
    print ("cann't create SYSTEMDETAILS table")
sql = """INSERT INTO SYSTEMDETAILS(BAUDRATE,WARD,HOSPITAL_NAME,LOGO,CENTRALSERVER,MAXROOM,DELAY,HOST1,HOST2,HOST3,MASTERKEY,LOCALIP,ONLINESTATUS,CBMSGSTATUS,GSMSTATUS)
      VALUES('9600','Artho','BPS','/home/pi/image/logo.jpg','192.168.1.5','4','0:03:0','192.168.0.56','192.168.0.38','192.168.0.37','bpsincms01#','192.168.1.30','','','')"""
try:
    #execute sql command
    cursor.execute(sql)
    #commit your changes into database
    db.commit()
    print ("Data is inserted into SYSTEMDETAILS table")
except:
    #roleback if there is an error
    db.rollback()
    print ("Data cann't inserted into SYSTEMDETAILS table")

cursor.execute("DROP TABLE IF EXISTS RBNAME")
#Create table as per requirement
sql="""CREATE TABLE RBNAME(
       BEDID INT(5) NOT NULL,
       ROOM_NO CHAR(10) NOT NULL,
       BED_NO CHAR(10) NOT NULL,
       BED_TYPE CHAR(10),
       LAST_CON CHAR(20),
       MOBILE_NO1 CHAR(12),
       MOBILE_NO2 CHAR(12),
       MOBILE_NO3 CHAR(12))"""
try:
    #execute sql command
    cursor.execute(sql)
    print ("RBNAME table created")
except:
    print ("cann't create RBNAME table")
sql = """INSERT INTO RBNAME(BEDID,ROOM_NO,BED_NO,BED_TYPE,LAST_CON)
      VALUES(1,'A001','1','room','12:00  21/03/2019'),
            (2,'A001','2','bed','12:00  21/03/2019'),
            (3,'A002','1','room','12:00  21/03/2019'),
            (4,'A002','2','bed','12:00  21/03/2019'),
            (5,'A003','1','bed','12:00  21/03/2019'),
            (6,'A003','2','bed','12:00  21/03/2019'),
            (7,'A003','3','bed','12:00  21/03/2019'),
            (8,'A003','4','bed','12:00  21/03/2019'),
            (9,'A003','5','bed','12:00  21/03/2019'),
            (10,'A003','6','bed','12:00  21/03/2019'),
            (11,'A004','1','bed','12:00  21/03/2019'),
            (12,'A004','2','bed','12:00  21/03/2019'),
            (13,'A004','3','bed','12:00  21/03/2019'),
            (14,'A004','4','bed','12:00  21/03/2019'),
            (15,'A004','5','bed','12:00  21/03/2019'),
            (16,'A004','6','bed','12:00  21/03/2019'),
            (17,'A004','7','bed','12:00  21/03/2019'),
            (18,'A004','8','bed','12:00  21/03/2019'),
            (19,'A001','3','bed','12:00  21/03/2019'),
            (20,'A001','4','bed','12:00  21/03/2019'),
            (21,'A001','5','bed','12:00  21/03/2019'),
            (22,'A001','6','bed','12:00  21/03/2019'),
            (23,'A001','7','bed','12:00  21/03/2019'),
            (24,'A001','8','bed','12:00  21/03/2019'),
            (25,'A001','9','bed','12:00  21/03/2019'),
            (26,'A001','10','bed','12:00  21/03/2019'),
            (27,'A001','11','bed','12:00  21/03/2019'),
            (28,'A001','12','bed','12:00  21/03/2019'),
            (29,'A001','13','bed','12:00  21/03/2019'),
            (30,'A001','14','bed','12:00  21/03/2019'),
            (31,'A001','15','bed','12:00  21/03/2019'),
            (32,'A001','16','bed','12:00  21/03/2019'),
            (33,'A001','17','bed','12:00  21/03/2019'),
            (34,'A001','18','bed','12:00  21/03/2019'),
            (35,'A001','19','bed','12:00  21/03/2019'),
            (36,'A001','20','bed','12:00  21/03/2019'),
            (37,'A001','21','bed','12:00  21/03/2019'),
            (38,'A001','22','bed','12:00  21/03/2019'),
            (39,'A001','23','bed','12:00  21/03/2019'),
            (40,'A001','24','bed','12:00  21/03/2019'),
            (41,'A001','25','bed','12:00  21/03/2019'),
            (42,'A001','26','bed','12:00  21/03/2019'),
            (43,'A001','27','bed','12:00  21/03/2019'),
            (44,'A001','28','bed','12:00  21/03/2019'),
            (45,'A001','29','bed','12:00  21/03/2019'),
            (46,'A001','30','bed','12:00  21/03/2019'),
            (47,'A001','31','bed','12:00  21/03/2019'),
            (48,'A001','32','bed','12:00  21/03/2019'),
            (49,'A001','33','bed','12:00  21/03/2019'),
            (50,'A001','34','bed','12:00  21/03/2019'),
            (51,'A001','35','bed','12:00  21/03/2019'),
            (52,'A001','36','bed','12:00  21/03/2019'),
            (53,'A002','37','bed','12:00  21/03/2019'),
            (54,'A002','38','bed','12:00  21/03/2019'),
            (55,'A003','39','bed','12:00  21/03/2019'),
            (56,'A003','40','bed','12:00  21/03/2019'),
            (57,'A004','41','bed','12:00  21/03/2019'),
            (58,'A004','42','bed','12:00  21/03/2019'),
            (59,'A001','43','bed','12:00  21/03/2019'),
            (60,'A001','44','bed','12:00  21/03/2019'),
            (61,'A001','45','bed','12:00  21/03/2019'),
            (62,'A001','46','bed','12:00  21/03/2019'),
            (63,'A002','47','bed','12:00  21/03/2019'),
            (64,'A002','48','bed','12:00  21/03/2019'),
            (65,'A003','49','bed','12:00  21/03/2019'),
            (66,'A003','50','bed','12:00  21/03/2019'),
            (67,'A004','51','bed','12:00  21/03/2019'),
            (68,'A004','52','bed','12:00  21/03/2019'),
            (69,'A001','53','bed','12:00  21/03/2019'),
            (70,'A001','54','bed','12:00  21/03/2019'),
            (71,'A001','55','bed','12:00  21/03/2019'),
            (72,'A001','56','bed','12:00  21/03/2019'),
            (73,'A002','57','bed','12:00  21/03/2019'),
            (74,'A002','58','bed','12:00  21/03/2019'),
            (75,'A003','59','bed','12:00  21/03/2019'),
            (76,'A003','60','bed','12:00  21/03/2019'),
            (77,'A004','61','bed','12:00  21/03/2019'),
            (78,'A004','62','bed','12:00  21/03/2019'),
            (79,'A001','63','bed','12:00  21/03/2019'),
            (80,'A001','64','bed','12:00  21/03/2019'),
            (81,'A001','65','bed','12:00  21/03/2019'),
            (82,'A001','66','bed','12:00  21/03/2019'),
            (83,'A002','67','bed','12:00  21/03/2019'),
            (84,'A002','68','bed','12:00  21/03/2019'),
            (85,'A003','69','bed','12:00  21/03/2019'),
            (86,'A003','70','bed','12:00  21/03/2019'),
            (87,'A004','71','bed','12:00  21/03/2019'),
            (88,'A004','72','bed','12:00  21/03/2019'),
            (89,'A001','73','bed','12:00  21/03/2019'),
            (90,'A001','74','bed','12:00  21/03/2019'),
            (91,'A001','75','bed','12:00  21/03/2019'),
            (92,'A001','76','bed','12:00  21/03/2019'),
            (93,'A002','77','bed','12:00  21/03/2019'),
            (94,'A002','78','bed','12:00  21/03/2019'),
            (95,'A003','79','bed','12:00  21/03/2019'),
            (96,'A003','80','bed','12:00  21/03/2019'),
            (97,'A004','81','bed','12:00  21/03/2019'),
            (98,'A004','82','bed','12:00  21/03/2019'),
            (99,'A001','83','bed','12:00  21/03/2019'),
            (100,'A001','84','bed','12:00  21/03/2019')"""
try:
    #execute sql command
    cursor.execute(sql)
    #commit your changes into database
    db.commit()
    print ("Data is inserted into RBNAME table")
except:
    #roleback if there is an error
    db.rollback()
    print ("Data cann't inserted into RBNAME table")
    
#disconnect from server
db.close()

