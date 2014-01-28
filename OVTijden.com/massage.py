#!/usr/bin/python3
import os;
import re;

from bs4 import BeautifulSoup;

def getRows(htmldoc):
    soup = BeautifulSoup(htmldoc);
    return soup.findAll('tr');

def mergeOrder(service, order):
	if service not in services:
		services[service] = [];
	if order not in services[service]:
		services[service].append(order);

def mergeService(train, service):
	if train not in trains:
		trains[train] = [];
	if service not in trains[train]:
		trains[train].append(service);

trains = {};
services = {};

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
				mergeOrder(contents[0], (contents[1], stationName[0].upper() + stationName[1:], contents[5]));
			else:
				mergeOrder(contents[0], (contents[1], stationName[0].upper() + stationName[1:]));
			mergeService(contents[9] + " " + contents[0], contents[0]);
		except IndexError:
			print("Manual massaging needed:");
			print("File: {}".format(fileName));
			print(row);

print("version: 2");

print("services:");
for service in services:
	print("\t{}:".format(service));
	for order in services[service]:
		if len(order) >= 3:
			print("\t\t{}, {}S{}".format(order[0], order[1], order[2]));
		else:
			print("\t\t{}, {}".format(order[0], order[1]));
	print("\t:end");
print(":end");

print("trains:");
for train in trains:
	print("\t{}:".format(train));
	for service in trains[train]:
		print("\t\t{}".format(service));
	print("\t:end");
print(":end");
