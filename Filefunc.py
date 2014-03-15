import re;
import sys;

import Data;
import Parser;
import Station;

def tryint(s):
    try:
        return int(s)
    except:
        return s
     
def alphanum_key(s):
	""" Turn a string into a list of string and number chunks.
		"z23a" -> ["z", 23, "a"]
	"""
	if isinstance(s, str):
		return [ tryint(c) for c in re.split('([0-9]+)', s) ]
	else:
		return s;

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    return sorted(l, key=lambda x: alphanum_key(x[0]))

sectionStartSyntax = [
	Parser.MatchName, Parser.MatchText(":"),
];

endSyntax = [
	Parser.MatchText(":end")
];

addServiceSyntax = [
	Parser.MatchName, Parser.MatchText(":"), # new service name
	Parser.MatchText("Add"), Parser.MatchText("("), Parser.MatchInt, # minutes of difference
	Parser.MatchText(","), Parser.MatchName, Parser.MatchText(")"), # old service
];

newStopSyntax = [
	Parser.MatchInt, Parser.MatchText(","), Parser.MatchInt, Parser.MatchText(","), # time
	Parser.MatchName, # place
];

newStopFancyTimeSyntax = [
	Parser.MatchInt, Parser.MatchText(":"), Parser.MatchInt, Parser.MatchText(","), # time
	Parser.MatchName, # place
];

oldStopSyntax = [
	Parser.MatchText("("), Parser.MatchText("Time"), Parser.MatchText("("), # start of stop
	Parser.MatchInt, Parser.MatchText(","), Parser.MatchInt, # time
	Parser.MatchText(")"), Parser.MatchText(","), # end of time
	Parser.MatchText('"'), Parser.MatchName, Parser.MatchText('"'), # name
	Parser.MatchText(")"), Parser.MatchText(","), # end of stop
];

