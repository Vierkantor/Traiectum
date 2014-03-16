#!/usr/bin/env python3

print("version: 2");

print("services:");
with open("LM.txt") as emptyTrains:
	for line in emptyTrains:
		fields = line.split("\t");
		days = fields[0];
		service = fields[1];
		trainType = fields[2];
		depTime = fields[3];
		depPlace = fields[4];
		arrTime = fields[5];
		arrPlace = fields[6];
		
		# check for tuesday
		if days[1] == 'D':
			print("\t{}:".format(service));
			print("\t\t{}, {}".format(depTime, depPlace));
			print("\t\t{}, {}".format(arrTime, arrPlace));
			print("\t:end");
print(":end");
