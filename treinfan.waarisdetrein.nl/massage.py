#!/usr/bin/env python3

print("version: 6");

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
			if trainType != "?":
				print("\t\t[stock: {},]".format(trainType));
			print("\t\t{}, {}".format(depTime, depPlace));
			print("\t\t{}, {}".format(arrTime, arrPlace));
			print("\t:end");

with open("mat.txt") as data:
	for line in data:
		fields = line.split("\t");
		for i in range(0, len(fields) // 3): # format: (days \t service \t type \t)+
			days = fields[i + 0];
			service = fields[i + 1];
			trainType = fields[i + 2];
			
			# check for tuesday
			if days[1] == 'D':
				print("\t{}:".format(service));
				if trainType != "?":
					print("\t\t[stock: {},]".format(trainType));
				print("\t:end");
print(":end");
