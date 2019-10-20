import datetime
import operator
import requests
import json
import sys
import os
import math
import polyline

cal_file = sys.argv[1]
print(f"file: {cal_file}")

cal = open(cal_file, 'r')

buildings = {}
with open("buildings.json", "r") as read_file:
    buildings = json.load(read_file)

api_key = ""

with open("api_key.txt") as key_file:
    api_key = key_file.readline().strip()

bus_api_call = "https://transloc-api-1-2.p.rapidapi.com/stops.json?agencies=1323"
bus_api_headers = {"x-rapidapi-host": "transloc-api-1-2.p.rapidapi.com",
	               "x-rapidapi-key": "726c140f50mshcda6ecc676bb6d5p137173jsnc9fa1972a6f7"}
bus_res = requests.get(bus_api_call, headers=bus_api_headers).json()

acceptable_routes = ["4012616", "4012618", "4012620", "4012624", "4012626", "4012628", "4012630", "4012632", "4012634"]

class Position:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def __repr__(self):
        return f"lat: {self.lat}, long:{self.long}"

    def get_dict(self):
        return {lat:self.lat, long:self.long}

    def distance(self, lat, long):
        return math.sqrt((self.lat-lat)**2 + (self.long-long)**2)


class Location:

    def __init__(self, position, name, acronym, campus = None):
        self.acronym = acronym
        self.position = position
        if campus is not None:
            self.campus = campus
        if name is None:
            self.name = buildings[acronym.split('-')[0]]["name"]
            self.campus = buildings[acronym.split('-')[0]]["campus"]
        else:
            self.name = name


    def __eq__(self, loc2):
        return self.position == loc2.position and \
               self.name == loc2.name and \
               self.acronym == loc2.acronym

    def find_position(self):
        self.position = Location.get_position(self.name)

    def get_address_str(self):
        return self.name.replace(" ", "+")

    @staticmethod
    def get_position(address):
        address_str = address.replace(" ", "+")
        api_call = f"https://maps.googleapis.com/maps/api/geocode/json?address={address_str}&key={api_key}"
        response = requests.get(api_call)
        resp_location = response.json()["results"][0]['geometry']['location']
        return Position(resp_location["lat"], resp_location["lng"])


class Class:
    def __init__(self, date, startTime, endTime, name, location):
        self.date = date
        self.startTime = startTime
        self.endTime = endTime
        self.name = name
        self.location = location

    def __repr__(self):
        return f"date: class {self.name} on {self.date.month}/{self.date.day}/{self.date.year} from {self.startTime} to {self.endTime} at {self.location.name} on {self.location.campus}\n"

    def find_position(self):
        self.location.find_position()

    def __eq__(self, class2):
        #print(f"class1: {self}\nclass2: {class2}")
        return self.startTime == class2.startTime and \
               self.endTime == class2.endTime and \
               self.name == class2.name and \
               self.location == class2.location

    def get_dict(self):
        return {"date":str(self.date),
                "startTime":self.startTime,
                "endTime":self.endTime,
                "name":self.name,
                "acronym":self.location.acronym,
                "loc_name":self.location.name}




schedule = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}
home = cal.readline().strip()
home_campus = cal.readline().strip()

dorm_class = Class(None, None, None, home, Location(None, home, None, campus=home_campus))
sys.stderr.write(f"dorm_campus: {dorm_class.location.campus}")
dorm_class.find_position()
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

        sys.stderr.write(location + "\n")
        loc = Location(None, None, location)
        newClass = Class(date, int(startTime), int(endTime), name, loc)
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

#adding bus layovers

print(schedule)

write_file = open(cal_file + "_response", "w+")

schedule_dict = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}
for day in schedule:
    schedule[day].insert(0, dorm_class)
    schedule[day].append(dorm_class)

    schedule_dict[day].insert(0, {"message":"Leave your dorm at " + dorm_class.name + "<br><br>"})

    for c in schedule[day]:
        schedule_dict[day].append(c.get_dict())

    schedule_dict[day].append({"message":"Come back to your dorm at " + dorm_class.name + "<br><br>"})


