

cal = open("schedule.ics", 'r')

while True:
        line = cal.readline().strip()
        if not line:
            break
        if(line == "BEGIN:VEVENT"):
            startDate = cal.readline().split(":")[1].strip()
            endDate = cal.readline().split(":")[1].strip()
            name = cal.readline().split(":")[1].strip()
            location = cal.readline().split(":")[1].strip()
            print(f"start: {location}\n")
