from __future__ import division;
import math;
import random;

import Data;
import SimObject;
import Passenger;
import Service;

stations = {};

class Station(SimObject.SimObject):
	def __init__(self, attrs, name):
		SimObject.SimObject.__init__(self, attrs);
		self.name = name;
		
		self.platforms = [];
		self.nodes = [];
		self.passengers = [];
		self.departures = [];
	
	def AddPlatform(self, place):
		self.platforms.append(place);
		self.nodes.append(Data.places[place]);
		Data.nodes[Data.places[place]].station = self;
	
	def HasPlatform(self, node):
		return node in self.nodes;
	
	def Update(self):
		passengersPerTick = Data.timeStep / 10;
		
		if random.random() < (passengersPerTick - math.floor(passengersPerTick)):
			for i in range(0, int(math.ceil(passengersPerTick))):
				self.passengers.append(Passenger.Passenger(self));
	
	# all the services that leave said node after said time
	def DeparturesFrom(self, time):
		for service in self.departures:
			for stop in Service.services[service].orders:
				if stop[0] > time and Data.Place(stop[1]) in self.platforms:
					yield service;
					break;
