from __future__ import division;
import pygame;

import Graphics;
import Path;
	
def Time(hr = 0, min = 0, sec = 0):
	if hr < 2:
		hr += 24;
	return hr * 60 + min + sec / 60;

clock = pygame.time.Clock();
frameTime = 120;

# the time (in minutes) elapsing every tick
timeStep = 30 / 1000;

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
	return map(lambda x: (x[0] + time, x[1]), service);

# joins a list of orders together
def Join(list):
	result = [(0, services[list[0]][0][1])];

	prev = None;
	for elem in list:
		for order in services[elem]:
			result.append(order);

	result.append((1560, result[-1][1]));
	return result;

class Train:
	def __init__(self, composition, serviceName, service):
		self.composition = composition;
		self.serviceName = serviceName;
		self.service = service;
		self.order = 0;
		self.pos = nodes[self.service[self.order][1]];
		self.v = 0;
		self.distance = 0;
		self.path = Path.FindRoute(self.service[self.order][1], self.service[self.order + 1][1]);
	
	def Update(self):
		try:
			if self.path == []:
				self.path = Path.FindRoute(self.service[self.order][1], self.service[self.order + 1][1]);
			elif self.path == False: # no way to continue
				return;
			elif len(self.path) == 1:
				self.v = 0;
				self.distance = 0;
				self.pos = nodes[self.path[0]];
				if self.service[self.order + 1][0] < frameTime:
					self.order += 1;
					self.path = [];
			else:
				lineDistance = Path.Distance(nodes[self.path[0]], nodes[self.path[1]]);
				
				# accelerate
				if len(self.path) == 2 and self.v * (self.service[self.order + 1][0] - frameTime) > (lineDistance - self.distance):
					# brake for an upcoming station
					if self.v > 100:
						# decelerate by about 6 m/s^2
						self.v -= 20000 * timeStep;
					if self.v <= 0:
						self.v = 0;
				else:
					# if the velocity is too low, accelerate by about 6 m/s^2
					if self.v <= 20:
						self.v += 20000 * timeStep;
					else:
						self.v += timeStep * 400000 / self.v;
				
				# move the train
				self.distance += self.v * timeStep;
				self.pos = Path.Move(nodes[self.path[1]], nodes[self.path[0]], self.distance / lineDistance);
				
				# move to the next line segment if we pass the end of this one
				if self.distance > lineDistance:
					del self.path[0];
					self.distance -= lineDistance;
		except:
			print(self.serviceName, self.path, self.service, self.order);
			raise;
	
	def Draw(self, screen):
		screenPos = Graphics.GetPos(self.pos);
		pygame.draw.circle(screen, (255, 0, 0), screenPos, 2, 0);
		if self.service[self.order + 1][0] < frameTime - 1:
			text = Graphics.font.render("{} +{}".format(self.composition, int(frameTime - self.service[self.order + 1][0])), 1, (0, 0, 0));
		else:
			text = Graphics.font.render("{}".format(self.composition), 1, (0, 0, 0));
		textpos = text.get_rect().move((screenPos[0], screenPos[1]));
		pygame.draw.rect(screen, (255, 255, 255), (screenPos[0], screenPos[1], 100, 12));
		pygame.draw.rect(screen, (0, 0, 0), (screenPos[0], screenPos[1], 100, 12), 1);
		screen.blit(text, textpos);
	
	def __str__(self):
		return "Data.Train, composition={0}, serviceName={1}, service={2}".format(str(self.composition), str(self.serviceName), str(self.service));
