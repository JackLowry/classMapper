import datetime
import operator

cal = open("schedule.ics", 'r')

class Location:

    def __init__(self, position, name, acronym):
        self.position = position
        self.name = name
        self.acronym = acronym

    def __eq__(self, loc2):
        return self.position == loc2.position and \
               self.name == loc2.name and \
               self.acronym == loc2.acronym

class Class:
    def __init__(self, date, startTime, endTime, name, location):
        self.date = date
        self.startTime = startTime
        self.endTime = endTime
        self.name = name
        self.location = location

    def __repr__(self):
        return f"date: class {self.name} on {self.date.month}/{self.date.day}/{self.date.year} from {self.startTime} to {self.endTime} at {self.location}\n"

    def __eq__(self, class2):
        #print(f"class1: {self}\nclass2: {class2}")
        return self.startTime == class2.startTime and \
               self.endTime == class2.endTime and \
               self.name == class2.name and \
               self.location == class2.location





schedule = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}

while True:
        line = cal.readline().strip()
        if not line:
            break
        if(line == "BEGIN:VEVENT"):
            startDate = cal.readline().split(":")[1].strip()
            endDate = cal.readline().split(":")[1].strip()
            cal.readline()
            name = cal.readline().split(":")[1].strip()
            location = cal.readline().split(":")[1].strip()

            year = startDate[0:4]
            month = startDate[4:6]
            day = startDate[6:8]
            startTime = startDate[9:13]
            endTime = endDate[9:13]

            date = datetime.date(int(year), int(month), int(day))

            loc = Location(None, None, location)
            newClass = Class(date, int(startTime), int(endTime), name, location)
            weekday = newClass.date.strftime('%A')

            duplicate = False

            for c in schedule[weekday]:
                if c == newClass:
                    duplicate = True
                    break

            if(duplicate):
                continue

            schedule[weekday].append(newClass)

for day in schedule:
    schedule[day] = sorted(schedule[day], key=operator.attrgetter('startTime'))
print(schedule)
