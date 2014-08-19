import codecs;
import re;
import sys;

import Data;
import Parser;
import Service;
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
	if isinstance(s, str):
		return [ tryint(c) for c in re.split('([0-9]+)', s, re.UNICODE) ]
	else:
		return s;

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    return sorted(l, key=lambda x: alphanum_key(x[0]))

def isSorted(list, key=lambda x: x):
	return all(key(list[i]) <= key(list[i + 1]) for i in range(len(list) - 1))

# gets (optional) attributes for a SimObject from the text
def ParseAttrs(text):
	try:
		text, _ = Parser.ParseFormat(text, [Parser.MatchText("[")]);
	except Parser.ParseError:
		return text, {};
	
	attrs = {};
	
	while True:
		try:
			text, values = Parser.ParseFormat(text, [Parser.MatchName, Parser.MatchText(":"), Parser.MatchName, Parser.MatchText(",")]);
		except Parser.ParseError:
			break;
		else:
			attrs[values[0]] = values[2];
	
	text, _ = Parser.ParseFormat(text, [Parser.MatchText("]")]);
	
	return text, attrs;

# writes these attributes to the data file
def SaveAttrs(data, attrs):
	data.write("\t\t[");
	for key in attrs:
		data.write("{}: {},".format(key, attrs[key]));
	data.write("]\n");

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
		if version == None or int(version.group(1)) not in [2, 3, 4, 5, 6]:
			raise Exception("Data file is of an invalid version! (Expected [2, 3, 4, 5], received {})".format(version.group(1)));
		else:
			text = Parser.StringSlice(text, version.end(0));
			version = int(version.group(1));
			
		# remove old data
		Service.services = {};
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
							
							Service.services[name] = Service.Add(time, Service.services[to]);
							continue;
						
						# define a service by all its stops and times
						try:
							text, values = Parser.ParseFormat(text, sectionStartSyntax);
						except Parser.ParseError:
							pass;
						else:
							name = values[0];
							
							# try to get its attributes
							text, attrs = ParseAttrs(text);
							
							# add a new service if this one hasn't been defined before (merging them otherwise)
							if name not in Service.services:
								Service.services[name] = Service.Service(attrs, name, []);
							
							service = Service.services[name];
							
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
									
									service.Append((Data.Time(hours, minutes), (place, platform)));
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
									
									service.Append((Data.Time(hours, minutes), (place, '')));
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
									
									service.Append((Data.Time(hours, minutes), (place, platform)));
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
									
									service.Append((Data.Time(hours, minutes), (place, '')));
									continue;
								
								# try matching the antique time format (when it was barely not hardcoded)
								try:
									text, values = Parser.ParseFormat(text, oldStopSyntax);
									
									hours = values[3];
									minutes = values[5];
									place = Data.places[values[9]];
									
									service.Append((Data.Time(hours, minutes), place));
									continue;
								except Parser.ParseError:
									pass;
								
								# and make sure there is an :end mark otherwise
								text, _ = Parser.ParseFormat(text, endSyntax);
								break;
							
							# make sure the orders are sorted (and warn if they aren't)
							if not isSorted(service.orders, key=lambda x: x[0]):
								sys.stderr.write("Warning: Orders for service {} are not in order!".format(name));
								sys.stderr.flush();
								service.orders.sort(key=lambda x: x[0]);
							
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
							for name in Service.services:
								for order in Service.services[name].orders:
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
							text, attrs = ParseAttrs(text);
							
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
								Data.trains[name] = Data.Train(attrs, name, trainData, Service.TrainSchedule(trainData));
							
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
	for name in Service.services:
		for stop in Service.services[name].orders:
			try:
				node = Data.nodes[Data.places[Data.Place(stop[1])]];
				if node.station != None:
					node.station.departures.append(name);
			except KeyError:
				raise KeyError("{} stops at non-existing place {}".format(name, stop[1]));

# "label": "name" (places, stations, links)
labelNameSyntax = [
	Parser.MatchName, Parser.MatchText(":"), Parser.MatchName,
];
nodeSyntax = [
	Parser.MatchName, Parser.MatchText(":"), Parser.MatchFloat, Parser.MatchText(","), Parser.MatchFloat,
];
namedNodeSyntax = [
	Parser.MatchName, Parser.MatchText(":"), Parser.MatchName, Parser.MatchText(":"), Parser.MatchFloat, Parser.MatchText(","), Parser.MatchFloat,
];
linkIntervalSyntax = [
	Parser.MatchInt, Parser.MatchText("..."), Parser.MatchInt,
];

