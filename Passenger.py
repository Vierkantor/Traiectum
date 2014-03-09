from __future__ import division;
import collections;
import math;
import random;

import Data;
import Station;

class Passenger:
	def __init__(self, pos, destination = None):
		if destination == None:
			destination = random.choice(Station.stations.values());
		
		self.pos = pos;
		self.destination = destination;
		
		self.route = None;
		# where the route is calculated from
		self.routePos = None;
	
	def MakePath(self, dirs):
		try:
			result = [(None, self.destination, None)];
			while result[0][1] != self.pos:
				result.insert(0, dirs[result[0][1]]);
		
			return result;
		except KeyError:
			print(dirs);
			raise;
	
	# finds the quickest path between our position and our destination
	# using Dijkstra's algorithm
	def MakeRoute(self):
		if self.pos == None or self.destination == None:
			return None;
		
		if self.pos == self.destination:
			return [(None, self.destination)];
		
		visited = set();
		toVisit = collections.OrderedDict([(self.pos, Data.frameTime)]);
		dirs = {self.pos: (None, self.pos, Data.frameTime)};
	
		while len(toVisit) > 0:
			# get the next node with lowest distance
			toVisit = collections.OrderedDict(sorted(toVisit.items(), key = lambda x: x[1], reverse = True));
			current = toVisit.popitem();
			visited.add(current[0]);
			
			# if we are done, stop
			if current[0] == self.destination:
				return self.MakePath(dirs);
			
			# find all the services we can get into
			for service in current[0].DeparturesFrom(current[1] + 1):
				# find all the stops we can get off at and add them
				boarded = False;
				for stop in Data.services[service]:
					time = stop[0];
					station = Data.nodes[stop[1]].station;
					
					# make sure the stop is at an actual station
					if station == None:
						continue;
					
					# make sure it's not before we get on the train
					if not boarded and station != current[0]:
						continue;
					else:
						boarded = True;
					
					# unless we've already reached them
					if station in visited:
						continue;
					
					# don't add it if we already have a quicker route to our node
					if station in toVisit and toVisit[station] < time:
						continue;
					
					# take a minute to exit the train
					toVisit[station] = time;
					# and save how we got here
					dirs[station] = (service, current[0], time);
		return None;
	
	def ShouldEmbark(self, train):
		if self.routePos != self.pos:
			self.route = self.MakeRoute();
			self.routePos = self.pos;
			if self.route != None and len(self.route) > 1:
				print(map(lambda x: "{}: {}".format(x[2], x[1].name), self.route))
		
		if self.route == None:
			return False;
		
		return self.route[0][0] in train.serviceName;
	
	def ShouldDisembark(self, node):
		for stop in self.route:
			if stop[1].HasPlatform(node):
				return True;
		
		return False;
