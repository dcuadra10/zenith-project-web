import urllib.request
import json
import os
import re

def parse_ics_date(val):
    # e.g., 20250222 or 20250222T100000Z or 20250222T100000
    val = val.strip()
    if 'T' in val:
        # Date and time
        match = re.match(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)', val)
        if match:
            y, m, d, hh, mm, ss, z = match.groups()
            iso = f"{y}-{m}-{d}T{hh}:{mm}:{ss}"
            if z:
                iso += "Z"
            return iso, False
    else:
        # Just date
        match = re.match(r'(\d{4})(\d{2})(\d{2})', val)
        if match:
            y, m, d = match.groups()
            return f"{y}-{m}-{d}", True
    return val, True

def clean_text(text):
    # Unescape commas, semicolons, and newlines
    text = text.replace(r'\,', ',').replace(r'\;', ';')
    text = text.replace(r'\n', '\n').replace(r'\N', '\n')
    return text.strip()

def sync():
    url = "https://calendar.google.com/calendar/ical/5589780017d3612c518e01669b77b70f667a6cee4798c961dbfb9cf1119811f3%40group.calendar.google.com/public/basic.ics"
    ics_path = "scratch/basic.ics"
    
    print("Fetching ICS calendar...")
    content = None
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        os.makedirs("scratch", exist_ok=True)
        with open(ics_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Fetched and saved to scratch/basic.ics successfully.")
    except Exception as e:
        print(f"Failed to fetch online feed ({e}). Attempting to read local scratch/basic.ics...")
        if os.path.exists(ics_path):
            with open(ics_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("Error: No local basic.ics found.")
            return

    # Unfold lines
    unfolded_lines = []
    for line in content.splitlines():
        if line.startswith(' ') or line.startswith('\t'):
            if unfolded_lines:
                unfolded_lines[-1] += line[1:]
        else:
            unfolded_lines.append(line)

    events = []
    current_event = None

    for line in unfolded_lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("BEGIN:VEVENT"):
            current_event = {}
        elif line.startswith("END:VEVENT"):
            if current_event and "start" in current_event:
                events.append(current_event)
            current_event = None
        elif current_event is not None:
            # Split key and value by the first colon that isn't inside quotes or parameter list
            # A simple split on ':' is usually fine, but keys can have attributes (e.g. DTSTART;VALUE=DATE:...)
            if ":" in line:
                key_part, val = line.split(":", 1)
                
                # Clean up key parameters
                key = key_part.split(";")[0]
                
                if key == "SUMMARY":
                    current_event["summary"] = clean_text(val)
                elif key == "DESCRIPTION":
                    current_event["description"] = clean_text(val)
                elif key == "DTSTART":
                    date_str, all_day = parse_ics_date(val)
                    current_event["start"] = date_str
                    current_event["all_day"] = all_day
                elif key == "DTEND":
                    date_str, _ = parse_ics_date(val)
                    current_event["end"] = date_str
                elif key == "LOCATION":
                    current_event["location"] = clean_text(val)
                elif key == "UID":
                    current_event["uid"] = val.strip()

    # Sort events by start date
    events.sort(key=lambda x: x["start"])

    # Output to assets/events.json
    os.makedirs("assets", exist_ok=True)
    events_json_path = "assets/events.json"
    with open(events_json_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully processed {len(events)} events and saved to {events_json_path}")

if __name__ == "__main__":
    sync()
