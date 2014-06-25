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
scale = 8;
center = (50, 0);

# screen is initialized when the main module runs (so things can get imported without displaying a screen)
screen = None;

# move standard parallel to about 50 degrees
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
	global following, center, parallelCorrection;
	
	# make the center of the screen look right
	parallelCorrection = math.cos(center[0] / 180 * math.pi);

	screen.fill((255, 255, 255));
	
	if following != None:
		center = following.pos;
	
	if scale > 1024:
		for place in Data.places:
			pos = GetPos(Data.nodes[Data.places[place]].pos);
			if pos[0] < 0 or pos[0] > width or pos[1] < 0 or pos[1] > height:
				continue;
			pygame.draw.circle(screen, (0, 0, 0), pos, 3, 0);
			text = font.render(place, 1, (0, 0, 0));
			textpos = text.get_rect().move((pos[0], pos[1] - 12));
			screen.blit(text, textpos);
	
	for node in Data.links:
		if scale > 65536:
			pos = GetPos(Data.nodes[node].pos);
			if 0 <= pos[0] <= width and 0 <= pos[1] <= height:
				Data.nodes[node].Draw(screen);
		for link in Data.links[node]:
			pygame.draw.line(screen, (0, 0, 0), GetPos(Data.nodes[node].pos), GetPos(Data.nodes[link].pos), 1);
	
	for train in Data.trains:
		pos = GetPos(Data.trains[train].pos);
		if 0 <= pos[0] <= width and 0 <= pos[1] <= height:
			Data.trains[train].Draw(screen);
	
	if following != None:
		screenPos = GetPos(following.pos);
		
		pygame.draw.rect(screen, (255, 255, 255), (screenPos[0], screenPos[1] - 6 * 12, 100, 6 * 12));
		pygame.draw.rect(screen, (0, 0, 0), (screenPos[0], screenPos[1] - 6 * 12, 100, 6 * 12), 1);
		offset = -6 * 12;
		for order in following.service[following.order : following.order + 6]:
			text = font.render("{}:{} {}".format(int(order[0] // 60), int(order[0] % 60), order[1]), 1, (0, 0, 0));
			textpos = text.get_rect().move((screenPos[0], screenPos[1] + offset));
			screen.blit(text, textpos);
			offset += 12;
	
	text = font.render(str(int(Data.frameTime // 60)).zfill(2) + ":" + str(int(Data.frameTime % 60)).zfill(2), 1, (0, 0, 0));
	textpos = text.get_rect();
	screen.blit(text, textpos);
	
	text = font.render(str(Data.clock.get_fps()), 1, (0, 0, 0));
	textpos = text.get_rect().move((0, 12));
	screen.blit(text, textpos);
	
	pygame.display.flip();
