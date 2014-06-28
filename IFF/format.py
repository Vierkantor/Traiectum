#!/usr/bin/env python3

# parses the IFF data into a working servicedata.txt formatted file

# IFF is not a nice format. Even the current thrown-together format Traiectum uses is better. Even XML is better. Even COBOL programmers can create better data formats. You get a directory of files whose names are a suspicious maximum of 8 characters long plus a dot plus three characters. Let's talk about the format of the files themselves. Data is stored in what is essentially a comma-separated file, but with constant column width. The first character in every line indicates what kind of data follows in a way more opaque than a kilometer of compressed concrete. Of course, this value is not comma-separated. The specification has its indices being 1-based and lists of numbers being of the form [start ... end], instead of what Dijkstra commanded in [EWD831](https://www.cs.utexas.edu/users/EWD/transcriptions/EWD08xx/EWD831.html). The text is in Latin-1 and is terminated with CRLF. Now of course, the data in each file is handled even worse. Instead of indicating, say, the day of week a service is valid, you get to read and parse a big file consisting only of giant strings of 0 and 1, indicating when the service is valid for every day that the timetable is valid. So now you have a table of about a megabyte consisting only of footnotes somewhere in your memory, and you haven't even started reading the actual trains.
# 
# I not like IFF and it is a bad format.

# of course you have to backtrack whole lines in this format, why wouldn't you?
class BackTrackFile:
	def __init__(self, file):
		self.file = file;
		self.index = 0;
	
	def __enter__(self):
		self.file.__enter__();
		return self;
	
	def __exit__(self, type, value, traceback):
		return self.file.__exit__(type, value, traceback);
	
	def readline(self):
		self.index = self.file.tell();
		return self.file.readline();
	
	def BackTrack(self):
		self.file.seek(self.index);
	
	def __getattr__(self, name):
		return self.file.__getattribute__(name);

# split and validate a line of data following the given format
# d: digit
# w: word
# other: literal character (is not returned)
def ParseLine(format, line):
	i = 0;
	result = [];
	
	while i < len(format):
		if format[i] == 'd':
			begin = i;
			while i < len(format) and format[i] == 'd':
				if line[i] not in "0123456789":
					raise Exception("Line not conforming to spec:\n{}\n{}^\n{}".format(line, " " * i, format));
				
				i += 1;
			
			result.append(int(line[begin:i]));
		elif format[i] == 'w':
			begin = i;
			while i < len(format) and format[i] == 'w':
				i += 1;
			
			result.append(line[begin:i]);
		else:
			if format[i] != line[i]:
				raise Exception("Line not conforming to spec:\n{}\n{}^\n{}".format(line, " " * i, format));
			i += 1;
	
	return result;

