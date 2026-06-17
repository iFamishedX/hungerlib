import time
import math
from datetime import datetime, timedelta

def snapSchedule(minimumMinutes: int = 30, snapMinutes: tuple[int, int] = (0, 30)) -> dict:
    '''Powerful snap scheduler (will update this docstring later)'''
    now = datetime.now()
    minimum = now + timedelta(minutes=minimumMinutes)
    snapMinutes = sorted(snapMinutes)

    for snap in snapMinutes:
        if minimum.minute < snap:
            scheduled = minimum.replace(minute=snap, second=0, microsecond=0)
            break
    else:
        scheduled = (minimum.replace(minute=0, second=0, microsecond=0)
                     + timedelta(hours=1))

    return {
        'now': now,
        'minimum': minimum,
        'scheduled': scheduled,
        'formatted': scheduled.strftime('%I:%M %p')
    }

def runCountdownEvents(
    target_time,
    minute_callbacks: dict | None = None,
    second_callbacks: dict | None = None,
    tick_interval: int = 1
):
    '''Runs events based on a countdown timer'''

    # Default to empty dicts if none provided
    minute_callbacks = minute_callbacks or {}
    second_callbacks = second_callbacks or {}

    # Track which events we've already fired
    fired_minutes = set()
    fired_seconds = set()

    while True:
        now = datetime.now()
        seconds_left = math.ceil((target_time - now).total_seconds())
        minutes_left = seconds_left // 60

        # Countdown finished
        if seconds_left <= 0:
            return

        # Fire minute-based events
        if minutes_left in minute_callbacks and minutes_left not in fired_minutes:
            fired_minutes.add(minutes_left)
            minute_callbacks[minutes_left]()

        # Fire second-based events
        if seconds_left in second_callbacks and seconds_left not in fired_seconds:
            fired_seconds.add(seconds_left)
            second_callbacks[seconds_left]()

        time.sleep(tick_interval)

def waitForOnline(server: 'Server', timeout: int = 60, interval: int = 2) -> bool:
    '''Pauses script until the server is back online'''
    elapsed = 0
    while elapsed < timeout:
        if server.isOnline():
            return True
        time.sleep(interval)
        elapsed += interval
    return False

def waitForOffline(server: 'Server', timeout: int = 60, interval: int = 2) -> bool:
    '''Pauses script until the server is fully offline'''
    elapsed = 0
    while elapsed < timeout:
        if server.isOffline():
            return True
        time.sleep(interval)
        elapsed += interval
    return False

def secsUntil(target: datetime) -> int:
    '''Returns the seconds until the target time'''
    now = datetime.now()
    return int((target - now).total_seconds())

def minsUntil(target: datetime) -> int:
    '''Returns the minutes until the target time'''
    now = datetime.now()
    return int((target - now).total_seconds()) // 60
