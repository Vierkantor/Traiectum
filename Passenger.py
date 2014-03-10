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
		last = self.route[-1];
		service = random.choice([last[1].DeparturesFrom(last[0])]);
		
		# find all the stops after we can board
		stops = [];
		boarded = False;
		for stop in service:
			if last[1].HasPlatform(stop[1]):
				boarded = True;
			elif not boarded:
				continue;
			else:
				stops.append(stop);
		
		# if there are no stops after this, give up
		if len(stops) < 1:
			print("No stops");
			return;
		
		# find a new station
		new = random.choice(stops);
		# make sure we actually stop there
		if new[1].station == None:
			return;
		
		self.route.append((new[0], new[1].station));
	
	def MakeRoute(self):
		self.route = [(Data.frameTime, self.pos)];
		self.AddStop();
		
		# about 4 stops (pos, next, approx 2 more)
		while random.random() < 0.5:
			self.AddStop();
		
		print(map(lambda x: "{}: {}".format(x[0], x[1].name), self.route))
	
	def ShouldEmbark(self, train):
		if len(self.route) == 1:
			return False;
		
		boarded = False;
		for stop in train.service:
			if not (boarded or self.route[0][1].HasPlatform(stop[1])):
				continue;
			else:
				boarded = True;
			
			if self.route[1][1].HasPlatform(stop[1]):
				return True;
		return False;
	
	def ShouldDisembark(self, node):
		if self.route[0][1].HasPlatform(node):
			return True;
		
		return False;
