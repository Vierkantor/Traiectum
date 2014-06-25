#!/usr/bin/env python3

import os;
import re;

import Data;
import Filefunc;

# Groups all the different service data files together into one big one
# And use them to automatically produce the trains
services = {};

# the list of files we got data from
sources = [];

def sameStation(a, b):
	if a == b: # either the same station + track
		return True;
	
	if a[0] != b[0]: # or the same station
		return False;
	
	if a[1] == '' or b[1] == '': # with one missing their track nr
		return True;
	
	return a[1][:len(b[1])] == b[1][:len(a[1])];

for fileName in os.listdir("DataSources"):
	# only load data files
	if not fileName.endswith(".txt"):
		continue;
	
	sources.append(fileName);
	
	# get all the services in that file
	Filefunc.LoadServices(filename = os.path.join("DataSources", fileName), loadIndicators = False);
	for service in Data.services:
		# make a secret copy for ourselves
		if service in services:
			# add to existing service data
			services[service].extend(Data.services[service]);
			# in the correct order
			services[service].sort(key=lambda order: order[0]);
		else:
			services[service] = Data.services[service];

# write it all down
print("version: 5");
print("#Generated by group.py from the following base files:");

for source in sources:
	print("#\t{}".format(source));

# we've already got all the services, so this one is easy
print("services:");
for service in services:
	print("\t{}:".format(service));
	
	for stop in services[service]:
		if stop[1][1] != '':
			print("\t\t{}, {}, {}, {}".format(int(stop[0]) // 60, int(stop[0]) % 60, stop[1][0], stop[1][1]));
		else:
			print("\t\t{}, {}, {}".format(int(stop[0]) // 60, int(stop[0]) % 60, stop[1][0]));
	
	print("\t:end");

print(":end");

# sort the services for easier searching of departures
servicesByTime = sorted(services.items(), key=lambda x: (x[1], x[0]));

print("trains:");
index = 0;
while len(servicesByTime) > 0:
	# add this service to the new schedule
	schedule = [servicesByTime.pop(0)];
	while True:
		lastOrder = schedule[-1][1][-1];
		newIndex = 0;
		
		# find the next service to depart at the arrival station
		for newService in servicesByTime:
			firstOrder = newService[1][0];
			
			# if the new service starts later than this one in the same station with the same train
			if firstOrder[0] > lastOrder[0] and sameStation(firstOrder[1], lastOrder[1]):
				schedule.append(servicesByTime.pop(newIndex));
				break;
			
			newIndex += 1;
		else:
			break;
	
	# save the data
	print("\t{}:".format(index));
	
	for service in schedule:
		print("\t\t{}".format(service[0]));
	
	print("\t:end");
	
	index += 1;
print(":end");
