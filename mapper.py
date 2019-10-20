import datetime
import operator
import requests
import json
import sys
import os
import math

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

    def __init__(self, position, name, acronym):
        self.acronym = acronym
        self.position = position
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
    for c in schedule[day]:
        schedule_dict[day].append(c.get_dict())


write_file.write(json.dumps(schedule_dict) + "\n")

for day in schedule:
    schedule[day][0].find_position()
    write_file.write(f"{day}\n")
    for i in range(1,len(schedule[day])):
        class1 = schedule[day][i-1]
        class2 = schedule[day][i]
        class2.find_position()

        if(class1.location.campus != class2.location.campus):
            start_min_dist = sys.maxsize
            start_min_index = 0

            end_min_dist = sys.maxsize
            end_min_index = 0
            for i in range(len(bus_res["data"])):
                stop = bus_res["data"][i];
                start_dist = class1.location.position.distance(stop["location"]["lat"], stop["location"]["lng"])
                end_dist = class2.location.position.distance(stop["location"]["lat"], stop["location"]["lng"])
                if(start_dist < start_min_dist):
                    start_min_dist = start_dist;
                    start_min_index = i;

                if(end_dist < end_min_dist):
                    start_end_dist = end_dist;
                    start_end_index = i;

            start_bus_loc = bus_res["data"][start_min_index]
            start_bus_loc = Location(start_bus_loc["location"], start_bus_loc["name"] + " Bus Stop Rutgers", None)
            start_address_str = start_bus_loc.get_address_str()

            end_bus_loc = bus_res["data"][end_min_index]
            end_bus_loc = Location(end_bus_loc["location"], end_bus_loc["name"] + " Bus Stop Rutgers", None)
            end_address_str = end_bus_loc.get_address_str()

            class1_address_str = class1.location.get_address_str()
            class2_address_str = class2.location.get_address_str()

            api_call1 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={class1_address_str}&"
                        f"destination={start_address_str}&"
                        "mode=walking&"
                        f"key={api_key}")

            api_call2 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={start_address_str}&"
                        f"destination={end_address_str}&"
                        "mode=driving&"
                        f"key={api_key}")

            api_call3 = ("https://maps.googleapis.com/maps/api/directions/json?"
                        f"origin={end_address_str}&"
                        f"destination={class2_address_str}&"
                        "mode=walking&"
                        f"key={api_key}")

            calls = [api_call1, api_call2, api_call3]

            for c in calls:
                response = requests.get(c)
                output = json.dumps(response.json())
                write_file.write(f"{output}\n")


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

#os.remove(cal_file)
