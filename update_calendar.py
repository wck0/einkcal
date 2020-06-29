#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import caldav
from datetime import datetime, timedelta
import icalendar

# time zone info
import pytz
LOS_ANGELES = pytz.timezone('America/Los_Angeles')

# calendar infor
url = os.environ.get('CAL_URL')
username = os.environ.get('CAL_USR')
password = os.environ.get('CAL_PWD')

# local files to store previous info
schedule_file = "/home/pi/einkcal/schedule"
day_file = "/home/pi/einkcal/day"

# eink font setup
fontdir = '/usr/share/fonts/truetype/dejavu'
MONO = 'DejaVuSansMono.ttf'
HEAD_FONT_SIZE = 24
HEAD_FONT = ImageFont.truetype(os.path.join(fontdir, MONO), HEAD_FONT_SIZE)
EVENT_FONT_SIZE = 18
EVENT_FONT = ImageFont.truetype(os.path.join(fontdir, MONO), EVENT_FONT_SIZE)

# logging settings
logging.basicConfig(level=logging.INFO)

# now we start working

# get calendar
client = caldav.DAVClient(url, username=username, password=password)

try:
    principal = client.principal()
except ConnectionError:
    logging.error("Could not connect to CALDAV server. Quitting.")
    exit()
for calendar in principal.calendars():
    if calendar.name == "Academia":
        break

# get today's events
today = datetime.today() # - timedelta(days=4)
after = today - timedelta(days=2)
before = today + timedelta(days=2)

events_today = calendar.date_search(start=after, end=before)

mystrs = []
for e in events_today:
    event_today = icalendar.Calendar.from_ical(e.data)
    fmt = "%H%M"
    for vevent in event_today.walk(name="VEVENT"):
        dtstart = vevent.get('dtstart').dt
        if today.astimezone(LOS_ANGELES).day ==\
           dtstart.astimezone(LOS_ANGELES).day:
            start = dtstart.astimezone(LOS_ANGELES).strftime(fmt)
            dtend = vevent.get('dtend').dt
            end = dtend.astimezone(LOS_ANGELES).strftime(fmt)
            date = dtstart.astimezone(LOS_ANGELES).strftime("%m%d")
            summary = vevent.get('summary')
            mystrs.append(f"{start}-{end} {summary}")

msg = "\n".join(sorted(mystrs))
daystr = str(today.astimezone(LOS_ANGELES).day)
# check to see if events differ from the stored ones, if present

try:
    with open(schedule_file, 'r') as f:
        last_msg = f.read()
    if msg != last_msg:
        logging.info("Detected a change in schedule")
        update_needed = True
    else:
        update_needed = False
        logging.info("No change to schedule detected")
except FileNotFoundError:
    logging.warning("No schedule file found.")
    update_needed = True

try:
    with open(day_file, 'r') as f:
        last_day = f.read()
    if last_day != daystr:
        logging.info("Detected a change in day")
        update_needed = True
except FileNotFoundError:
    logging.warning("No day file found.")
    update_needed = True

if update_needed:
    try:
        logging.info("eink Calendar prototype")
        
        epd = epd2in7.EPD()
        
        '''2Gray(Black and white) display'''
        logging.info("init and Clear")
        epd.init()
        epd.Clear(0xFF)
        
        image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(image)
        head = today.astimezone(LOS_ANGELES).strftime("%A %x")
        logging.info("Write header")
        draw.text((1,1), head, font=HEAD_FONT, fill=0)
        logging.info("Write schedule")
        draw.text((1,1+HEAD_FONT_SIZE), msg, font=EVENT_FONT, fill=0)

        epd.display(epd.getbuffer(image))
        logging.info("Put e-paper to sleep.")
        epd.sleep()
        with open(schedule_file, 'w') as f:
            f.write(msg)
            logging.info("Writing schedule to file")
        with open(day_file, 'w') as f:
            f.write(daystr)
            logging.info("Writing day to file")
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        exit()
else:
    sys.exit()
