#!/usr/bin/python3
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

files = ["ac", "apn", "atn", "bsk", "gd", "ut", "wad", "wadn", "wd"];

for fileName in files:
	with open("{}.txt".format(fileName)) as data:
		text = data.read();

	rows = getRows(text);
	for row in rows:
		contents = [];
		columns = row.findAll('td');
		for column in columns:
			contents.append(''.join(column.findAll(text=True)));
	
		try:
			mergeOrder(contents[0], (contents[1], fileName[0].upper() + fileName[1:], contents[5]));
			mergeService(contents[9] + " " + contents[0], contents[0]);
		except IndexError:
			print("Manual massaging needed:");
			print("File: {}.txt".format(fileName));
			print(row);

print("version: 2");

print("services:");
for service in services:
	print("\t{}:".format(service));
	for order in services[service]:
		print("\t\t{}, {}S{}".format(order[0], order[1], order[2]));
	print("\t:end");
print(":end");

print("trains:");
for train in trains:
	print("\t{}:".format(train));
	for service in trains[train]:
		print("\t\t{}".format(service));
	print("\t:end");
print(":end");
