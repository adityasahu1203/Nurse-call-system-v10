from flask import Flask, render_template, jsonify, Response, request, redirect, url_for, session, send_file
#import mysql.connector
#from mysql.connector.pooling import MySQLConnectionPool
import mariadb
import threading
import socket
import time
import json
import webbrowser
import pandas as pd
import io
from threading import Timer
from functools import wraps
import urllib.parse
from datetime import datetime, timedelta
import logging
import queue
import os

app = Flask(__name__)
app.secret_key = 'cf7106d2db5944a120e9bac987c39f04'

broadcast_queue = queue.Queue()
acknowledge_lock = threading.Lock()  # Add this globally
clients_lock = threading.Lock()

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'Admin',
    'password': 'iNCMS-R9@2024',
    'database': 'NursecallDB'
}

#pool = MySQLConnectionPool(pool_name="mypool", pool_size=10, **db_config)
pool = mariadb.ConnectionPool(pool_name="mypool", pool_size=10, **db_config)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Network Configuration
SERVER_IP = '192.168.0.3'  # None # Server Ip will receive from database
SERVER_PORT = 6903
IDLE_TIMEOUT = 30 * 60  # 30 minutes in seconds
RECORD_KEEP_DAYS = 0
ward = None
DELAY = None


def get_connection():
    return pool.get_connection()

def set_server_ip(ip_address):
    """
    Configures the Raspberry Pi's static IP address to the specified IP.
    """
    try:
        # Backup the current dhcpcd.conf file
        os.system("sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak")

        # Update the dhcpcd.conf file to set a static IP
        with open("/etc/dhcpcd.conf", "r") as file:
            lines = file.readlines()

        # Remove existing static IP settings
        with open("/etc/dhcpcd.conf", "w") as file:
            static_block = False
            for line in lines:
                if line.startswith("interface eth0") or line.startswith("static ip_address"):
                    static_block = True
                if static_block and line.strip() == "":
                    static_block = False
                    continue
                if not static_block:
                    file.write(line)

            # Append the new static IP settings
            file.write("\ninterface eth0\n")
            file.write(f"static ip_address={ip_address}/24\n")
            file.write("static routers=192.168.1.1\n")  # Adjust as needed
            file.write("static domain_name_servers=8.8.8.8 8.8.4.4\n")  # Adjust as needed

        # Restart the dhcpcd service to apply the changes
        os.system("sudo systemctl restart dhcpcd")

        logger.info(f"Server static IP set to {ip_address}.")

    except Exception as e:
        logger.error(f"Error setting Server IP address: {e}")

def load_system_info():
    global ward, DELAY, SERVER_IP, RECORD_KEEP_DAYS
    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch system details
                cursor.execute("SELECT WARD, DELAY, LOCALIP, RECORD_KEEP_DAYS FROM SYSTEMDETAILS LIMIT 1")
                result = cursor.fetchone()

                if result:
                    ward = result['WARD']
                    delay_time = result['DELAY']
                    SERVER_IP = result['LOCALIP']
                    RECORD_KEEP_DAYS = result.get('RECORD_KEEP_DAYS', 30)  # Default to 30 days if not set

                    # Convert DELAY to timedelta
                    if isinstance(delay_time, str):
                        h, m, s = map(int, delay_time.split(":"))
                        DELAY = timedelta(hours=h, minutes=m, seconds=s)
                    else:
                        DELAY = timedelta(seconds=delay_time.total_seconds())

                    # Log loaded system info
                    logger.info(
                        f"Loaded system info: WARD={ward}, DELAY={DELAY}, SERVER_IP={SERVER_IP}, RECORD_KEEP_DAYS={RECORD_KEEP_DAYS}")
                else:
                    # Default values if no SYSTEMDETAILS found
                    ward = "DefaultWard"
                    DELAY = timedelta(hours=0, minutes=3, seconds=0)
                    SERVER_IP = "127.0.0.1"
                    RECORD_KEEP_DAYS = 30
                    logger.warning("No SYSTEMDETAILS found in the database. Using default values.")

                # Delete old call records
                if RECORD_KEEP_DAYS > 0:
                    delete_query = """
                        DELETE FROM CALLRECORD 
                        WHERE CALL_AT < NOW() - INTERVAL %s DAY
                    """
                    cursor.execute(delete_query, (RECORD_KEEP_DAYS,))
                    conn.commit()
                    logger.info(f"Deleted call records older than {RECORD_KEEP_DAYS} days.")

                # Replace Raspberry Pi's IP with the IP from SYSTEMDETAILS
                system_ip = socket.gethostbyname(socket.gethostname())  # Get the Pi's current IP
                logger.info(f"Current IP of the system {system_ip}")
                if SERVER_IP != system_ip:
                    logger.info(f"Currently disabled")
                    #set_server_ip(SERVER_IP)

    except mariadb.Error as e:
        logger.error(f"Database error while loading system info: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while loading system info: {e}")

