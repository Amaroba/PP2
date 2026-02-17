from datetime import datetime, timedelta

def subtract_five_days():
    today = datetime.now()
    five_days_ago = today - timedelta(days=5)
    print("Current date:", today)
    print("Date 5 days ago:", five_days_ago)
    print()

def yesterday_today_tomorrow():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    print("Yesterday:", yesterday)
    print("Today:", today)
    print("Tomorrow:", tomorrow)
    print()

def remove_microseconds():
    now = datetime.now()
    no_microseconds = now.replace(microsecond=0)
    print("Current datetime:", now)
    print("Datetime without microseconds:", no_microseconds)
    print()

def difference_in_seconds(date1, date2):
    diff = date2 - date1
    print("Date 1:", date1)
    print("Date 2:", date2)
    print("Difference in seconds:", diff.total_seconds())
    print()

