#!/usr/bin/python2.7

from __future__ import division;

import collections;
import math;
import sys;
import pygame;

import Data;
import Filefunc;
import Graphics;
import Path;

def Add(time, service):
	return map(lambda x: (x[0] + time, x[1]), services[service]);

mouseDown = False;

Filefunc.LoadData();

while 1:
	keys = pygame.key.get_pressed();
		
	if keys[pygame.K_LEFT] or keys[pygame.K_a]:
		Graphics.center = (Graphics.center[0], Graphics.center[1] - 100 / Graphics.scale);
		Graphics.following = None;
	if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
		Graphics.center = (Graphics.center[0], Graphics.center[1] + 100 / Graphics.scale);
		Graphics.following = None;
	if keys[pygame.K_UP] or keys[pygame.K_w]:
		Graphics.center = (Graphics.center[0] + 100 / Graphics.scale, Graphics.center[1]);
		Graphics.following = None;
	if keys[pygame.K_DOWN] or keys[pygame.K_s]:
		Graphics.center = (Graphics.center[0] - 100 / Graphics.scale, Graphics.center[1]);
		Graphics.following = None;
		
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			Filefunc.SaveData();
			sys.exit();
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1: # center on a train
				worldPos = Graphics.GetWorldPos(pygame.mouse.get_pos());
				smallestDistance = 0.01;
				
				# check all trains
				for trainID in Data.trains:
					train = Data.trains[trainID];
					
					# if the distance is the shortest
					distance = Path.Distance(train.pos, worldPos);
					if distance < smallestDistance:
						# center on that train
						Graphics.following = train;
						smallestDistance = distance;
			elif event.button == 4:
				Graphics.scale = Graphics.scale * 2;
			elif event.button == 5:
				Graphics.scale = Graphics.scale / 2;
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_EQUALS:
				Data.timeStep *= 2;
			elif event.key == pygame.K_MINUS:
				Data.timeStep /= 2;	

	Data.UpdateTime();
	
	for train in Data.trains:
		try:
			Data.trains[train].Update();
		except:
			print(train);
			raise;

	Graphics.Draw();
	
	# make sure the log gets updated
	sys.stdout.flush();
