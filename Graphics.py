from __future__ import division;
import math;
import pygame;

import Data;

pygame.init();

size = width, height = 1024, 768;
scale = 8;
center = (50, 0);
font = pygame.font.Font(None, 14);
screen = pygame.display.set_mode(size);

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
	print(pos);
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
	
	for place in Data.places:
		pos = GetPos(Data.nodes[Data.places[place]].pos);
		if pos[0] < 0 or pos[0] > width or pos[1] < 0 or pos[1] > height:
			continue;
		pygame.draw.circle(screen, (0, 0, 0), pos, 3, 0);
		text = font.render(str(place), 1, (0, 0, 0));
		textpos = text.get_rect().move((pos[0], pos[1] - 12));
		screen.blit(text, textpos);
	
	for node in Data.links:
		Data.nodes[node].Draw(screen);
		for link in Data.links[node]:
			pygame.draw.line(screen, (0, 0, 0), GetPos(Data.nodes[node].pos), GetPos(Data.nodes[link].pos), 1);
	
	for train in Data.trains:
		Data.trains[train].Draw(screen);
	
	text = font.render(str(int(Data.frameTime // 60)) + ":" + str(int(Data.frameTime % 60)), 1, (0, 0, 0));
	textpos = text.get_rect();
	screen.blit(text, textpos);
	
	text = font.render(str(Data.clock.get_fps()), 1, (0, 0, 0));
	textpos = text.get_rect().move((0, 12));
	screen.blit(text, textpos);
	
	pygame.display.flip();
