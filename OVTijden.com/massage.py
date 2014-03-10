#!/usr/bin/python3
import os;
import re;
import sys;

from bs4 import BeautifulSoup;

def Time(hr = 0, min = 0, sec = 0):
	if hr < 2:
		hr += 24;
	return hr * 60 + min + sec / 60;

def getRows(htmldoc):
    soup = BeautifulSoup(htmldoc);
    return soup.findAll('tr');

def mergeOrder(service, order):
	if service not in services:
		services[service] = [];
	if order not in services[service]:
		services[service].append(order);
	
	services[service].sort(key=lambda order: order[1]);

# sorts the services by departure time
def mergeService(serviceData):
	# find the insertion point
	index = 0;
	for service in servicesByTime:
		if service[0][1] > serviceData[0][1]:
			break;
		index += 1;
	
	# insert before the later service
	servicesByTime.insert(index, serviceData);

services = {};
servicesByTime = [];

for fileName in os.listdir("."):
	if not fileName.endswith(".txt"):
		continue;
	
	stationName = fileName.partition(".")[0];
	
	with open(fileName) as data:
		havePlatforms = (data.readline() == "has platforms\n");
		text = data.read();

	rows = getRows(text);
	for row in rows:
		contents = [];
		columns = row.findAll('td');
		for column in columns:
			contents.append(''.join(column.findAll(text=True)));
		
		if len(contents) != 10:
			print("Manual massaging needed:");
			print("File: {}".format(fileName));
			print(row);
			
			continue;
		
		try:
			#        train id     - time                                              - S                      tation name      - track nr   - train type - has platforms
			order = (contents[0], Time(int(contents[1][0:2]), int(contents[1][3:5])), stationName[0].upper() + stationName[1:], contents[5], contents[9], havePlatforms);
			mergeOrder(contents[0], order);
		except IndexError as e:
			print("Manual massaging needed:");
			print("File: {}".format(fileName));
			print(row);
			print("Error:");
			print(e);

for service in services:
	mergeService(services[service]);

print("version: 2");

print("services:");
for service in services:
	print("\t{}:".format(service));
	for order in services[service]:
		if order[5]:
			print("\t\t{}, {}, {}S{}".format(int(order[1] // 60), int(order[1] % 60), order[2], order[3]));
		else:
			print("\t\t{}, {}, {}".format(int(order[1] // 60), int(order[1] % 60), order[2]));
	print("\t:end");
print(":end");

print("trains:");
index = 0;
while len(servicesByTime) > 0:
	# add this service to the new schedule
	schedule = [servicesByTime.pop(0)];
	while True:
		lastOrder = schedule[-1][-1];
		newIndex = 0;
		for newService in servicesByTime:
			firstOrder = newService[0];
			
			# if the new service starts later than this one in the same station with the same train
			# note that we'll assume that trains can go between subsections of platforms (e.g. 12b -> 12a)
			if firstOrder[1] > lastOrder[1] and firstOrder[2] == lastOrder[2] and re.sub("\D", "", firstOrder[3]) == re.sub("\D", "", lastOrder[3]) and firstOrder[4] == lastOrder[4]:
				schedule.append(servicesByTime.pop(newIndex));
				break;
			
			newIndex += 1;
		else:
			break;
	
	# save the data
	print("\t{} {}:".format(schedule[0][0][4], index));
	
	for service in schedule:
		print("\t\t{}".format(service[0][0]));
	
	print("\t:end");
	sys.stdout.flush();
	
	index += 1;
print(":end");
