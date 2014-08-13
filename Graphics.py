from __future__ import division;
import math;

import Data;

try:
	import pygame;
	
	pygame.init();

	font = pygame.font.Font(None, 14);
except ImportError:
	pass;

size = width, height = 1024, 768;

# the width in pixels of one degree on the map
scale = oldScale = 8;
# center of screen
center = oldCenter = (50, 0);

# an extra buffer for speeding up background (links, nodes and places)
background = pygame.Surface(size);
# make sure it's drawn initially (also: old... variables)
backgroundDirty = True;

# screen is initialized when the main module runs (so things can get imported without displaying a screen)
screen = None;

# lists information such as the trains or where the selected one stops
selectedList = None;

# move standard parallel to where we are looking
# to make the equirectangular projection look a bit better
parallelCorrection = math.cos(center[0] / 180 * math.pi);

def GetPos(pos):
	pos = Transform(pos);
	return (pos[1] + 512, (-pos[0]) + 384);

def SVGPos(pos):
	return (pos[1] * 1000, pos[0] * -1000);

def Transform(pos):
	return (int((pos[0] - center[0]) * scale), int((pos[1] - center[1]) * scale * parallelCorrection));

def InvTransform(pos):
	return (pos[0] / scale + center[0], pos[1] / scale / parallelCorrection + center[1]);

def GetWorldPos(pos):
	return InvTransform((-(pos[1] - 384), pos[0] - 512));

# centers the camera on a thing
following = None;

def Draw():
	global following, center, oldCenter, oldScale, backgroundDirty, parallelCorrection;
	
	if following != None:
		center = following.pos;
	
	# background is dirty
	if center != oldCenter or scale != oldScale or backgroundDirty:
		oldCenter = center;
		oldScale = scale;
		backgroundDirty = False;
		
		parallelCorrection = math.cos(center[0] / 180 * math.pi);
		
		# redraw background
		background.fill((255, 255, 255));
		
		if scale > 1024:
			for place in Data.places:
				pos = GetPos(Data.nodes[Data.places[place]].pos);
				if pos[0] < 0 or pos[0] > width or pos[1] < 0 or pos[1] > height:
					continue;
				pygame.draw.circle(background, (0, 0, 0), pos, 3, 0);
				text = font.render(place, 1, (0, 0, 0));
				textpos = text.get_rect().move((pos[0], pos[1] - 12));
				background.blit(text, textpos);
		
		for node in Data.links:
			if scale > 65536:
				pos = GetPos(Data.nodes[node].pos);
				if 0 <= pos[0] <= width and 0 <= pos[1] <= height:
					Data.nodes[node].Draw(background);
			for link in Data.links[node]:
				Data.links[node][link].Draw(background);
	
	# draw the unchanged objects
	screen.blit(background, (0, 0));
	
	# draw the changed objects
	for train in Data.trains:
		pos = GetPos(Data.trains[train].pos);
		if 0 <= pos[0] <= width and 0 <= pos[1] <= height:
			Data.trains[train].Draw(screen);
	
	# draw the interface
	
	# top bar
	pygame.draw.rect(screen, (222, 222, 222), (0, 0, width, 32), 0);
	pygame.draw.rect(screen, (128, 128, 128), (0, 0, width, 32), 1);
	
	# current time
	text = font.render("{}:{} ({} sec/tick)".format(str(int(Data.frameTime // 60)).zfill(2), str(int(Data.frameTime % 60)).zfill(2), Data.deltaT), 1, (0, 0, 0));
	textpos = text.get_rect().move((6, 6));
	screen.blit(text, textpos);
	
	# fps
	text = font.render(str(Data.clock.get_fps()), 1, (0, 0, 0));
	textpos = text.get_rect().move((6, 18));
	screen.blit(text, textpos);
	
	if selectedList:
		selectedList.Draw(screen);
	
	pygame.display.flip();
