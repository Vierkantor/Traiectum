import pygame;

import Data;
import Graphics;

class List:
	def __init__(self, values):
		self.values = values;
		self.index = 0;
		
		self.surface = pygame.Surface((128, Graphics.height - 32));
		
		self.Redraw();
	
	def Click(self, pos):
		self.Selected((pos[1] - 32) // 16 + self.index);
	
	def Draw(self, screen):
		screen.blit(self.surface, (Graphics.width - 128, 32));
	
	def Redraw(self):
		self.surface.fill((222, 222, 222));
		
		i = 0;
		
		for value in self.values[self.index : self.index + Graphics.height // 16]:
			text = Graphics.font.render(value, 1, (0, 0, 0));
			textpos = text.get_rect().move((0, i * 16));
			self.surface.blit(text, textpos);
			
			i += 1;
	
	def Scroll(self, direction):
		self.index += direction;
		if self.index < 0:
			self.index = 0;
		if self.index > len(self.values):
			self.index = len(self.values);
		self.Redraw();
	
	def Selected(self, item):
		pass;

# the stops of the selected train
class StopsList(List):
	def __init__(self, train):
		self.train = train;
		
		List.__init__(self, ["{}:{} {}".format(int(order[0] // 60), int(order[0] % 60), order[1]) for order in train.service]);
		
		self.index = train.order;
		self.Redraw();
	
	def Selected(self, item):
		if 0 <= item < len(self.values):
			station = Data.nodes[Data.places[self.train.service[item][1]]].station;
			if station:
				Graphics.selectedList = TrainsList(station);

# the trains at this station
class TrainsList(List):
	def __init__(self, station):
		self.station = station;
		
		List.__init__(self, [str(service) for service in station.DeparturesFrom(0)]);
