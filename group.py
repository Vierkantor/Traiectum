#!/usr/bin/env python3

import os;
import re;

import Data;
import Filefunc;

# Groups all the different service data files together into one big one
# And use them to automatically produce the trains
services = {};
servicesByTime = [];

# sorts the services by departure time
def mergeService(serviceName, serviceData):
	# find the insertion point
	index = 0;
	for service in servicesByTime:
		if service[1][0][0] > serviceData[0][0]:
			break;
		index += 1;
	
	# insert before the later service
	servicesByTime.insert(index, (serviceName, serviceData));

for fileName in os.listdir("DataSources"):
	# only load data files
	if not fileName.endswith(".txt"):
		continue;
	
	# get all the services in that file
	Filefunc.LoadServices(filename = os.path.join("DataSources", fileName), loadIndicators = False);
	for service in Data.services:
		# make a secret copy for ourselves
		services[service] = Data.services[service];
		mergeService(service, Data.services[service]);

# write it all down
print("version: 2");

# we've already got all the services, so this one is easy
print("services:");
for service in services:
	print("\t{}:".format(service));
	
	for stop in services[service]:
		print("\t\t{}, {}, {}".format(int(stop[0]) // 60, int(stop[0]) % 60, stop[1]));
	
	print("\t:end");

print(":end");

print("trains:");
index = 0;
while len(servicesByTime) > 0:
	# add this service to the new schedule
	schedule = [servicesByTime.pop(0)];
	while True:
		lastOrder = schedule[-1][1][-1];
		newIndex = 0;
		for newService in servicesByTime:
			firstOrder = newService[1][0];
			
			# if the new service starts later than this one in the same station with the same train
			if firstOrder[0] > lastOrder[0] and firstOrder[1] == lastOrder[1]:
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