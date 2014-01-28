from __future__ import division;
import pygame;

import Data;

pygame.init();

size = width, height = 1024, 768;
scale = 8;
center = (0, 50);
font = pygame.font.Font(None, 14);
screen = pygame.display.set_mode(size);

def GetPos(pos):
	return Transform((pos[1], -pos[0]));

def SVGPos(pos):
	return (pos[1] * 1000, pos[0] * -1000);

def Transform(pos):
	return (int((pos[0] + center[0]) * scale + 512), int((pos[1] + center[1]) * scale + 384));

def InvTransform(pos):
	return ((pos[0] - 512) / scale - center[0], (pos[1] - 384) / scale - center[1]);

def GetWorldPos(pos):
	pos = InvTransform(pos);
	return (-pos[1], pos[0]);

def Draw():
	screen.fill((255, 255, 255));
	
	for place in Data.places:
		pos = GetPos(Data.nodes[Data.places[place]]);
		pygame.draw.circle(screen, (0, 0, 0), pos, 3, 0);
		text = font.render(str(place), 1, (0, 0, 0));
		textpos = text.get_rect().move(pos);
		screen.blit(text, textpos);
	
	for node in Data.links:
		pos = GetPos(Data.nodes[node]);
		text = font.render(str(node), 1, (0, 0, 0));
		textpos = text.get_rect().move((pos[0], pos[1] + 12));
		screen.blit(text, textpos);
		for link in Data.links[node]:
			pygame.draw.line(screen, (0, 0, 0), pos, GetPos(Data.nodes[link]), 1);
	
	for train in Data.trains:
		Data.trains[train].Draw(screen);
	
	text = font.render(str(int(Data.frameTime // 60)) + ":" + str(int(Data.frameTime % 60)), 1, (0, 0, 0));
	textpos = text.get_rect();
	screen.blit(text, textpos);
	
	pygame.display.flip();
