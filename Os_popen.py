# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
###conda install nwani::portaudio nwani::pyaudio
##sudo apt install libespeak1
#sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
#sudo apt-get install ffmpeg libav-tools
#sudo pip install pyaudio
#sudo apt install flite
#sudo apt install lynis
#sudo apt install rkhunter
from __future__ import print_function
import datetime
import pytz
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#from datetime import timedelta
#import datetime
#from pytz import timezone
import os
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]
def speak(text):
  os.popen( 'flite "'+text+'"' )

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening..")
        audio = r.listen(source)
        said = ""

        try:
            print("Recognizing..")
            said = r.recognize_google(audio)
            print(said)

        except Exception as e:
            print("Exception:", str(e))

    return said.lower()




def authenticate_google():

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service
def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.time.min)
    end = datetime.datetime.combine(day, datetime.time.max)
    utc = pytz.UTC
    date = date.astimezone(utc)
    end = end.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
        
    else:
        speak(f"you have {len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"
                
            speak(event["summary"] + " at " + start_time)

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # THE NEW PART STARTS HERE
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  # FIXED FROM VIDEO
        return datetime.date(month=month, day=day, year=year)
def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":","-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)
    os.system(f"leafpad {file_name}")
def quick_scan():
    os.system("sudo xterm -T QuickScanner -e rkhunter --check")
    
def pack_info():
    os.system("dpkg --get-selections > installed_packages_info.txt")
def apps_info():
    os.system("chmod +x apps.sh; bash apps.sh")

WAKE = "hello"
#Login credentials for google calender
SERVICE = authenticate_google()
print("Start..")
while True:
    text = get_audio()
    
    if text.count(WAKE) > 0:
        speak("I'm ready")
        text = get_audio()
        CAL_STR = ["what do i have", "do i have plans", "am i busy"]
        for phrase in CAL_STR:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I didn't get you, please try again")
         #Make a note           
        NOTE_STR = ["make a note", "write this down", "remember this"]
        for phrase in NOTE_STR:
            if phrase in text.lower():
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that")
                
        #System scanning
                
        SCAN_STR = ["scan my system", "check system vulnerabilities", "check rootkits", "check viruses"]
        for phrase in SCAN_STR:
            if phrase in text.lower():
                speak("Scanning your whole system")
                quick_scan()
                
        #Show all system packages
        PACKAGES_STR = ["list packages", "i need installed packages info", "get all packages information", "do i have any package installed", "installed packages info", "info installed packages"]
        for phrase in PACKAGES_STR:
            if phrase in text.lower():
                pack_info()
                speak("All information saved in txt file check it out")
                os.system("leafpad installed_packages_info.txt")
        #Show all applications installed
        APP_STR = ["list down all apps", "installed apps", "all installed apps list down"]
        for phrase in APP_STR:
            if phrase in text.lower():
                apps_info()
                speak("All installed apps info saved in txt file check it out")
                os.system("leafpad installed_apps_info.txt")
        # get_events(get_date(text), SERVICE)