# Call this function at program startup to initialize WARD, DELAY, and LOCALIP
load_system_info()

def convert_timedelta_to_string(records):
    for record in records:
        if 'TIME_TAKEN' in record and record['TIME_TAKEN'] is not None:
            # Convert timedelta to a string format HH:MM:SS
            record['TIME_TAKEN'] = str(record['TIME_TAKEN'])
        if 'CALL_AT' in record and record['CALL_AT'] is not None:
            record['CALL_AT'] = record['CALL_AT'].strftime('%Y-%m-%d %H:%M:%S')
        if 'SERVED_AT' in record and record['SERVED_AT'] is not None:
            record['SERVED_AT'] = record['SERVED_AT'].strftime('%Y-%m-%d %H:%M:%S')
    return records


# Store client connections
clients = []


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return render_template('index.html')


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        result = None  # Initialize result to avoid UnboundLocalError
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # logger.info(f"Login Attempt- User Name:", {username}, "Password:", {password})
                cursor.execute("SELECT * FROM USER WHERE USERNAME = %s AND PASSWORD = %s", (username, password))
                result = cursor.fetchone()
                # logger.info(result)
                if result:
                    session['user_id'] = result['ID']
                    session['username'] = result['USERNAME']
                    session['is_admin'] = result['IS_ADMIN']  # Store admin status
                    return jsonify({'status': 'success', 'message': 'Login successful'}), 200
                else:
                    return jsonify({'status': 'fail', 'message': 'Invalid username or password'}), 401

    except mariadb.Error as err:
        logger.error(f"Login Mysql Error: {err}")
        return jsonify({'error': f"Database error: {str(err)}"}), 500

    except Exception as e:
        logger.error(f"Login Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/home')
@login_required
def home():
    username = session.get('username', 'Guest')  # Fallback to 'Guest' if not logged in
    return render_template('home.html', username=username)


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/status')
@login_required
def status():
    username = session.get('username', 'Guest')  # Fallback to 'Guest' if not logged in
    return render_template('status.html', username=username)

@app.route('/report')
@login_required
def report():
    wards = []  # Initialize to avoid UnboundLocalError in case of exception
    call_types = []

    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch unique wards
                try:
                    cursor.execute("SELECT DISTINCT WARD FROM CALLRECORD WHERE WARD IS NOT NULL")
                    wards = [row['WARD'] for row in cursor.fetchall()]
                except mariadb.Error as e:
                    logger.error(f"Database error while fetching wards: {e}")
                    wards = []  # Ensure wards is empty on failure

                # Fetch unique call types
                try:
                    cursor.execute("SELECT DISTINCT CALLTYPE FROM CALLRECORD WHERE CALLTYPE IS NOT NULL")
                    call_types = [row['CALLTYPE'] for row in cursor.fetchall()]
                except mariadb.Error as e:
                    logger.error(f"Database error while fetching call types: {e}")
                    call_types = []  # Ensure call_types is empty on failure
    except mariadb.Error as e:
        logger.error(f"Database connection error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in report function: {e}")

    username = session.get('username', 'Guest')  # Fallback to 'Guest' if not logged in
    return render_template('report.html', username=username, wards=wards, call_types=call_types)

@app.route('/about')
@login_required
def about():
    username = session.get('username', 'Guest')  # Fallback to 'Guest' if not logged in
    return render_template('about.html', username=username)


@app.route('/Settings')
@login_required
def settings():
    try:
        system_detail = None
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch SYSTEMDETAILS data
                cursor.execute(
                    "SELECT HOSPITAL_NAME, WARD, BAUDRATE, RECORD_KEEP_DAYS, CENTRALSERVER, MAXROOM, DELAY, LOCALIP FROM "
                    "SYSTEMDETAILS")
                system_detail = [
                    {
                        "HOSPITAL_NAME": row['HOSPITAL_NAME'] or "",
                        "WARD": row['WARD'] or "",
                        "BAUDRATE": row['BAUDRATE'] or "",
                        "RECORD_KEEP_DAYS": row['RECORD_KEEP_DAYS'] or "",
                        "CENTRALSERVER": row['CENTRALSERVER'] or "",
                        "MAXROOM": row['MAXROOM'] or "",
                        "DELAY": row['DELAY'] or "",
                        "LOCALIP": row['LOCALIP'] or ""
                    }
                    for row in cursor.fetchall()
                ]

                # Fetch BED_DETAILS data with additional debug information
                cursor.execute("SELECT BEDID, IP_ADDRESS, ROOM_NO, BED_NO, BED_TYPE FROM BED_DETAILS")
                bed_details = [
                    {
                        "BEDID": row['BEDID'],
                        "IP_ADDRESS": row['IP_ADDRESS'] or "",  # default to empty string if None
                        "ROOM_NO": row['ROOM_NO'] or "",
                        "BED_NO": row['BED_NO'] or "",
                        "BED_TYPE": row['BED_TYPE'] or ""
                    }
                    for row in cursor.fetchall()
                ]
    except Exception as e:
        logger.error(f"Settings Error: {e}")

    username = session.get('username', 'Guest')  # Fallback to 'Guest' if not logged in
    return render_template('Settings.html', system_detail=system_detail, bed_details=bed_details, username=username)


@app.route('/active-calls')
def get_active_calls():
    global DELAY
    query_select = """
    SELECT WARD, ROOM_NO, BED_NO, CALLTYPE, CALL_AT, status 
    FROM CALLRECORD 
    WHERE STATUS IN ('s', 'S', 'a', 'A')
    ORDER BY CASE 
                WHEN LOWER(REPLACE(CALLTYPE, ' ', '')) = 'codeblue' THEN 1
                WHEN LOWER(CALLTYPE) = 'emergency' THEN 2
                WHEN LOWER(CALLTYPE) = 'normal' THEN 3
                ELSE 4
            END ASC, CALL_AT ASC
    """

    query_update = """
    UPDATE CALLRECORD 
    SET CALLTYPE = 'Emergency', STATUS = 'S'
    WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN ('s', 'S', 'a', 'A')
    """
    calls = []  # Ensure calls is initialized to avoid UnboundLocalError

    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch all active calls
                cursor.execute(query_select)
                calls = cursor.fetchall()
                current_time = datetime.now()

                # Iterate over the calls to check for updates
                for call in calls:
                    call_type = call['CALLTYPE'].lower().strip()
                    if call_type == 'normal':
                        call_at = call['CALL_AT']

                        # Calculate the delay in seconds
                        delay_in_seconds = (current_time - call_at).total_seconds()
                        # logger.info(f"Delay for Room {call['ROOM_NO']} Bed {call['BED_NO']}: {delay_in_seconds}s")
                        # Check if the delay exceeds the defined DELAY (assume DELAY is in seconds)
                        if DELAY is None:
                            logger.warning("DELAY not initialized. Using default value.")
                            DELAY = timedelta(minutes=3)
                        if delay_in_seconds > DELAY.total_seconds():
                            try:
                                # Perform database update
                                cursor.execute(query_update, (call['ROOM_NO'], call['BED_NO'], ward))
                                conn.commit()

                                # Update local data for consistency in the response
                                call['CALLTYPE'] = 'Emergency'
                                call['status'] = 'S'
                            except mariadb.Error as e:
                                logger.error(f"Database error during update: {e}")

    except mariadb.Error as e:
        logger.error(f"Database error while fetching active calls: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_active_calls: {e}")

    return jsonify(calls)


@app.route('/latest-event')
def get_latest_event():
    query = """
    SELECT ROOM_NO, BED_NO, CALLTYPE, CALL_AT 
    FROM CALLRECORD 
    ORDER BY CALL_AT DESC LIMIT 1
    """
    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                latest_event = cursor.fetchone()
    except Exception as e:
        logger.warning(f"Get latest event error: {e}")

    return jsonify(latest_event)


@app.route('/stream-calls')
def stream_calls():
    def generate():
        error_count = 0
        while True:
            if error_count > 5:  # Max retries
                logger.error("Maximum retries reached. Stopping stream.")
                break
            try:
                with pool.get_connection() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        query = """
                        SELECT ROOM_NO, BED_NO, CALLTYPE, CALL_AT 
                        FROM CALLRECORD 
                        ORDER BY CALL_AT DESC LIMIT 1
                        """
                        cursor.execute(query)
                        latest_event = cursor.fetchone()

                        if latest_event:
                            latest_event["CALL_AT"] = latest_event["CALL_AT"].strftime("%Y-%m-%d %H:%M:%S")
                            yield f"data: {json.dumps(latest_event)}\n\n"
                time.sleep(3)
                error_count = 0
            except Exception as e:
                error_count += 1
                logger.warning(f"Error streaming calls: {e}")
                if error_count > 5:  # Stop after 5 consecutive errors
                    break

    return Response(generate(), content_type='text/event-stream')


@app.route('/acknowledge-call', methods=['POST'])
def acknowledge_call():
    if not acknowledge_lock.acquire(blocking=False):  # Prevent simultaneous clicks
        return jsonify({'error': 'Acknowledgment is already in progress'}), 400

    try:
        # Ensure the broadcast queue is empty
        while not broadcast_queue.empty():
            try:
                broadcast_queue.get_nowait()
            except queue.Empty:
                break
        data = request.get_json()
        room_no = data.get('ROOM_NO')
        bed_no = data.get('BED_NO')
        call_at = data.get('CALL_AT')
        call_type = data.get('CALL_TYPE')
        ward = data.get('WARD')

        if not all([ward, room_no, bed_no, call_at, call_type]):
            return jsonify({'error': 'Missing parameters in request data'}), 400

        # Parse and format CALL_AT
        try:
            call_at_datetime = datetime.strptime(call_at, "%a, %d %b %Y %H:%M:%S %Z")
            call_at_formatted = call_at_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({'error': f"Invalid datetime format for CALL_AT: {call_at}"}), 400

        # Broadcast acknowledgment message
        ack_message = f"ACK#{room_no}#{bed_no}#{call_type}#*"
        ack_received = broadcast(ack_message, wait_for_ack=True)

        if not ack_received:
            return jsonify({'error': 'No acknowledgment received from beds'}), 400

        # Update the database
        query = """
                UPDATE CALLRECORD
                SET STATUS = 'A'
                WHERE WARD = %s AND ROOM_NO = %s AND BED_NO = %s AND CALLTYPE = %s AND CALL_AT = %s
                  AND STATUS IN ('s', 'S')
            """
        try:
            with pool.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (ward, room_no, bed_no, call_type, call_at_formatted))
                    if cursor.rowcount > 0:
                        conn.commit()
                        return jsonify({'message': 'Call acknowledged successfully'})
                    else:
                        return jsonify({'error': 'Call not found or already acknowledged'}), 404
        except mariadb.Error as e:
            logger.error(f"Database error during acknowledgment update: {e}")
            return jsonify({'error': 'Database error occurred'}), 500

    except Exception as e:
        logger.error(f"Error acknowledging call: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        acknowledge_lock.release()  # Ensure the lock is released

# Update SYSTEMDETAILS records
@app.route('/update_systemdetails', methods=['POST'])
@login_required
@admin_required
def update_systemdetails():
    data = request.json['updatedData']
    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for record in data:
                    cursor.execute("""UPDATE SYSTEMDETAILS SET HOSPITAL_NAME = %s, WARD = %s, BAUDRATE = %s, RECORD_KEEP_DAYS 
                    = %s, CENTRALSERVER = %s, MAXROOM = %s, DELAY = %s, LOCALIP = %s """,
                                   (
                                       record['hospital_name'],
                                       record['ward'],
                                       record['baudrate'],
                                       record['keep_record_days'],
                                       record['centralserver'],
                                       record['maxroom'],
                                       record['delay'],
                                       record['localip']
                                   ))
            conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Error updating SYSTEMDETAILS data: {e}")
        return jsonify({"success": False, "error": str(e)})


# Update BED_DETAILS records
@app.route('/update_bed_details', methods=['POST'])
@login_required
@admin_required
def update_bed_details():
    data = request.json['updatedBedDetails']
    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for record in data:
                    cursor.execute("""
                        UPDATE bed_details
                        SET IP_ADDRESS = %s, ROOM_NO = %s, BED_NO = %s, BED_TYPE = %s
                        WHERE BEDID = %s
                    """, (
                        record['ip_address'],
                        record['room_no'],
                        record['bed_no'],
                        record['bed_type'],
                        record['bed_id']
                    ))
            conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Error updating BED_DETAILS data: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/search_logs', methods=['GET'])
@login_required
def search_logs():
    # Get parameters from request, defaulting to None if not provided
    ward = request.args.get('ward') or None
    call_type = request.args.get('callType') or None
    from_date = request.args.get('fromDateTime') or None
    to_date = request.args.get('toDateTime') or None

    # SQL query with optional parameters
    query = """
    SELECT ROOM_NO, BED_NO, WARD, STATUS, CALLTYPE, CALL_AT, SERVED_AT, TIME_TAKEN 
    FROM CALLRECORD 
    WHERE (%s IS NULL OR WARD = %s) 
      AND (%s IS NULL OR CALLTYPE = %s) 
      AND (%s IS NULL OR CALL_AT >= %s) 
      AND (%s IS NULL OR CALL_AT <= %s)
    """
    params = (ward, ward, call_type, call_type, from_date, from_date, to_date, to_date)

    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                records = cursor.fetchall()

        # Convert `timedelta` and `datetime` fields to strings
        for record in records:
            if 'TIME_TAKEN' in record and isinstance(record['TIME_TAKEN'], timedelta):
                record['TIME_TAKEN'] = str(record['TIME_TAKEN'])  # Convert to HH:MM:SS
            if 'CALL_AT' in record and isinstance(record['CALL_AT'], datetime):
                record['CALL_AT'] = record['CALL_AT'].strftime('%Y-%m-%d %H:%M:%S')
            if 'SERVED_AT' in record and isinstance(record['SERVED_AT'], datetime):
                record['SERVED_AT'] = record['SERVED_AT'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(records)

    except Exception as e:
        logger.error(f"Search Logs Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download_excel')
@login_required
def download_excel():
    ward = request.args.get('ward') or None
    call_type = request.args.get('callType') or None
    from_date = request.args.get('fromDateTime') or None
    to_date = request.args.get('toDateTime') or None

    query = """
        SELECT ROOM_NO, BED_NO, WARD, STATUS, CALLTYPE, CALL_AT, SERVED_AT, TIME_TAKEN 
        FROM CALLRECORD WHERE 
        (%s IS NULL OR WARD = %s) AND 
        (%s IS NULL OR CALLTYPE = %s) AND
        (%s IS NULL OR CALL_AT >= %s) AND 
        (%s IS NULL OR CALL_AT <= %s)
        """
    params = (
        ward, ward,
        call_type, call_type,
        from_date if from_date else None, from_date if from_date else None,
        to_date if to_date else None, to_date if to_date else None
    )

    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                records = cursor.fetchall()
    except Exception as e:
        logger.error(f"Download excel error: {e}")

    if not records:
        return "No records found.", 404

    # Convert timedelta fields to string format for Excel export
    records = convert_timedelta_to_string(records)

    df = pd.DataFrame(records)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Logs")

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="logs.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route('/next_bed_id')
@login_required
def next_bed_id():
    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT COALESCE(MAX(BEDID), 0) + 1 AS next_bed_id FROM BED_DETAILS")
                result = cursor.fetchone()
                next_bed_id = result['next_bed_id'] if result else 1

                return jsonify({"next_bed_id": next_bed_id})

    except Exception as e:
        logger.error(f"Error fetching next BEDID: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/add_bed', methods=['POST'])
@login_required
@admin_required
def add_bed():
    data = request.json
    is_editing = data.get("is_editing", False)  # Check if editing

    try:
        # Validate input data
        required_fields = ["bed_id", "ip_address", "room_no", "bed_no", "bed_type"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Check if Room No and Bed No already exist
                cursor.execute("""
                    SELECT COUNT(*) AS count FROM BED_DETAILS 
                    WHERE ROOM_NO = %s AND BED_NO = %s AND BEDID != %s
                """, (data['room_no'], data['bed_no'], data['bed_id']))
                result = cursor.fetchone()

                if result['count'] > 0:
                    return jsonify(
                        {"success": False, "error": "Bed already registered with this Room and Bed Number."}), 409

                if is_editing:
                    # Update existing bed
                    cursor.execute("""
                        UPDATE BED_DETAILS 
                        SET IP_ADDRESS = %s, ROOM_NO = %s, BED_NO = %s, BED_TYPE = %s 
                        WHERE BEDID = %s
                    """, (data['ip_address'], data['room_no'], data['bed_no'], data['bed_type'], data['bed_id']))
                else:
                    # Insert new Bed
                    cursor.execute("""
                        INSERT INTO BED_DETAILS (BEDID, IP_ADDRESS, ROOM_NO, BED_NO, BED_TYPE)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (int(data['bed_id']), data['ip_address'], data['room_no'], data['bed_no'], data['bed_type']))

            # Commit the changes
            conn.commit()

        return jsonify({"success": True, "message": "Bed added/updated successfully."})

    except mariadb.Error as err:
        logger.error(f"Database Error adding/updating bed: {err}")
        return jsonify({"success": False, "error": str(err)}), 500

    except Exception as e:
        logger.warning(f"Error adding/updating bed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/delete_beds', methods=['POST'])
@login_required
@admin_required
def delete_beds():
    data = request.json
    bed_ids = data.get('bed_ids', [])

    try:
        with pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.executemany("DELETE FROM BED_DETAILS WHERE BEDID = %s", [(bed_id,) for bed_id in bed_ids])
            conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        logger.warning(f"Error deleting beds:{e}")
        return jsonify({"success": False, "error": str(e)})


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


def handle_client(client_socket, address):
    logger.info(f"New connection from {address}")
    with clients_lock:
        clients.append(client_socket)

    client_socket.settimeout(IDLE_TIMEOUT)
    last_active_time = time.time()

    try:
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    logger.info(f"No data received from {address}. Closing connection.")
                    break

                # Decode and parse the received data as a full HTTP request
                request_lines = data.decode().splitlines()
                if not request_lines:
                    logger.info(f"Malformed data from {address}: {data}")
                    break

                # Process the first line of the HTTP request (e.g., GET /?msg=... HTTP/1.1)
                request_line = request_lines[0]
                parsed_url = urllib.parse.urlparse(request_line.split()[1])
                query_params = urllib.parse.parse_qs(parsed_url.query)

                # Extract the 'msg' parameter
                if 'msg' in query_params:
                    packet_data = query_params['msg'][0]
                    if packet_data.startswith("$BROADCAST#ACK#") or packet_data.startswith("$BROADCAST#NACK#"):
                        logger.info(f"Broadcast response from {address}: {packet_data}")
                        broadcast_queue.put(packet_data)  # Pass response to the broadcast queue
                        continue
                    else:
                        logger.info(f"Received packet data from {address}: {packet_data}")
                    # Use a database connection from the pool to process the packet
                    with pool.get_connection() as conn:
                        response_text = handle_packet(packet_data, conn)

                    # Create the HTTP response
                    full_response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(response_text)}\r\n"
                        "Connection: close\r\n\r\n"
                        f"{response_text}"
                    )
                    client_socket.sendall(full_response.encode())
                    last_active_time = time.time()

            except socket.timeout:
                if time.time() - last_active_time > IDLE_TIMEOUT:
                    logger.warning(f"Disconnecting {address} due to inactivity.")
                    break
            except Exception as e:
                logger.warning(f"Error while handling data from {address}: {e}")
                break

    finally:
        # Clean up the client connection
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        logger.warning(f"Disconnected from {address}")


def handle_packet(packet_data, conn):
    try:
        packet_parts = packet_data.strip('$*').split('#')
        if len(packet_parts) < 4:
            return "Status: failure\nError: Invalid packet format\n"

        address, room_no, bed_no, packet_type = packet_parts[:4]
        #logger.info(f"Handling Packet: Address={address}, Room={room_no}, Bed={bed_no}, Type={packet_type}")
        #logger.info(f"Pool connections in use: {pool._cnx_queue.qsize()} / {pool.pool_size}")

        try:
            with conn.cursor(dictionary=True) as cursor:
                if packet_type == 'C':  # Normal Call
                    # Check if there is already an active call
                    cursor.execute("""
                        SELECT * FROM CALLRECORD WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN 
                        ('S', 'A', 's', 'a') 
                    """, (room_no, bed_no, ward))
                    existing_call = cursor.fetchone()
                    if not existing_call:  # If no active call, insert a new record
                        cursor.execute("""
                             INSERT INTO CALLRECORD (ROOM_NO, BED_NO, WARD, STATUS, CALLTYPE, CALL_AT)
                             VALUES (%s, %s, %s, 'S', 'Normal', %s)
                         """, (room_no, bed_no, ward, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                        return f"Status: success\nReceived message: {packet_data}\nReply message: Normal call processed successfully.\n"
                    else:
                        return f"Status: failure\nReceived message: {packet_data}\nReply message: Normal call already active for this bed.\n"

                elif packet_type == 'B':  # Code Blue
                    # Check if there is an active normal call for this bed
                    cursor.execute("""
                        SELECT * FROM CALLRECORD WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN ('S', 'A', 's', 'a') 
                        AND CALLTYPE IN ('Normal','Emergency')
                    """, (room_no, bed_no, ward))
                    existing_normal_call = cursor.fetchone()

                    if existing_normal_call:  # If a normal call exists, upgrade to Code Blue
                        cursor.execute("""
                            UPDATE CALLRECORD SET CALLTYPE = 'Code Blue' WHERE ROOM_NO = %s AND BED_NO = %s AND STATUS = 'S' AND WARD = %s
                         """, (room_no, bed_no, ward))
                        conn.commit()
                        return f"Status: success\nReceived message: {packet_data}\nReply message: Call upgraded to Code Blue.\n"
                    else:
                        return f"Status: failure\nReceived message: {packet_data}\nReply message: No pending call to upgrade to Code Blue.\n"

                elif packet_type == 'E':  # Emergency Call
                    # Check if there is already an active call
                    cursor.execute("""
                        SELECT * FROM CALLRECORD WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN 
                        ('S', 'A', 's', 'a') 
                    """, (room_no, bed_no, ward))
                    existing_call = cursor.fetchone()
                    if not existing_call:  # If no active call, insert a new record
                        cursor.execute("""
                             INSERT INTO CALLRECORD (ROOM_NO, BED_NO, WARD, STATUS, CALLTYPE, CALL_AT)
                             VALUES (%s, %s, %s, 'S', 'Emergency', %s)
                         """, (room_no, bed_no, ward, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                        return f"Status: success\nReceived message: {packet_data}\nReply message: Emergency call processed successfully.\n"
                    else:
                        return f"Status: failure\nReceived message: {packet_data}\nReply message: Emergency call already active for this bed.\n"

                elif packet_type == 'R':  # Reset
                    # Retrieve CALL_AT time for the specified room and bed where the status is 'S'
                    cursor.execute("""
                        SELECT CALL_AT FROM CALLRECORD 
                        WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN ('S', 'A', 's', 'a')
                    """, (room_no, bed_no, ward))
                    call_record = cursor.fetchone()
                    #logger.info(f"Reset detected: {call_record}")

                    if call_record and call_record.get('CALL_AT'):
                        call_at_time = call_record['CALL_AT']
                        served_at_time = datetime.now()
                        #logger.info(f"Reset CALL_AT {call_at_time}")

                        # Ensure CALL_AT is a datetime object
                        if isinstance(call_at_time, str):
                            call_at_time = datetime.strptime(call_at_time, "%Y-%m-%d %H:%M:%S")

                        # Calculate time taken
                        time_taken = served_at_time - call_at_time
                        # Format time taken to HH:MM:SS
                        days = time_taken.days
                        seconds = time_taken.seconds
                        hours, remainder = divmod(seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        time_taken_str = f"{days} {hours:02}:{minutes:02}:{seconds:02}" if days > 0 else f"{hours:02}:{minutes:02}:{seconds:02}"
                        #logger.info(f"Reset duration: {time_taken_str}")

                        cursor.execute("""
                            UPDATE CALLRECORD 
                            SET STATUS = 'R', SERVED_AT = %s, TIME_TAKEN = %s
                            WHERE ROOM_NO = %s AND BED_NO = %s AND WARD = %s AND STATUS IN ('S', 'A', 's', 'a')
                        """, (served_at_time.strftime('%Y-%m-%d %H:%M:%S'), time_taken_str, room_no, bed_no, ward))
                        conn.commit()
                        return f"Status: success\nReceived message: {packet_data}\nReply message: Call reset successfully.\n"
                    else:
                        return f"Status: success\nReceived message: {packet_data}\nReply message: No Pending Call to Reset.\n"

                elif packet_type == 'L':  # Live Check
                    return "Status: success\nMessage: Server is alive.\n"

                else:
                    return "Status: failure\nError: Unknown packet type\n"

        except mariadb.Error as db_err:
            logger.error(f"Database error: {db_err}")
            return f"Status: failure\nError: {db_err}\n"

    except Exception as e:
        logger.warning(f"Error processing packet: {e}")
        return "Status: failure\nError: Server error while processing packet\n"


def broadcast(message, wait_for_ack=False, timeout=10):
    """
    Broadcast a message to all clients and optionally wait for an acknowledgment.

    :param message: The message to broadcast.
    :param wait_for_ack: Whether to wait for acknowledgment.
    :param timeout: Timeout for receiving acknowledgment.
    :return: True if acknowledgment received, False otherwise.
    """
    #logger.info(f"Broadcasting message to all clients: {message}")
    ack_received = False

    if not clients:
        logger.warning("No clients connected for broadcast.")
        return False

    for client in clients[:]:
        try:
            tagged_message = f"$BROADCAST#{message}"
            client.sendall(tagged_message.encode())
            logger.info(f"Broadcast Message sent to client: {client.getpeername()}")

            if wait_for_ack:
                try:
                    # Wait for acknowledgment in the queue
                    response = broadcast_queue.get(timeout=timeout)
                    if response == "$BROADCAST#ACK#*":
                        ack_received = True
                        logger.info(f"Broadcast Acknowledgement received")
                        break
                except queue.Empty:
                    logger.info(f"No acknowledgment received within timeout for {client.getpeername()}")
        except (socket.timeout, socket.error) as e:
            logger.warning(f"Error communicating with client: {e}")
            if client in clients:
                clients.remove(client)
            client.close()

    return ack_received


# Main server function to accept incoming connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()  # Start listening for incoming connections
    logger.info(f"Listening for client connections on {SERVER_IP}:{SERVER_PORT}...")

    while True:
        try:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.start()
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")
            break

# Run the server in a thread
server_thread = threading.Thread(target=start_server)
server_thread.start()

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