def LoadServices(filename = "servicedata.txt"):
	with open(filename) as data:
		text = data.read();
		version = re.match("\s*version:\s*(\d+)", text);
		if version == None or int(version.group(1)) > 2:
			raise Exception("Data file is of an invalid version! (Expected [1, 2], received {})".format(version.group(1)));
		else:
			text = Parser.StringSlice(text, version.end(0));
			version = int(version.group(1));
			
		# remove old data
		Data.services = {};
		Data.trainCompositions = {};
		Data.trains = {};
		
		try:
			while len(Parser.SkipWhitespace(text)) > 0:
				text, values = Parser.ParseFormat(text, sectionStartSyntax);
				section = values[0];
				
				if section == "services":
					sys.stdout.write("Parsing services.");
					sys.stdout.flush();
					parseCount = 0;
					
					while True:
						parseCount += 1;
						if parseCount % 100 == 0:
							sys.stdout.write("\rParsing services." + "." * (parseCount // 100));
							sys.stdout.flush();
						
						# add a number of minutes to another service (handy for manual input of services)
						try:
							text, values = Parser.ParseFormat(text, addServiceSyntax);
						except Parser.ParseError:
							pass;
						else:
							name = values[0];
							time = values[4];
							to = values[6];
							
							Data.services[name] = Data.Add(time, Data.services[to]);
							continue;
						
						# define a service by all its stops and times
						try:
							text, values = Parser.ParseFormat(text, sectionStartSyntax);
						except Parser.ParseError:
							pass;
						else:
							name = values[0];
							
							# add a new service if this one hasn't been defined before (merging them otherwise)
							if name not in Data.services:
								Data.services[name] = [];
							
							# find all the stops in the service
							while True:
								
								# try matching the new time format
								try:
									text, values = Parser.ParseFormat(text, newStopSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									if version == 1:
										place = int(values[4]);
									else:
										try:
											place = Data.places[values[4]];
										except KeyError:
											raise KeyError("Place {} does not exist when defining service {}".format(values[4], name));
									
									Data.services[name].append((Data.Time(hours, minutes), place));
									continue;
								
								# support colons for time as well
								try:
									text, values = Parser.ParseFormat(text, newStopFancyTimeSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									if version == 1:
										place = int(values[4]);
									else:
										try:
											place = Data.places[values[4]];
										except KeyError:
											raise KeyError("Place {} does not exist when defining service {}".format(values[4], name));
									
									Data.services[name].append((Data.Time(hours, minutes), place));
									continue;
								
								# try matching the antique time format (when it was barely not hardcoded)
								try:
									text, values = Parser.ParseFormat(text, oldStopSyntax);
									
									hours = values[3];
									minutes = values[5];
									place = Data.places[values[9]];
									
									Data.services[name].append((Data.Time(hours, minutes), place));
									continue;
								except Parser.ParseError:
									pass;
								
								# and make sure there is an :end mark otherwise
								text, _ = Parser.ParseFormat(text, endSyntax);
								break;
						
							Data.services[name].sort(key=lambda x: x[0]);
							continue;
						
						# make sure we hit an :end mark
						text, _ = Parser.ParseFormat(text, endSyntax);
						print("");
						break;
			
				if section == "trains":
					print("Parsing trains...");
					while True:
						# train:
						try:
							text, values = Parser.ParseFormat(text, sectionStartSyntax);
						except Parser.ParseError:
							pass;
						else:
							name = values[0];
							
							# get all the services the train runs
							trainData = [];
							while True:
								try:
									text, serviceName = Parser.MatchName(text);
								except Parser.ParseError:
									pass;
								else:
									trainData.append(serviceName);
									continue;
								
								# make sure we hit an :end mark
								text, _ = Parser.ParseFormat(text, endSyntax);
								break;
						
							# and save it all
							if name in Data.trains:
								Data.trains[name].serviceName.extend(trainData);
							else:
								Data.trains[name] = Data.Train(name, trainData, Data.Join(trainData));
							
							continue;
						
						# make sure we hit an :end mark
						text, _ = Parser.ParseFormat(text, endSyntax);
						break;
		
		
		except:
			print("In servicedata.txt, near:");
			print(text[:100]);
			raise;

def LoadData():
	with open("data.txt") as data:
		text = data.read();
		version = re.match("\s*version:\s*(\d+)", text);
		if version == None or int(version.group(1)) > 2:
			raise Exception("Data file is of an invalid version! (Expected [1, 2], received {})".format(version.group(1)));
		else:
			text = text[version.end(0):];
			version = int(version.group(1));
			
		# remove old data
		Data.nodes = {};
		Data.places = {};
		Data.links = {};
		
		section = re.match("\s*(\w+):\s*", text);
		while section != None:
			text = text[section.end(0):];
			
			if section.group(1) == "places":
				print("Parsing places...");
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					placeData = re.match("\s*(\w+)\s*->\s*(\d+)", text);
					if placeData != None:
						Data.places[placeData.group(1)] = int(placeData.group(2));
						
						text = text[placeData.end(0):];
						continue;
			
			if section.group(1) == "stations":
				print("Parsing stations...");
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					placeData = re.match("\s*(\w+)\s*->\s*(\w+)", text);
					if placeData != None:
						if placeData.group(1) not in Station.stations:
							Station.stations[placeData.group(1)] = Station.Station(placeData.group(1));
					
						Station.stations[placeData.group(1)].AddPlatform(placeData.group(2));
						
						text = text[placeData.end(0):];
						continue;
	
			if section.group(1) == "links":
				print("Parsing links...");
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					linkData = re.match("\s*(\d+)\s*,\s*(\d+)", text);
					if linkData != None:
						link1 = int(linkData.group(1));
						link2 = int(linkData.group(2));
						Data.AddLink(link1, link2);
						
						text = text[linkData.end(0):];
						continue;
					raise Exception("Invalid syntax near {}".format(text[:100]));
	
			if section.group(1) == "nodes":
				print("Parsing nodes...");
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					nodeData = re.match("\s*(\w+)\s*->\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text);
					if nodeData != None:
						Data.nodes[int(nodeData.group(2))] = Data.Node(int(nodeData.group(2)), (float(nodeData.group(3)), float(nodeData.group(4))));
						Data.places[nodeData.group(1)] = int(nodeData.group(2));
						
						text = text[nodeData.end(0):];
						continue;
					
					nodeData = re.match("\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text);
					if nodeData != None:
						Data.nodes[int(nodeData.group(1))] = Data.Node(int(nodeData.group(1)), (float(nodeData.group(2)), float(nodeData.group(3))));
						
						text = text[nodeData.end(0):];
						continue;
					
					raise Exception("Syntax error near {0}".format(text[:100]));
				
			section = re.match("\s*(\w+):", text);
		LoadServices();

def SaveData():
	with open("data.txt", "w") as data:
		data.write("version: 2\n");
		
		data.write("nodes:\n");
		for node in sort_nicely(Data.nodes.items()):
			data.write("\t{0} -> {1}, {2}\n".format(node[0], node[1].pos[0], node[1].pos[1]));
		data.write(":end\n\n");
		
		data.write("links:\n");
		for link in sort_nicely(Data.links.items()):
			for node in sorted(link[1]):
				data.write("\t{0}, {1}\n".format(link[0], node));
		data.write(":end\n\n");
		
		data.write("places:\n");
		for place in sort_nicely(Data.places.items()):
			data.write("\t{0} -> {1}\n".format(place[0], place[1]));
		data.write(":end\n\n");
		
		data.write("stations:\n");
		for place in sort_nicely(Station.stations.items()):
			for platform in sort_nicely(place[1].platforms):
				data.write("\t{0} -> {1}\n".format(place[1].name, platform));
		data.write(":end\n\n");
		
	with open("servicedata.txt", "w") as data:
		data.write("version: 2\n");
		
		data.write("services:\n");
		inversePlaces = dict((v, k) for k, v in Data.places.items());
		for service in sort_nicely(Data.services.items()):
			data.write("\t{0}:\n".format(service[0]));
			for order in service[1]:
				data.write("\t\t{0}, {1}, {2}\n".format(int(order[0] // 60), int(order[0] % 60), inversePlaces[order[1]]));
			data.write("\t:end\n\n");
		data.write(":end\n\n");
		
		data.write("trains:\n");
		for train in sort_nicely(Data.trains.items()):
			data.write("\t{0}:\n".format(train[1].composition));
			for service in train[1].serviceName:
				data.write("\t\t{0}\n".format(service));
			data.write("\t:end\n\n");
			
			print(train[1].composition, Data.services[train[1].serviceName[0]][0], Data.services[train[1].serviceName[-1]][-1]);
		data.write(":end\n\n");
