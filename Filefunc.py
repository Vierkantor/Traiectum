import re;

import Data;

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
		Data.services = {};
		Data.trainCompositions = {};
		Data.trains = {};
		
		section = re.match("\s*(\w+):\s*", text);
		while section != None:
			text = text[section.end(0):];
			
			if section.group(1) == "places":
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
	
			if section.group(1) == "links":
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
					raise Exception("Invalid syntax near {}".format(text));
	
			if section.group(1) == "nodes":
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					nodeData = re.match("\s*(\w+)\s*->\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text);
					if nodeData != None:
						Data.nodes[int(nodeData.group(2))] = (float(nodeData.group(3)), float(nodeData.group(4)));
						Data.places[nodeData.group(1)] = int(nodeData.group(2));
						
						text = text[nodeData.end(0):];
						continue;
					
					nodeData = re.match("\s*(\d+)\s*->\s*(\-?[\d\.]+)\s*,\s*(\-?[\d\.]+)", text);
					if nodeData != None:
						Data.nodes[int(nodeData.group(1))] = (float(nodeData.group(2)), float(nodeData.group(3)));
						
						text = text[nodeData.end(0):];
						continue;
					
					raise Exception("Syntax error near {0}".format(text));
	
			if section.group(1) == "services":
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;

					addService = re.match("\s*([^:]+)\:\s*[Aa][Dd][Dd]\s*\(\s*(\d+)\s*\,\s*([^\:\)]+)\s*\)", text);
					if addService != None:
						name = addService.group(1);
						time = int(addService.group(2));
						to = addService.group(3);
						Data.services[name] = Data.Add(time, Data.services[to]);
						
						text = text[addService.end(0):];
						continue;
					
					serviceName = re.match("\s*([^:]+)\:\s*", text);
					if serviceName != None:
						name = serviceName.group(1);
						if name not in Data.services:
							Data.services[name] = [];
						
						text = text[serviceName.end(0):];
						while True:
							endMark = re.match("\s*\:end", text);
							if endMark != None:
								text = text[endMark.end(0):];
								break;
							
							timeData = re.match("\s*0*(\d+)\s*[,:]\s*0*(\d+)\s*,\s*(.+)", text);
							if timeData != None:
								if version == 1:
									Data.services[name].append((Data.Time(int(timeData.group(1)), int(timeData.group(2))), int(timeData.group(3))));
								else:
									Data.services[name].append((Data.Time(int(timeData.group(1)), int(timeData.group(2))), Data.places[timeData.group(3)]));									
								
								text = text[timeData.end(0):];
							else:
								timeData = re.match("\s*\(\s*Time\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*,\s*\"(.+)\"\s*\)\s*\,", text);
								if timeData != None:
									Data.services[name].append((Data.Time(int(timeData.group(1)), int(timeData.group(2))), Data.places[timeData.group(3)]));									
									text = text[timeData.end(0):];
								else:
									raise Exception("Syntax error near " + text);
						continue;
			
			if section.group(1) == "trains":
				while True:
					endMark = re.match("\s*\:end", text);
					if endMark != None:
						text = text[endMark.end(0):];
						break;
					
					trainName = re.match("\s*([^:]+)\:\s*", text);
					if trainName != None:
						name = trainName.group(1);
						
						trainData = [];
						text = text[trainName.end(0):];
						while True:
							endMark = re.match("\s*\:end", text);
							if endMark != None:
								if name in Data.trains:
									Data.trains[name].serviceName.extend(trainData);
								else:
									Data.trains[name] = Data.Train(name, trainData, Data.Join(trainData));
								text = text[endMark.end(0):];
								break;
							
							serviceData = re.match("\s*([^:\s]+)", text);
							if serviceData != None:
								trainData.append(serviceData.group(1));
								
								text = text[serviceData.end(0):];
								continue;
							
							raise Exception("Syntax error near " + text);
	
			section = re.match("\s*(\w+):", text);

def SaveData():
	with open("data.txt", "w") as data:
		data.write("version: 2\n");
		
		data.write("nodes:\n");
		for node in sort_nicely(Data.nodes.items()):
			data.write("\t{0} -> {1}, {2}\n".format(node[0], node[1][0], node[1][1]));
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