def LoadData(loadIndicators = True, services = True):
	with codecs.open("data.txt", encoding="utf-8") as data:
		text = data.read()
		version = re.match("\s*version:\s*(\d+)", text, re.UNICODE);
		if version == None or int(version.group(1)) not in (5, 6):
			raise Exception("Data file is of an invalid version! (Expected [5], received {})".format(version.group(1)));
		else:
			text = Parser.StringSlice(text, version.end(0));
			version = int(version.group(1));
		
		while len(Parser.SkipWhitespace(text)) > 0:
			text, values = Parser.ParseFormat(text, sectionStartSyntax);
			section = values[0];
			
			if section == "places":
				if loadIndicators:
					print("Parsing places...");
				while True:
					try:
						text, values = Parser.ParseFormat(text, labelNameSyntax);
					except Parser.ParseError:
						pass;
					else:
						place = values[0];
						node = values[2];
						
						# make sure we don't overwrite existing places
						if place in Data.places:
							raise Exception("Duplicate location {}".format(place));
						
						Data.places[place] = node;
						continue;
					
					# detect the end of this section
					text, _ = Parser.ParseFormat(text, endSyntax);
					
					break;
			
			if section == "stations":
				if loadIndicators:
					print("Parsing stations...");
				while True:
					try:
						text, values = Parser.ParseFormat(text, labelNameSyntax);
					except Parser.ParseError:
						pass;
					else:
						station = values[0];
						place = values[2];
						text, attrs = ParseAttrs(text);
						
						if station not in Station.stations:
							Station.stations[station] = Station.Station(attrs, station); # this could be worded better, probably
						
						Station.stations[station].AddPlatform(place);
						continue;
					
					text, _ = Parser.ParseFormat(text, endSyntax);
					break;
			
			if section == "links":
				if loadIndicators:
					print("Parsing links...");
				while True:
					try:
						text, values = Parser.ParseFormat(text, linkIntervalSyntax);
					except Parser.ParseError:
						pass;
					else:
						begin = values[0];
						end = values[2];
						text, attrs = ParseAttrs(text);
						
						for x in range(begin, end):
							Data.AddLink(attrs, x, x + 1);
						
						continue;
					
					try:
						text, values = Parser.ParseFormat(text, labelNameSyntax);
					except Parser.ParseError:
						pass;
					else:
						link1 = values[0];
						link2 = values[2];
						text, attrs = ParseAttrs(text);
						
						Data.AddLink(attrs, link1, link2);
						continue;
					
					text, _ = Parser.ParseFormat(text, endSyntax);
					break;
			
			if section == "nodes":
				if loadIndicators:
					print("Parsing nodes...");
				while True:
					try:
						text, values = Parser.ParseFormat(text, namedNodeSyntax);
					except Parser.ParseError:
						pass;
					else:
						place = values[0];
						node = values[2];
						lat = values[4];
						lon = values[6];
						text, attrs = ParseAttrs(text);
						
						Data.nodes[node] = Data.Node(attrs, node, (lat, lon));
						
						if place in Data.places:
							raise Exception("Duplicate location {}".format(place));
						
						Data.places[place] = node;
						
						continue;
					
					try:
						text, values = Parser.ParseFormat(text, nodeSyntax);
					except Parser.ParseError:
						pass;
					else:
						node = values[0];
						lat = values[2];
						lon = values[4];
						text, attrs = ParseAttrs(text);
						
						Data.nodes[node] = Data.Node(attrs, node, (lat, lon));
						continue;
					
					text, _ = Parser.ParseFormat(text, endSyntax);
					break;
	
	if services:
		LoadServices(verify = True);
		GenerateDepartures();

def SaveData():
	with codecs.open("data.txt", "w", encoding="utf-8") as data:
		data.write(u"version: 6\n");
		
		data.write(u"nodes:\n");
		for node in sort_nicely(Data.nodes.items()):
			data.write(u"\t{0}: {1}, {2}\n".format(node[0], node[1].pos[0], node[1].pos[1]));
			SaveAttrs(data, node[1].attrs);
		data.write(u":end\n\n");
		
		data.write(u"links:\n");
		for begin in sort_nicely(Data.links.items()):
			for end in sort_nicely(begin[1].items()):
				data.write(u"\t{0}: {1}\n".format(begin[0], end[0]));
				SaveAttrs(data, end[1].attrs);
		data.write(u":end\n\n");
		
		data.write(u"places:\n");
		for place in sort_nicely(Data.places.items()):
			data.write(u"\t{0}: {1}\n".format(place[0], place[1]));
		data.write(u":end\n\n");
		
		data.write(u"stations:\n");
		for place in sort_nicely(Station.stations.items()):
			for platform in sort_nicely(place[1].platforms):
				data.write(u"\t{0}: {1}\n".format(place[1].name, platform));
				SaveAttrs(data, place[1].attrs);
		data.write(u":end\n\n");
		
	with codecs.open("servicedata.txt", "w", encoding="utf-8") as data:
		data.write(u"version: 6\n");
		data.write(u"# Generated automatically by Traiectum\n");
		
		data.write("services:\n");
		for item in sort_nicely(Service.services.items()):
			service = item[1];
			data.write(u"\t{0}:\n".format(service.name));
			SaveAttrs(data, service.attrs);
			for order in service.orders:
				if order[1][1] != '':
					data.write(u"\t\t{0}, {1}, {2}, {3}\n".format(int(order[0] // 60), int(order[0] % 60), order[1][0], order[1][1]));
				else:
					data.write(u"\t\t{0}, {1}, {2}\n".format(int(order[0] // 60), int(order[0] % 60), order[1][0]));
			data.write(u"\t:end\n\n");
		data.write(u":end\n\n");
		
		data.write(u"trains:\n");
		for train in sort_nicely(Data.trains.items()):
			data.write(u"\t{0}:\n".format(train[1].composition));
			SaveAttrs(data, train[1].attrs);
			for service in train[1].serviceNames:
				data.write(u"\t\t{0}\n".format(service));
			data.write(u"\t:end\n\n");
		data.write(u":end\n\n");
