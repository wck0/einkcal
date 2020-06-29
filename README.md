# einkcal

A Python program to display calendar info on an eink display attached to a Raspberry Pi.

I typically have a schedule for the current semester posted at my office door so that students who are looking for me can know when I might be available.
Unfortunately, meetings get scheduled irregularly so my paper printout is often missing a lot of events.
So, I thought an nice e-ink display could connect to my academic calendar and update whenever a new event gets added.
That way students who are looking for me would see the most current info.

# requirements

The following should work on a Raspberry Pi 3 running Debian Lite.
It's untested on other configurations.

I'm using a Waveshare 2.7inch 2-Paper HAT.
It uses the `waveshare_epd` library to drive the display (and that library has its own dependencies).
A github repo for the library is [here](https://github.com/waveshare/e-Paper).
Details about software dependencies are [here](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT).
Step-by-step instructions are below.

You need to enable the SPI interface, e.g., through `raspi-config`.
The HAT requires the BCM2835 libraries, which can be installed as follows:

    wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
    tar zxvf bcm2835-1.60.tar.gz 
    cd bcm2835-1.60/
    sudo ./configure
    sudo make
    sudo make check
    sudo make install

Install WiringPi:

    sudo apt-get install wiringpi

And install the required python3 libraries:

    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo pip3 install RPi.GPIO
    sudo pip3 install spidev

Once those are done, you can download the Waveshare e-Paper library and install it.

    git clone https://github.com/waveshare/e-Paper
    cd e-Paper/RaspberryPi\&JetsonNano/python/
    sudo python3 setup.py install

And test the install with the provided demo code (below is for the 2.7 inch B&W display):

    cd examples
    sudo python3 epd_2in7_test.py

For my code to use it as a calendar display, clone the repo in your home directory.

    cd ~
    git clone https://github.com/wck0/einkcal.git

It requires the `caldav`, `icalendar`, and `pytz` python libraries.

    sudo pip3 install caldav
    sudo pip3 install icalendar

You should end up with `pytz` as well when installing icalendar.

The `caldav` library connects to a CalDAV server, and the response is parsed with the `icalendar` library.
`caldav` relies on libsxlt-dev`

    sudo apt-get install libxslt-dev
    
Also, we are using some fonts to render the text.
Raspbian Lite doesn't have them by default, so we get them:

    sudo apt-get install fontconfig-config

Finally, we set environment variables to access the CalDAV server:

 * `CAL_URL` - URL to CalDAV server
 * `CAL_USR` - CalDAV username
 * `CAL_PWD` - CalDAV password

These should go in `/etc/environment` to be available system wide.
Just add the following three lines to the bottom of that file.

    CAL_PWD=yourpassword
    CAL_USR=yourusername
    CAL_URL=https://example.com/path/to/caldav/calendar

# usage

Run the following to update the display:

    sudo -E python3 update_calendar.py
    
Using the `-E` flag with `sudo` allows the root user to use the environment variables set above.

# features

Displays the calendar events for the current day from one CalDAV calendar.

The display only updates if there is a change to the information that needs to be displayed.
That includes the date and the calendar events.
Information is logged if enabled.

A cronjob can run to check for updates every five minutes (for example) by adding the following to your crontab (run `crontab -e` to edit your crontab and put the line at the bottom):

    */5 * * * * sudo -E python3 /path/to/update_calendar.py 2>&1 | /usr/bin/logger -t einkCal

That will log any messages to `/var/log/syslog`.

You can also just run the script manually if you want to force a check for changes.
(But I haven't made any effort to ensure that a manual update doesn't conflict with the scheduled one or vice versa, so user beware.)

# TODO

I plan to have this display on a larger eink display (maybe 7.5in?), maybe a three-color display, and show events for multiple calendars for each day of the current week.
It would be nice to make that configurable, too, by the user.

It would be cool to also have the calendar visible on a webpage served by the same Raspberry Pi.

And right now, a couple of files are used to keep track of the date and the events.
It might be better to put those in a JSON file, along with the caldav credentials.
That would bipass the need for setting environment variables and make it all a little easier to manage.
