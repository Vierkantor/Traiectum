from __future__ import division;
import collections;
import math;
import random;

import Data;
import Station;

class Passenger:
	def __init__(self, pos):
		self.pos = pos;
		self.route = [];
		
		self.MakeRoute();
	
	def AddStop(self):
		# the previous stop
		last = self.route[-1];
		
		# find a new train
		departures = [x for x in last[1].DeparturesFrom(last[0])];
		if len(departures) < 1:
			return;
		
		service = random.choice(departures);
		
		# find all the stops after we can board
		stops = [];
		boarded = False;
		for stop in Data.services[service]:
			if last[1].HasPlatform(Data.places[Data.Place(stop[1])]):
				boarded = True;
			elif not boarded:
				continue;
			else:
				stops.append(stop);
		
		# if there are no stops after this, give up
		if len(stops) < 1:
			return;
		
		# find a new station
		new = random.choice(stops);
		station = Data.nodes[Data.places[Data.Place(new[1])]].station;
		# make sure we actually stop there
		if station == None:
			return;
		
		self.route.append((new[0], station, service));
	
	def MakeRoute(self):
		self.route = [(Data.frameTime, self.pos, None)];
		self.AddStop();
		
		# about 4 stops (pos, next, approx 2 more)
		while random.random() < 0.5:
			self.AddStop();
	
	def ShouldEmbark(self, train):
		if len(self.route) == 1:
			return False;
		
		return self.route[1][2] in train.serviceName;
	
	def ShouldDisembark(self, node):
		return node.station == self.route[0][1];
