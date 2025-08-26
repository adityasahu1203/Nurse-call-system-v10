#!/usr/bin/env python3
import mariadb
from mariadb import ConnectionPool

# Define the database configuration
db_config = {
    'user': 'Admin',
    'password': 'iNCMS-R9@2024',
    'host': 'localhost',
    'port': 3306,
    'autocommit': True
}

# Initialize a connection pool
try:
    pool = ConnectionPool(
        pool_name="mypool",
        pool_size=10,  # Adjust based on your needs
        **db_config
    )
    print("MariaDB connection pool created successfully.")
except mariadb.Error as e:
    print(f"Error creating MariaDB connection pool: {e}")
    exit(1)

# Create a connection and setup the database
try:
    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS NursecallDB;")  # Replace 'YourDatabaseName' with the actual name
        print("Database created or already exists.")

        # Switch to the new database
        cursor.execute("USE NursecallDB;")

        cursor.execute("DROP TABLE IF EXISTS CALLRECORD")

        # Create table as per requirement
        sql = """CREATE TABLE CALLRECORD (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            DATE CHAR(12) ,
            ROOM_NO VARCHAR(20) NOT NULL,
            BED_NO VARCHAR(20) NOT NULL,
            WARD VARCHAR(35),
            STATUS CHAR(3),
            CALLTYPE VARCHAR(10),
            CALL_AT DATETIME,
            SERVED_AT DATETIME,
            TIME_TAKEN TIME
            )"""
        try:
            cursor.execute(sql)
            print("CALLRECORD table created")
        except:
            print("can't create CALLRECORD table")

        cursor.execute("DROP TABLE IF EXISTS USER")
        # Create table as per requirement
        sql = """CREATE TABLE USER(
               ID  INT(12) NOT NULL AUTO_INCREMENT,
               USERNAME VARCHAR(40) NOT NULL,
               PASSWORD VARCHAR(40) NOT NULL,
               IS_ADMIN TINYINT(1) DEFAULT 0,
               PRIMARY KEY (ID))"""
        try:
            # execute sql command
            cursor.execute(sql)
            print("USER table created")
        except:
            print("cann't create USER table")
        sql = """INSERT INTO USER(USERNAME,
               PASSWORD,IS_ADMIN)
               VALUES('Admin','Manroot@2024',1),
                     ('Anup','Anup@2024',1), 
                     ('Guest','incms-r9@2024',1)"""
        try:
            # execute sql command
            cursor.execute(sql)
            print("Data is inserted into USER table")
        except:
            print("Data cann't be inserted into USER table")

        cursor.execute("DROP TABLE IF EXISTS SYSTEMDETAILS")
        # Create table as per requirement
        sql = """CREATE TABLE SYSTEMDETAILS(
               BAUDRATE VARCHAR(8),
               WARD VARCHAR(35),
               HOSPITAL_NAME VARCHAR(50),
               LOGO CHAR(30),
               CENTRALSERVER CHAR(16),
               ONLINESTATUS CHAR(5),
               ONLINEUSERNAME CHAR(25),
               ONLINEPASSWORD CHAR(21),
               GSMSTATUS CHAR(5),
               CBMSGSTATUS CHAR(5),
               MAXROOM CHAR(5),
               DELAY TIME,
               HOST1 CHAR(16),
               HOST2 CHAR(16),
               HOST3 CHAR(16),
               ADMIN_NAME CHAR(20),
               START_AT CHAR(13),
               CLOSE_AT CHAR(13),
               DURATION CHAR(13),
               MASTERKEY CHAR(20),
               LOCALIP CHAR(16),
               RECORD_KEEP_DAYS INT(5) DEFAULT 30
               )"""
        try:
            # execute sql command
            cursor.execute(sql)
            print("SYSTEMDETAILS table created")
        except:
            print("cann't create SYSTEMDETAILS table")
        sql = """INSERT INTO SYSTEMDETAILS(BAUDRATE,WARD,HOSPITAL_NAME,LOGO,CENTRALSERVER,MAXROOM,DELAY,HOST1,HOST2,HOST3,MASTERKEY,LOCALIP,ONLINESTATUS,CBMSGSTATUS,GSMSTATUS)
              VALUES('9600','General','MultiSpecility Hospital','/home/pi/image/logo.jpg','192.168.1.5','30','0:03:0','192.168.0.56','192.168.0.38','192.168.0.37','bpsincms01#','192.168.10.188','','','')"""
        try:
            # execute sql command
            cursor.execute(sql)
            print("Data is inserted into SYSTEMDETAILS table")
        except:
            print("Data cann't inserted into SYSTEMDETAILS table")

        cursor.execute("DROP TABLE IF EXISTS BED_DETAILS")
        # Create table as per requirement
        sql = """CREATE TABLE BED_DETAILS(
               BEDID INT(5) NOT NULL,
               IP_ADDRESS CHAR(20),
               ROOM_NO CHAR(10) NOT NULL,
               BED_NO CHAR(10) NOT NULL,
               BED_TYPE CHAR(10),
               LAST_CON CHAR(20),
               MOBILE_NO1 CHAR(12),
               MOBILE_NO2 CHAR(12),
               MOBILE_NO3 CHAR(12))"""
        try:
            # execute sql command
            cursor.execute(sql)
            print("BED_DETAILS table created")
        except:
            print("cann't create BED_DETAILS table")

except mariadb.Error as e:
    print(f"Error during database setup: {e}")
finally:
    cursor.close()

