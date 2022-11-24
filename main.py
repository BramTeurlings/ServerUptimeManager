# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from mcrcon import MCRcon
import os
import time as baseTime
import re
from datetime import datetime, time
import requests

emptyPlayerCountTicks = 0
serverBedtimeCountTicks = 0
url = 'http://localhost:30000/modules/user-activity-tracker/UserActivityLog.json'


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def shut_down():
    with MCRcon('127.0.0.1', 'h&s%1N_10N$') as mcr:
        resp = mcr.command('stop')
    if 'stopping' in resp.lower():
        # Shut down the computer
        os.system('shutdown -s')


startTime = baseTime.time()

print("MCRCON Service initialized. Waiting for player inactivity...")

while True:
    # try:
    # Runs every 60 seconds, needs to check server for amount of people logged in.

    allProgramsInactive = 1

    # Check if the Minecraft server is inactive
    try:
        with MCRcon('127.0.0.1', 'h&s%1N_10N$') as mcr:
            resp = mcr.command('list')
        if 'player' in resp:  # there are 0/20 players online: - This will be different for you.
            x = re.split("§c|§6", resp)  # "§6There are §c0§6 out of maximum §c20§6 players online."
            if x[2] == '0':
                print("Minecraft server empty, amount of ticks registered: ", emptyPlayerCountTicks)
            else:
                emptyPlayerCountTicks = 0
                allProgramsInactive = 0
    except:
        print('Minecraft server refused connection! Treating it as offline...')

    # Check if the FoundryVTT server is inactive
    #
    # (NOT NEEDED!) You can call the following API: http://localhost:30000/modules/api/api.html?name=module.user-activity-tracker&arg0=%7B%22request%22:%20%22test%22%7D&arg1=%7B%22result%22:%22test%22%7D to force an update of the JSON file.
    # Read the data from the UserActivityLog.json at http://localhost:30000/modules/user-activity-tracker/UserActivityLog.json
    # This JSON file is updated every time a user's status changes.
    # Because of this, we might want to not use the API call to refresh.
    try:
        resp = requests.get(url)
        data = resp.json()
        if data:
            for item in data:
                if item.get('name') != 'world name':
                    if item.get('status') == 0:
                        # User is not AFK
                        allProgramsInactive = 0
                        emptyPlayerCountTicks = 0
                        break
    except:
        print('Foundry server refused connection! Treating it as offline...')

    # Only count up the emptyPlayerCountTicks when ALL programs are inactive.
    if allProgramsInactive:
        emptyPlayerCountTicks += 1
        print("All servers empty, amount of ticks registered: ", emptyPlayerCountTicks)

    # Check if all programs have been inactive for the specified amount of time.
    if emptyPlayerCountTicks == 10:
        # Stop the server when empty for x amount of mins:
        shut_down()

    # Check if time is past 11PM or before 9AM
    if is_time_between(time(22, 50), time(6, 0)):
        print(datetime.now().time())
        with MCRcon('127.0.0.1', 'h&s%1N_10N$') as mcr:
            resp = mcr.command(
                'say End of day time almost reached, shutting down server in 10 minutes... Will notify again when 1 minute is left.')
        serverBedtimeCountTicks += 1
        if serverBedtimeCountTicks == 9:
            with MCRcon('127.0.0.1', 'h&s%1N_10N$') as mcr:
                resp = mcr.command('say End of day time imminent, shutting down server in 1 minute... Please log out.')
        if serverBedtimeCountTicks >= 10:
            secondCount = 10
            while secondCount > 0:
                with MCRcon('127.0.0.1', 'h&s%1N_10N$') as mcr:
                    warningString = "say End of day time reached, shutting down server in " + str(secondCount) + " seconds... Please log out."
                    resp = mcr.command(warningString)
                secondCount -= 1
                baseTime.sleep(1)

            if secondCount < 1:
                # Shut down server and host PC
                shut_down()

    # except:
    #    print("An exception has occurred")

    baseTime.sleep(60.0 - ((baseTime.time() - startTime) % 60.0))


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