for day in schedule:
    schedule_dict_count = 1
    schedule[day][0].find_position()
    write_file.write(f"{day}\n")
    for i in range(1,len(schedule[day])):
        class1 = schedule[day][i-1]
        class2 = schedule[day][i]
        class2.find_position()

        if(class1.location.campus != class2.location.campus):
            start_min_dist = sys.maxsize
            start_min_index = 0
            start_pos = {}

            end_min_dist = sys.maxsize
            end_min_index = 0
            end_pos = {}
            for j in range(len(bus_res["data"])):
                stop = bus_res["data"][j];
                stop_pos = stop["location"]
                start_dist = class1.location.position.distance(stop["location"]["lat"], stop["location"]["lng"])
                end_dist = class2.location.position.distance(stop["location"]["lat"], stop["location"]["lng"])
                if(start_dist < start_min_dist):
                    start_min_dist = start_dist;
                    start_min_index = j;
                    start_pos = stop_pos

                if(end_dist < end_min_dist):
                    end_min_dist = end_dist;
                    end_min_index = j;
                    end_pos = stop_pos

            start_bus_loc = bus_res["data"][start_min_index]
            print(f"start_name: {start_bus_loc['name']}")
            start_bus_loc = Location(start_bus_loc["location"], start_bus_loc["name"] + " Bus Stop Rutgers", None)
            start_bus_tuple = (start_bus_loc.position["lat"], start_bus_loc.position["lng"])


            end_bus_loc = bus_res["data"][end_min_index]
            print(f"end_name: {end_bus_loc['name']}")
            end_bus_loc = Location(end_bus_loc["location"], end_bus_loc["name"] + " Bus Stop Rutgers", None)
            end_bus_tuple = (round(end_bus_loc.position["lat"],5), round(end_bus_loc.position["lng"],5))

            acronym_dict = {"BUS":"Busch", "C/D":"Cook Douglass", "CAC":"College Ave:", "LIV":"Livingston"}
            sys.stderr.write(class2.location.campus + "\n")
            message_str =  "Get on the bus at the " + start_bus_loc.name + " heading towards " + acronym_dict[class2.location.campus]    + "<br><br>"
            message_str += "Get off the bus at the " + end_bus_loc.name + "<br><br>"

            schedule_dict[day].insert(schedule_dict_count, {"message":message_str})

            class1_address_str = class1.location.get_address_str()
            class2_address_str = class2.location.get_address_str()
            start_pos_address_str = f"{start_pos['lat']},{start_pos['lng']}"
            end_pos_address_str = f"{end_pos['lat']},{end_pos['lng']}"

            api_call1 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={class1_address_str}&"
                        f"destination={start_pos_address_str }&"
                        "mode=walking&"
                        f"key={api_key}")

            api_call2 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={start_pos_address_str }&"
                        f"destination={end_pos_address_str }&"
                        "mode=driving&"
                        f"key={api_key}")

            api_call3 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={end_pos_address_str}&"
                        f"destination={class2_address_str}&"
                        "mode=walking&"
                        f"key={api_key}")

            calls = [api_call1, api_call2, api_call3]
            print(calls)

            for c in calls:
                response = requests.get(c)
                output = json.dumps(response.json())
                write_file.write(f"{output}\n")

            schedule_dict_count += 1


        else:
            class1_address_str = class1.location.get_address_str()
            class2_address_str = class2.location.get_address_str()

            api_call = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={class1_address_str}&"
                        f"destination={class2_address_str}&"
                        "mode=walking&"
                        f"key={api_key}")
            #print(api_call)
            response = requests.get(api_call)
            output = response.json()
            write_file.write(f"{json.dumps(output)}\n")
        schedule_dict_count += 1

print(json.dumps(schedule_dict))

write_file.write("SCHEDULE_DONE\n" + json.dumps(schedule_dict))
os.remove(cal_file)
