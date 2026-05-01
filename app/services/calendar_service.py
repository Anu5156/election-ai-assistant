import urllib.parse
from datetime import datetime


def generate_calendar_link(location, date="20260510", title="Vote in Election", description=None):
    """
    Generates a Google Calendar event link for voting reminder

    Args:
        location (str): User location
        date (str): Date in YYYYMMDD format
        title (str): Event title
        description (str): Event description

    Returns:
        str: Google Calendar event URL
    """

    try:
        # ⏰ Default timings (7 AM to 6 PM voting window)
        start_date = f"{date}T070000"
        end_date = f"{date}T180000"

        # 📌 Default description
        if not description:
            description = "Remember to vote and participate in democracy!"

        place = f"Polling Station - {location}"

        # 🔥 URL ENCODING (IMPORTANT)
        title_encoded = urllib.parse.quote(title)
        details_encoded = urllib.parse.quote(description)
        location_encoded = urllib.parse.quote(place)

        calendar_url = (
            "https://calendar.google.com/calendar/render?"
            f"action=TEMPLATE"
            f"&text={title_encoded}"
            f"&dates={start_date}/{end_date}"
            f"&details={details_encoded}"
            f"&location={location_encoded}"
        )

        return calendar_url

    except Exception as e:
        print("CALENDAR ERROR:", e)
        return None


def generate_ics(location, date, time):
    from datetime import datetime, timedelta

    try:
        # normalize time
        if len(time.split(":")) == 2:
            time += ":00"

        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        dt_end = dt + timedelta(hours=1)

        start = dt.strftime("%Y%m%dT%H%M%S")
        end = dt_end.strftime("%Y%m%dT%H%M%S")

        ics_content = f"""BEGIN:VCALENDAR
                    VERSION:2.0
                    BEGIN:VEVENT
                    SUMMARY:Election Reminder
                    DTSTART:{start}
                    DTEND:{end}
                    LOCATION:{location}
                    DESCRIPTION:Go vote at {location}
                    END:VEVENT
                    END:VCALENDAR
                    """

        return ics_content  
    except Exception as e:
        print("ICS ERROR:", e)
        return None