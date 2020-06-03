# einkcal

A Python program to display calendar info on an eink display.

I typically have a schedule for the current semester posted at my office door so that students who are looking for me can know when I might be available.
Unfortunately, meetings get scheduled irregularly so my paper printout is often missing a lot of events.
So, I thought an nice e-ink display could connect to my academic calendar and update whenever a new event gets added.
That way students who are looking for me would see the most current info.

# requirements

This code was developed on a Raspberry Pi 3 Model B Rev 1.2 running Ubuntu 20.04 server.
Attached to it is a [Waveshare 2.7 inch e-Paper HAT](https://smile.amazon.com/gp/product/B075FQKSZ9/).

It uses the `waveshare_epd` library to drive the display (and that library has its own dependencies).
The `caldav` library connects to a CalDAV server, and the response is parsed with the `icalendar` library.

For some reason, I was having difficulty setting everything up in a `venv` so `requirements.txt` reflects the system-wide result of `pip3 freeze`.

Environment variables need to be set to access the CalDAV server:

 * `CAL_URL` - URL to CalDAV server
 * `CAL_USR` - CalDAV username
 * `CAL_PWD` - CalDAV password

On the Raspberry Pi, these should be set in `/etc/environment` since the script needs to run as root.

# features

Displays the calendar events for the current day from one CalDAV calendar.

The display only updates if there is a change to the information that needs to be displayed.
That includes the date and the calendar events.
Information is logged if enabled.

A cronjob can run to check for updates every five minutes (for example) by adding the following to your crontab:

    */5 * * * * sudo python3 /path/to/update_calendar.py 2>&1 | /usr/bin/logger -t einkCal

You can also just run the script manually if you want to force a check for changes.
(But I haven't made any effort to ensure that a manual update doesn't conflict with the scheduled one or vice versa, so user beware.)

# TODO

I plan to have this display on a larger eink display (maybe 7.5in?), maybe a three-color display, and show events for multiple calendars for each day of the current week.
It would be nice to make that configurable, too, by the user.

It would be cool to also have the calendar visible on a webpage served by the same Raspberry Pi.
