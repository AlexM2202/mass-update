#! /usr/bin/python3

#Alex Marquardt 
#3-11-24
#PBX-Auto-Updater

import logging
import os
import threading
import csv
import json
import smtplib
import configparser
import paramiko #pip
import pandas as pd #pip
from time import perf_counter
from datetime import datetime
from multiprocessing import Queue
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO

script_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = f"{script_dir}/output"

#Log File Info
fp = open(f"{output_dir}/log.log", 'w')
logging.basicConfig(filename=f"{output_dir}/log.log", level=logging.INFO, format= "%(asctime)s %(message)s", filemode='a')

#open csv
sheetOpened = open(f"{output_dir}/emailTable.csv", "w")
sheet = csv.writer(sheetOpened)
sheet.writerow(['Name', 'Address', 'Run Time (sec)', 'Errors'])

#Run a desired command. command needs to be of type string
def __runCommand(command: str, client, outF) -> tuple:
    """Run a command on a machine through ssh (paramiko).
    
    Args: Command: str, client, output file
    Returns: tuple[error, stderr]
    """
    logging.info(f"Running command {command}")
    stdin, stdout, stderr = client.exec_command(command)
    stdoutput = [line for line in stdout]
    error = stderr.read()
    if len(error) > 1:
        if 'paramiko' in str(error):
            error = 0
        else:
            error = 1
    else:
        error = 0
    for output in stdoutput:
        line = output.strip()
        outF.write(f"{line}\n")
    return error, stderr

#run all of the commands needed for updates and create output files at ./outputs/.
def __update(ip: str, user: str, password: str, name: str) -> None:
    
    start_time = perf_counter()
    print(f"----- Starting {name} Updates -----")
    output = f"{output_dir}/{name}.txt"    
    output = open(output, "w", encoding="utf-8")
    output.write(str(datetime.now()))
    ssh_machine = ip
    ssh_username = user
    ssh_password = password

    status = 0
    failed = "    "

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    output.write(f"\n----- Updates Started -----\n")
    try: #try to ssh, if we get in then lets start the updates
        client.connect(hostname=ssh_machine, username=ssh_username, password=ssh_password, timeout=10)
    except: #ssh failed
        failed = "Failed: SSH_ERR"
        print(f"--- {name} SSH Failed ---")
        output.write("--- SSH Failed ---\n")
        logging.info(f"----- {name} SSH Failed -----")
        return

    for command in commands:
        #Run command, get if there was a failure and the stderr
        print(f"Running \'{command}\' on {name}")
        #__runCommand -> int: status(is there an error?), stderr(The error)
        status, stderr = __runCommand(command, client, output) 
        if(status == 1):
            output.write(f"{stderr}\n")
            failed = "Failed: ERR_CODE"

    if "Failed" in failed: #if we got an error code log it
        print(f"----- {name} {failed}! -----")
        output.write(f"----- Updates {failed}! -----\n")
        logging.info(f"----- {name} {failed}! -----")
    else: #updates were good
        print(f"----- {name} Done! -----")
        output.write("----- Updates Complete! -----\n")
        logging.info(f"----- Done with {name} updates! -----")

    #cleanup and send results to table
    client.close()
    output.close()
    end_time = perf_counter()
    run_time = end_time - start_time
    sheet.writerow([name, ip, round(run_time, 2), failed])
    return

#worker for multithreading 
def __worker() -> None:
    """worker for thread. pertty much just 'main' for thread"""
    global machine_user, machine_password
    while not q.empty():
        pbx = q.get()
        __update(pbx['ip'], machine_user, machine_password, pbx['name'])
    return

#multithreading function
def __multithread(thread_count: int) -> None:
    """make {thread_count} number of threads"""
    thread_list = []

    for t in range(thread_count):
        thread = threading.Thread(target=__worker)
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    return

def email(sender_email: str, receiver_email: str, password: str) -> None:
    """Send an email with the script output
    
    Args: sender: str, receiver: str, sender_password: str
    """
    logging.info("--- Sending Email ---")
    #set server local vars
    server = 'smtp-mail.outlook.com'
    port = 587
    str_io = StringIO()

    #get out table and convert it to html
    df = pd.read_csv(f"{output_dir}/emailTable.csv")
    df.to_html(buf=str_io)
    table_html = str_io.getvalue()

    #make message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Subject: PBX Updates"
    message["From"] = sender_email
    message["To"] = receiver_email

    #insert text and html table to message
    text = """\
    Subject: PBX Updates"""

    html = """\
    <html>
    <body>
        <p>PBX updates finished! Error code False means no errors. Logs can be found on the VM under ~/pbx-update/outputs</p>
        <p>{table_html}</p>
    </body>
    </html>
    """.format(table_html=table_html)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Send email
    try: #try to connect to server
        server = smtplib.SMTP(server, port)
    except Exception as e: #raise exception
        print(e)
        logging.info(f"EMAIL SERVER ERROR: {e}")
        server = smtplib.SMTP_SSL(server, 465)
    #encrypt and send email
    server.ehlo('mylowercasehost')
    server.starttls()
    server.ehlo('mylowercasehost')
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    logging.info("--- Email Sent ---")
    return

#MAIN
def run_update() -> None:
    """Main for pbxUpdater"""
    global machine_user, machine_password

    try:
        config = configparser.ConfigParser()
        config.read(f'{script_dir}/config.ini')
    except FileNotFoundError as e:
        logging.log(e)
        return
    
    machine_user = config.get('Login', 'user')
    machine_password = config.get('Login', 'password')

    email_sender = config.get('Email', 'sender')
    email_receiver = config.get('Email', 'reveiver')
    email_password = config.get('Email', 'password')
    
    tc = int(config.get('settings', 'threads'))
    debug = config.getboolean('settings', 'debug')

    global q, fp
    q = Queue()

    try:
        json_fp = open(f'{script_dir}/machines.json')
    except FileNotFoundError as e:
        logging.log(e)
        return
    
    global commands
    json_file = json.load(json_fp)
    commands = json_file['commands']
    for pbx in json_file['machines']:
        q.put(pbx)
    
    json_fp.close()

    if(debug == False): __multithread(tc) #if we aren't in debugging mode run the script
    sheetOpened.close()
    if(debug == False): email(email_sender, email_receiver, email_password) #if we aren't in debugging mode send the email
    
    return
