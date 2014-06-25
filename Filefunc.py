import codecs;
import re;
import sys;

import Data;
import Parser;
import Station;

# fix Python2's bad range() function
try:
	range = xrange;
except NameError:
	pass;

def tryint(s):
    try:
        return int(s)
    except:
        return s
     
def alphanum_key(s):
	""" Turn a string into a list of string and number chunks.
		"z23a" -> ["z", 23, "a"]
	"""
	if isinstance(s, str) or isinstance(s, unicode):
		return [ tryint(c) for c in re.split('([0-9]+)', s, re.UNICODE) ]
	else:
		return s;

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    return sorted(l, key=lambda x: alphanum_key(x[0]))

def isSorted(list, key=lambda x: x):
	return all(key(list[i]) <= key(list[i + 1]) for i in range(len(list) - 1))

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

newStopWithPlatformSyntax = [
	Parser.MatchInt, Parser.MatchText(","), Parser.MatchInt, Parser.MatchText(","), # time
	Parser.MatchName, Parser.MatchText(","), # place
	Parser.MatchName, # platform
];

newStopFancyTimeWithPlatformSyntax = [
	Parser.MatchInt, Parser.MatchText(":"), Parser.MatchInt, Parser.MatchText(","), # time
	Parser.MatchName, Parser.MatchText(","), # place
	Parser.MatchName, # platform
];

oldStopSyntax = [
	Parser.MatchText("("), Parser.MatchText("Time"), Parser.MatchText("("), # start of stop
	Parser.MatchInt, Parser.MatchText(","), Parser.MatchInt, # time
	Parser.MatchText(")"), Parser.MatchText(","), # end of time
	Parser.MatchText('"'), Parser.MatchName, Parser.MatchText('"'), # name
	Parser.MatchText(")"), Parser.MatchText(","), # end of stop
];

