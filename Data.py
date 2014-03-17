from __future__ import division;
import math;
import random;

import Graphics;
import Path;
import Passenger;
	
def Time(hr = 0, min = 0, sec = 0):
	if hr < 2:
		hr += 24;
	return hr * 60 + min + sec / 60;

try:
	import pygame;
	clock = pygame.time.Clock();
except ImportError:
	pass;

frameTime = 120;

# the time (in minutes) elapsing every tick (= 1/30s)
timeStep = 0.5 / 30;

def UpdateTime():
	global frameTime;
	frameTime += timeStep;
	while frameTime > 1560:
		frameTime -= 1440;
	while frameTime < 120:
		frameTime += 1440;

	clock.tick(30);

def GetLinks(node):
	if node in links:
		return links[node];
	else:
		return [];

nodes = {};
places = {};
links = {};
services = {};
trainCompositions = {};
trains = {};

def AddLink(begin, end):
	if begin in links:
		if end not in links[begin]:
			links[begin].append(end);
	else:
		links[begin] = [end];
	
	if end in links:
		if begin not in links[end]:
			links[end].append(begin);
	else:
		links[end] = [begin];

# returns a new service that starts the specified amount of time later
def Add(time, service):
	return list(map(lambda x: (x[0] + time, x[1]), service));

# find name of node if it exists, else return its number
def NodeName(node):
	for place in places:
		if places[place] == node:
			return place;
	
	return node;

# joins a list of orders together
def Join(list):
	result = [(0, services[list[0]][0][1])];

	prev = None;
	for elem in list:
		for order in services[elem]:
			result.append(order);

	result.append((1560, result[-1][1]));
	return result;

class Node:
	def __init__(self, name, pos):
		self.name = name;
		self.pos = pos;
		self.station = None;
	
	def Draw(self, screen):
		screenPos = Graphics.GetPos(self.pos);
		text = Graphics.font.render(str(self.name), 1, (0, 0, 0));
		textpos = text.get_rect().move(screenPos);
		screen.blit(text, textpos);

class Train:
	def __init__(self, composition, serviceName, service):
		self.composition = composition;
		self.serviceName = serviceName;
		self.service = service;
		self.order = 0;
		self.pos = nodes[places[self.service[self.order][1]]].pos;
		self.v = 0;
		self.distance = 0;
		self.CreateNewPath();
		
		self.passengers = [];
	
	def CreateNewPath(self):
		self.path = Path.FindRoute(places[self.service[self.order][1]], places[self.service[self.order + 1][1]]);
	
	def Arrived(self):
		# warn if we're too late by at least 1 minute
		plannedTime = self.service[self.order + 1][0];
		if plannedTime < frameTime - 1:
			print("{} arrived +{} at {}".format(self.composition, int(frameTime - plannedTime), self.path[0]));
		
		# we just arrived, so let passengers get off
		currentNode = nodes[self.path[0]];
		for passenger in self.passengers:
			if passenger.ShouldDisembark(currentNode):
				self.passengers.remove(passenger);
				
				# send the passenger to their following train
				if len(passenger.route) > 1:
					passenger.pos = currentNode.station;
					passenger.pos.passengers.append(passenger);
		
		# since we arrived, stop the train
		self.v = 0;
		self.distance = 0;
		self.pos = currentNode.pos; # at the place we arrived
		
		if plannedTime < frameTime:
			self.Depart();
	
	def Depart(self):
		# if we stopped at a station
		currentNode = nodes[self.path[0]];
		if currentNode.station != None:
			currentStation = currentNode.station;
			# take in passengers
			for passenger in currentStation.passengers:
				if passenger.ShouldEmbark(self):
					passenger.pos = None;
					passenger.route = passenger.route[1:];
					self.passengers.append(passenger);
					currentStation.passengers.remove(passenger);
			
		self.order += 1;
		self.path = [];
	
	def GetAcceleration(self):
		lineDistance = Path.Distance(nodes[self.path[0]].pos, nodes[self.path[1]].pos);
		
		# determine our movement
		a = 0;
		if len(self.path) == 2 and self.v * (self.service[self.order + 1][0] - frameTime) > (lineDistance - self.distance):
			# brake for an upcoming station
			if self.v > 100:
				# decelerate by about 6 m/s^2
				a = -20000;
		else:
			# if the velocity is too low, accelerate by about 6 m/s^2
			if self.v <= 20:
				a = 20000;
			else:
				a = 400000 / self.v;
		return a;
	
	def Update(self):
		try:
			if self.path == []:
				self.CreateNewPath();
			elif self.path == False: # no way to continue
				return;
			elif len(self.path) == 1: # we arrived at the destination
				self.Arrived();
			else:
				a = self.GetAcceleration();
				
				# move the train
				self.distance += self.v * timeStep;
				self.v += a * timeStep;
				if self.v <= 0:
					self.v = 0;
				# distance is the integral of v dt = x_0 + v_0 * t + 1/2 * a * t * t
				self.distance += 0.5 * a * timeStep * timeStep;
				
				lineDistance = Path.Distance(nodes[self.path[0]].pos, nodes[self.path[1]].pos);
				if lineDistance <= 0 or self.distance > lineDistance:
					del self.path[0]; # go to the next node in our path
					self.distance -= lineDistance;
					
					# recalculate path distance
					if len(self.path) > 1:
						lineDistance = Path.Distance(nodes[self.path[0]].pos, nodes[self.path[1]].pos);
					else:
						lineDistance = 0;
				
				# make sure we don't go off the end of the route
				if lineDistance > 0:
					self.pos = Path.Move(nodes[self.path[1]].pos, nodes[self.path[0]].pos, self.distance / lineDistance);
				else:
					self.pos = nodes[self.path[0]].pos;
				
		except:
			print(self.serviceName, self.path, self.service, self.order);
			raise;
	
	def Draw(self, screen):
		screenPos = Graphics.GetPos(self.pos);
		pygame.draw.circle(screen, (min(255, len(self.passengers)), max(0, 255 - len(self.passengers)), 0), screenPos, 2, 0);
		if Graphics.scale > 1024:
			if self.service[self.order + 1][0] < frameTime - 1:
				text = Graphics.font.render("{} +{} (p: {})".format(self.composition, int(frameTime - self.service[self.order + 1][0]), len(self.passengers)), 1, (0, 0, 0));
			else:
				text = Graphics.font.render("{} (p: {})".format(self.composition, len(self.passengers)), 1, (0, 0, 0));
			textpos = text.get_rect().move((screenPos[0], screenPos[1]));
			pygame.draw.rect(screen, (255, 255, 255), (screenPos[0], screenPos[1], 100, 12));
			pygame.draw.rect(screen, (0, 0, 0), (screenPos[0], screenPos[1], 100, 12), 1);
			screen.blit(text, textpos);
	
	def __str__(self):
		return "Data.Train, composition={0}, serviceName={1}, service={2}".format(str(self.composition), str(self.serviceName), str(self.service));
