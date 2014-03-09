from __future__ import division;

import Data;

stations = {};

class Station:
	def __init__(self, name):
		self.name = name;
		
		self.platforms = [];
		self.nodes = [];
		self.passengers = [];
	
	def AddPlatform(self, place):
		self.platforms.append(place);
		self.nodes.append(Data.places[place]);
	
	# all the services that leave said node after said time
	def DeparturesFrom(self, time):
		for service in services:
			for stop in services[service]:
				if stop[0] > time and stop[1] in self.platforms:
					yield service;
					break;
	
	