def LoadServices(filename = "servicedata.txt", loadIndicators = True, verify = False):
	with codecs.open(filename, encoding="utf-8") as data:
		text = data.read();
		version = re.match("\s*version:\s*(\d+)", text);
		if version == None or int(version.group(1)) not in [2, 3, 4, 5]:
			raise Exception("Data file is of an invalid version! (Expected [2, 3, 4, 5], received {})".format(version.group(1)));
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
					if loadIndicators:
						sys.stdout.write("Parsing services.");
						sys.stdout.flush();
					parseCount = 0;
					
					while True:
						parseCount += 1;
						if parseCount % 100 == 0 and loadIndicators:
							sys.stdout.write("\rParsing services." + "." * (parseCount // 200));
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
								
								# try matching the new time format with a platform
								try:
									text, values = Parser.ParseFormat(text, newStopWithPlatformSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									place = values[4];
									platform = values[6];
									
									Data.services[name].append((Data.Time(hours, minutes), (place, platform)));
									continue;
								
								# or without a platform
								try:
									text, values = Parser.ParseFormat(text, newStopSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									place = values[4];
									
									Data.services[name].append((Data.Time(hours, minutes), (place, '')));
									continue;
								
								# support colons for time as well
								try:
									text, values = Parser.ParseFormat(text, newStopFancyTimeWithPlatformSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									place = values[4];
									platform = values[6];
									
									Data.services[name].append((Data.Time(hours, minutes), (place, platform)));
									continue;
								
								# or without a platform
								try:
									text, values = Parser.ParseFormat(text, newStopFancyTimeSyntax);
								except Parser.ParseError:
									pass;
								else:
									hours = values[0];
									minutes = values[2];
									place = values[4];
									
									Data.services[name].append((Data.Time(hours, minutes), (place, '')));
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
							
							# make sure the orders are sorted (and warn if they aren't)
							if not isSorted(Data.services[name], key=lambda x: x[0]):
								sys.stderr.write("Warning: Orders for service {} are not in order!".format(name));
								sys.stderr.flush();
								Data.services[name].sort(key=lambda x: x[0]);
							
							continue;
						
						# make sure we hit an :end mark
						text, _ = Parser.ParseFormat(text, endSyntax);
						if loadIndicators:
							print("");
						
						if verify:
							# make sure the stops are all correct
							if loadIndicators:
								print("Verifying places...");
							errors = set();
							for service in Data.services:
								for order in Data.services[service]:
									if Data.Place(order[1]) not in Data.places:
										errors.add(str(order[1]));
						
							if errors:
								raise Exception("Places not found:\n{}".format("\n".join(errors)));
						
						break;
				
				if section == "trains":
					if loadIndicators:
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
			print("In {}, near:".format(filename));
			print(text[:100]);
			raise;

# creates the stations' departure list
def GenerateDepartures():
	for service in Data.services:
		for stop in Data.services[service]:
			try:
				node = Data.nodes[Data.places[Data.Place(stop[1])]];
				if node.station != None:
					node.station.departures.append(service);
			except KeyError:
				raise KeyError("{} stops at non-existing place {}".format(service, stop[1]));

def LoadData(loadIndicators = True, services = True):
	with codecs.open("data.txt", encoding="utf-8") as data:
		text = data.read()
		version = re.match("\s*version:\s*(\d+)", text, re.UNICODE);
		if version == None or int(version.group(1)) > 3:
			raise Exception("Data file is of an invalid version! (Expected [1, 2, 3], received {})".format(version.group(1)));
		else:
			text = text[version.end(0):];
			version = int(version.group(1));
			
		# remove old data
		Data.nodes = {};
		Data.places = {};
		Data.links = {};
		
		section = re.match("\s*(\w+):\s*", text, re.UNICODE);
		while section != None:
			text = text[section.end(0):];
			
			if section.group(1) == "places":
				if loadIndicators:
					print("Parsing places...");
				while True:
					endMark = re.match("\s*\:end", text, re.UNICODE);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					placeData = re.match("\s*(\w+)\s*->\s*(\d+)", text, re.UNICODE);
					if placeData != None:
						Data.places[placeData.group(1)] = int(placeData.group(2));
						
						text = text[placeData.end(0):];
						continue;
			
			if section.group(1) == "stations":
				if loadIndicators:
					print("Parsing stations...");
				while True:
					endMark = re.match("\s*\:end", text, re.UNICODE);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					placeData = re.match("\s*(\w+)\s*->\s*(\w+)", text, re.UNICODE);
					if placeData != None:
						if placeData.group(1) not in Station.stations:
							Station.stations[placeData.group(1)] = Station.Station(placeData.group(1));
					
						Station.stations[placeData.group(1)].AddPlatform(placeData.group(2));
						
						text = text[placeData.end(0):];
						continue;
			
			if section.group(1) == "links":
				if loadIndicators:
					print("Parsing links...");
				while True:
					endMark = re.match("\s*\:end", text, re.UNICODE);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					linkData = re.match("\s*(\d+)\s*,\s*(\d+)", text, re.UNICODE);
					if linkData != None:
						link1 = int(linkData.group(1));
						link2 = int(linkData.group(2));
						Data.AddLink(link1, link2);
						
						text = text[linkData.end(0):];
						continue;
					raise Exception("Invalid syntax near {}".format(text[:100]));
			
			if section.group(1) == "nodes":
				if loadIndicators:
					print("Parsing nodes...");
				while True:
					endMark = re.match("\s*\:end", text, re.UNICODE);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					nodeData = re.match("\s*(\w+)\s*->\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text, re.UNICODE);
					if nodeData != None:
						Data.nodes[int(nodeData.group(2))] = Data.Node(int(nodeData.group(2)), (float(nodeData.group(3)), float(nodeData.group(4))));
						Data.places[nodeData.group(1)] = int(nodeData.group(2));
						
						text = text[nodeData.end(0):];
						continue;
					
					nodeData = re.match("\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text, re.UNICODE);
					if nodeData != None:
						Data.nodes[int(nodeData.group(1))] = Data.Node(int(nodeData.group(1)), (float(nodeData.group(2)), float(nodeData.group(3))));
						
						text = text[nodeData.end(0):];
						continue;
					
					raise Exception("Syntax error near {0}".format(repr(text[:100])));
				
			section = re.match("\s*(\w+):", text, re.UNICODE);
	
	if services:
		LoadServices(verify = True);
		GenerateDepartures();

def SaveData():
	with codecs.open("data.txt", "w", encoding="utf-8") as data:
		data.write(u"version: 3\n");
		
		data.write(u"nodes:\n");
		for node in sort_nicely(Data.nodes.items()):
			data.write(u"\t{0} -> {1}, {2}\n".format(node[0], node[1].pos[0], node[1].pos[1]));
		data.write(u":end\n\n");
		
		data.write(u"links:\n");
		for link in sort_nicely(Data.links.items()):
			for node in sorted(link[1]):
				data.write(u"\t{0}, {1}\n".format(link[0], node));
		data.write(u":end\n\n");
		
		data.write(u"places:\n");
		for place in sort_nicely(Data.places.items()):
			data.write(u"\t{0} -> {1}\n".format(place[0], place[1]));
		data.write(u":end\n\n");
		
		data.write(u"stations:\n");
		for place in sort_nicely(Station.stations.items()):
			for platform in sort_nicely(place[1].platforms):
				data.write(u"\t{0} -> {1}\n".format(place[1].name, platform));
		data.write(u":end\n\n");
		
	with codecs.open("servicedata.txt", "w", encoding="utf-8") as data:
		data.write(u"version: 4\n");
		data.write(u"# Generated automatically by Traiectum\n");
		
		data.write("services:\n");
		for service in sort_nicely(Data.services.items()):
			data.write(u"\t{0}:\n".format(service[0]));
			for order in service[1]:
				if order[1][1] != '':
					data.write(u"\t\t{0}, {1}, {2}, {3}\n".format(int(order[0] // 60), int(order[0] % 60), order[1][0], order[1][1]));
				else:
					data.write(u"\t\t{0}, {1}, {2}\n".format(int(order[0] // 60), int(order[0] % 60), order[1][0]));
			data.write(u"\t:end\n\n");
		data.write(u":end\n\n");
		
		data.write(u"trains:\n");
		for train in sort_nicely(Data.trains.items()):
			data.write(u"\t{0}:\n".format(train[1].composition));
			for service in train[1].serviceName:
				data.write(u"\t\t{0}\n".format(service));
			data.write(u"\t:end\n\n");
		data.write(u":end\n\n");
