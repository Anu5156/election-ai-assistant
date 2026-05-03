import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

def generate_calendar_link(
    location: str, 
    date: str = "20260510", 
    title: str = "Vote in Election", 
    description: Optional[str] = None
) -> Optional[str]:
    """
    Generates a high-fidelity Google Calendar event link for a voting reminder.
    
    Args:
        location: Human-readable location or booth name.
        date: Date in YYYYMMDD format.
        title: Title of the calendar event.
        description: Detailed description of the event.
        
    Returns:
        A Google Calendar TEMPLATE URL or None if an error occurs.
    """

    try:
        # ⏰ Default timings (7 AM to 6 PM IST voting window)
        start_date = f"{date}T070000"
        end_date = f"{date}T180000"

        # 📌 Default description if none provided
        if not description:
            description = "Your voice matters! Head to your assigned polling station and cast your vote for a stronger democracy."

        place = f"Polling Station - {location}"

        # 🔥 URL ENCODING (Strict compliance with RFC 3986)
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
        print(f"CALENDAR GENERATION ERROR: {e}")
        return None


def generate_ics(location: str, date: str, time: str) -> Optional[str]:
    """
    Generates a standard iCalendar (.ics) format string for offline calendar integration.
    
    Args:
        location: The physical location of the booth.
        date: Date in ISO format (YYYY-MM-DD).
        time: Time in HH:MM format.
        
    Returns:
        A valid VCALENDAR string or None on failure.
    """
    try:
        # Normalize time to include seconds
        if len(time.split(":")) == 2:
            time += ":00"

        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        dt_end = dt + timedelta(hours=1)

        start = dt.strftime("%Y%m%dT%H%M%S")
        end = dt_end.strftime("%Y%m%dT%H%M%S")

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CivicGuide AI//NONSGML Election Reminder//EN
BEGIN:VEVENT
SUMMARY:🗳️ Election Day Reminder
DTSTART:{start}
DTEND:{end}
LOCATION:{location}
DESCRIPTION:Time to vote! Ensure you carry your EPIC card and visit your polling station at {location}.
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Election Reminder
END:VALARM
END:VEVENT
END:VCALENDAR"""

        return ics_content  
    except Exception as e:
        print(f"ICS GENERATION ERROR: {e}")
        return None