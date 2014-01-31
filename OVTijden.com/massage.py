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
			if havePlatforms:
				#        train id     - time                                              - S                      tation name             - track nr   - train type
				order = (contents[0], Time(int(contents[1][0:2]), int(contents[1][3:5])), stationName[0].upper() + stationName[1:] + "S" + contents[5], contents[9]);
			else:
				order = (contents[0], Time(int(contents[1][0:2]), int(contents[1][3:5])), stationName[0].upper() + stationName[1:], contents[9]);
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
		print("\t\t{}, {}, {}".format(int(order[1] // 60), int(order[1] % 60), order[2]));
	print("\t:end");
print(":end");

print("trains:");
index = 0;
for service in servicesByTime:
	# skip used services
	if service == None:
		newIndex += 1;
		continue;
	
	# add this service to the new schedule
	servicesByTime[index] = None;
	schedule = [service];
	while True:
		lastOrder = schedule[-1][-1];
		newIndex = 0;
		for newService in servicesByTime:
			if newService == None:
				newIndex += 1;
				continue;
			
			firstOrder = newService[0];
			
			# if the new service starts later than this one in the same station with the same train
			if firstOrder[1] > lastOrder[1] and firstOrder[2] == lastOrder[2] and firstOrder[3] == lastOrder[3]:
				schedule.append(newService);
				servicesByTime[newIndex] = None;
				break;
			
			newIndex += 1;
		else:
			break;
	
	# save the data
	print("\t{} {}:".format(schedule[0][0][3], index));
	
	for service in schedule:
		print("\t\t{}".format(service[0][0]));
	
	print("\t:end");
	sys.stdout.flush();
	
	index += 1;
print(":end");