def ParseTime(time):
	return int(time // 100), int(time % 100);

def ParseIdentification(file):
	# @ddd,dddddddd,dddddddd,dddd
	line = file.readline();
	if line == '':
		return False;
	
	try:
		record = line[0];
		if record != '@':
			return False;
		
		# sure, we'll accept it
		return True;
	except Exception: # you broke it
		return False;


# a map of Int -> [Bool], footnotes[i][j] indicating that services with footnote i run on day number j
footnotes = {};

currentDay = 2; # the footnote index of the day we want to simulate
prevDay = currentDay - 1; # just in case a service runs past the day change

def ParseFootnoteDescription(file):
	descLine = file.readline();
	if descLine == '':
		return False;
	
	record = descLine[0];
	
	if record != '#':
		# whoops, something went wrong
		file.BackTrack();
		return False;
	number = int(descLine[1:]);
	#                                                               snip off the newline
	footnotes[number] = list(map(lambda x: x == '1', file.readline()[:-1]));
	
	return True;

def FormatStation(station, platform = None):
	station = station.strip();
	
	if platform == None:
		return station[0].upper() + station[1:];
	else:
		platform = platform.strip();
		
		return "{}{}, {}".format(station[0].upper(), station[1:], platform);

services = {};
prevServices = {};

def ParseTransportService(file):
	line = file.readline();
	if line == '':
		return False;
	id = ParseLine("#dddddddd", line);
	
	tempServices = {};
	validServices = {};
	
	# service number
	line = file.readline();
	while line[0] == '%': # supposed to occur just once but who cares, right?
		company, number, variant, firstValid, lastValid, name = ParseLine("%ddd,ddddd,wwwwww,ddd,ddd,wwwwwwwwwwwwwwwwwwwwwwwwwwwwww", line);
		tempServices[number] = {"company": company, "variant": variant, "name": name, "footnotes": {}, "modes": [], "attrs": []};
		
		if lastValid == 999:
			lastValid = -1;
		validServices[number] = (firstValid, lastValid);
		line = file.readline();
	
	# validity
	while line[0] == '-':
		footnote, first, last = ParseLine("-ddddd,ddd,ddd", line);
		for number in tempServices:
			tempServices[number]["footnotes"][footnote] = (first, last);
		line = file.readline();
	
	# transport mode
	while line[0] == '&':
		code, first, last = ParseLine("&wwww,ddd,ddd", line);
		for number in tempServices:
			tempServices[number]["modes"].append((code, first, last));
		line = file.readline();
	
	# attributes
	while line[0] == '*':
		code, first, last = ParseLine("*wwww,ddd,ddd", line);
		for number in tempServices:
			tempServices[number]["attrs"].append((code, first, last));
		line = file.readline();
	
	# stops in the service (finally!)
	stops = [];
	while line[0] in '>.;+<':
		if line[0] == '<': # end of stops
			station, time = ParseLine("<wwwwwww,dddd", line);
			line =  file.readline();
			if line != '' and line[0] == '?':
				arrival, departure, footnote = ParseLine("?wwwww,wwwww,ddddd", line);
				
				stops.append((ParseTime(time), FormatStation(station, arrival)));
			else:
				stops.append((ParseTime(time), FormatStation(station)));
				# don't skip over the end
				file.BackTrack();
			
			# record the stops we encountered
			for number in tempServices:
				for footnote in tempServices[number]["footnotes"]:
					if footnotes[footnote][currentDay]:
						if number not in services:
							services[number] = tempServices[number];
						
						services[number]["stops"] = [stop for stop in stops[validServices[number][0] - 1:validServices[number][1]]];
					
					if footnotes[footnote][prevDay]:
						if number not in prevServices:
							prevServices[number] = tempServices[number];
							prevServices[number]["stops"] = [];
						
						prevServices[number]["stops"] = [stop for stop in stops[validServices[number][0] - 1:validServices[number][1]]];
			
			# we're done here
			return True;
			
		elif line[0] == '>': # start of stops
			station, time = ParseLine(">wwwwwww,dddd", line);
			line =  file.readline();
			if line[0] == '?':
				arrival, departure, footnote = ParseLine("?wwwww,wwwww,ddddd", line);
				line = file.readline();
				
				stops.append((ParseTime(time), FormatStation(station, departure)));
			else:
				stops.append((ParseTime(time), FormatStation(station)));
			
		elif line[0] == '.': # continuation (arrives and immediately departs)
			station, time = ParseLine(".wwwwwww,dddd", line);
			line =  file.readline();
			if line[0] == '?':
				arrival, departure, footnote = ParseLine("?wwwww,wwwww,ddddd", line);
				line = file.readline();
				
				stops.append((ParseTime(time), FormatStation(station, departure)));
			else:
				stops.append((ParseTime(time), FormatStation(station)));
			
		elif line[0] == '+': # stop
			station, arriveTime, departTime = ParseLine("+wwwwwww,dddd,dddd", line);
			line =  file.readline();
			
			# add one stop to the services (because in IFF this is one stop and in our format it's 2)
			for number in validServices:
				if validServices[number][1] != -1:
					if validServices[number][1] > len(stops):
						validServices[number] = (validServices[number][0], validServices[number][1] + 1);
				
				if validServices[number][0] - 1 > len(stops):
						validServices[number] = (validServices[number][0] + 1, validServices[number][1]);
			
			if line[0] == '?':
				arrival, departure, footnote = ParseLine("?wwwww,wwwww,ddddd", line);
				line = file.readline();
				
				stops.append((ParseTime(arriveTime), FormatStation(station, arrival)));
				stops.append((ParseTime(departTime), FormatStation(station, departure)));
			else:
				stops.append((ParseTime(arriveTime), FormatStation(station)));
				stops.append((ParseTime(departTime), FormatStation(station)));
		else:
			raise Exception("Unsupported stop record found:\n{}".format(line));
	
	raise Exception("Unknown format for line:\n{}".format(line));

with BackTrackFile(open("footnote.dat", "r")) as file:
	if not ParseIdentification(file):
		raise Exception("Someone managed to break IFF. ERROR ERROR ABORT ABORT");
	
	while ParseFootnoteDescription(file):
		pass;

with BackTrackFile(open("timetbls.dat", "r")) as file:
	if not ParseIdentification(file):
		raise Exception("Someone managed to break IFF. ERROR ERROR ABORT ABORT");

	while ParseTransportService(file):
		pass;

print("version: 5");

print("services:");
for service in services:
	print("\t{}:".format(service));
	for stop in services[service]["stops"]:
		if stop[0][0] < 26:
			print("\t\t{}, {}, {}".format(stop[0][0], stop[0][1], stop[1]));
	
	print("\t:end");

for service in prevServices:
	print("\t{}:".format(service));
	for stop in prevServices[service]["stops"]:
		if stop[0][0] >= 26:
			print("\t\t{}, {}, {}".format(stop[0][0] - 24, stop[0][1], stop[1]));
	
	print("\t:end");

print(":end");
