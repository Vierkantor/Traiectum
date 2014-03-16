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
			if last[1].HasPlatform(Data.places[stop[1]]):
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
		station = Data.nodes[Data.places[new[1]]].station;
		# make sure we actually stop there
		if station == None:
			return;
		
		self.route.append((new[0], station));
	
	def MakeRoute(self):
		self.route = [(Data.frameTime, self.pos)];
		self.AddStop();
		
		# about 4 stops (pos, next, approx 2 more)
		while random.random() < 0.5:
			self.AddStop();
	
	def ShouldEmbark(self, train):
		if len(self.route) == 1:
			return False;
		
		boarded = False;
		for stop in train.service:
			if not (boarded or self.route[0][1].HasPlatform(Data.places[stop[1]])):
				continue;
			else:
				boarded = True;
			
			if self.route[1][1].HasPlatform(Data.places[stop[1]]):
				return True;
		return False;
	
	def ShouldDisembark(self, node):
		if self.route[0][1].HasPlatform(node):
			return True;
		
		return False;
