from __future__ import division;
import math;

import Data;

def Distance(begin, end):
	return math.sqrt((begin[0] - end[0]) ** 2 + (begin[1] - end[1]) ** 2);

def Average(a, b, weight = 0.5):
	return (a[0] * weight + b[0] * (1 - weight), a[1] * weight + b[1] * (1 - weight));

def FindRoute(begin, end):
	if begin == end:
		return [end];

	closed = [];
	open = [(begin, 0, Distance(Data.nodes[begin], Data.nodes[end]))];
	dirs = {};
	
	while open != []:
		open = sorted(open, key = lambda x: x[2]);
		current = open[0];
		open = open[1:];
		closed.append(current);
		
		if current[0] == end:
			return MakePath(begin, end, dirs);
		
		for next in Data.links[current[0]]:
			skip = False;
			g = current[1] + Distance(Data.nodes[current[0]], Data.nodes[next]);
			for closedNode in closed:
				if closedNode[0] == next:
					if g < closedNode[1]:
						closed.remove(closedNode);
					else:
						skip = True;
					break;			
			
			if not skip:
				open.append((next, g, g + Distance(Data.nodes[next], Data.nodes[end])));
				dirs[next] = current[0];
	
	return False;

def MakePath(begin, end, dirs):
	if begin == end:
		return [end];
	result = [end];
	current = end;
	while True:
		current = dirs[current];
		result.insert(0, current);
		if current == begin:
			break;
	
	return result;