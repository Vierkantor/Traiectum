from __future__ import division;
import math;

import Data;

# distance (in m) between the begin and end points (as coordinates)
def Distance(begin, end):
	if begin == end:
		return 0;
	
	begin = (begin[0] / 180 * math.pi, begin[1] / 180 * math.pi);
	end = (end[0] / 180 * math.pi, end[1] / 180 * math.pi);

	# begin and end points as coordinates in R^3 (with ||begin|| = ||end|| = 1)
	by = math.sin(begin[0]);
	ey = math.sin(end[0]);
	
	bx = math.cos(begin[0]) * math.cos(begin[1]);
	ex = math.cos(end[0]) * math.cos(end[1]);
	
	bz = math.cos(begin[0]) * math.sin(begin[1]);
	ez = math.cos(end[0]) * math.sin(end[1]);
	
	try:
		# the angle between two points is acos(dot product / length product (= 1) ), multiply by sphere radius for actual distance
		return 6400000 * math.acos(bx * ex + by * ey + bz * ez);
	except ValueError as e:
		print(bx, by, bz, ex, ey, ez, begin, end);
		raise e;

def Move(a, b, weight = 0.5):
	return (a[0] * weight + b[0] * (1 - weight), a[1] * weight + b[1] * (1 - weight));

def FindRoute(begin, end):
	if begin == end:
		return [end];

	closed = [];
	open = [(begin, 0, Distance(Data.nodes[begin].pos, Data.nodes[end].pos))];
	dirs = {};
	
	while open != []:
		open = sorted(open, key = lambda x: x[2]);
		current = open[0];
		open = open[1:];
		closed.append(current);
		
		if current[0] == end:
			return MakePath(begin, end, dirs);
		
		for next in Data.GetLinks(current[0]):
			skip = False;
			g = current[1] + Distance(Data.nodes[current[0]].pos, Data.nodes[next].pos);
			for closedNode in closed:
				if closedNode[0] == next:
					if g < closedNode[1]:
						closed.remove(closedNode);
					else:
						skip = True;
					break;			
			
			if not skip:
				open.append((next, g, g + Distance(Data.nodes[next].pos, Data.nodes[end].pos)));
				dirs[next] = current[0];
	
	print("No path between {} and {}".format(begin, end));
	
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
