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
			#        train id     - time                                              - S                      tation name      - track nr   - train type - has platforms
			order = (contents[0], Time(int(contents[1][0:2]), int(contents[1][3:5])), stationName[0].upper() + stationName[1:], contents[5], contents[9], havePlatforms);
			mergeOrder(contents[0], order);
		except IndexError as e:
			print("Manual massaging needed:");
			print("File: {}".format(fileName));
			print(row);
			print("Error:");
			print(e);

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
