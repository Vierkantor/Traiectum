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

# uses A*
# heuristic: distance along great circle (is lower bound of actual distance, so it is admissible)
def FindRoute(begin, end):
	if begin == end:
		return [end];

	closed = {};
	open = {};
	open[begin] = (Distance(Data.nodes[begin].pos, Data.nodes[end].pos), 0);
	dirs = {};
	
	while len(open) > 0:
		# find first node to process
		current = min(open, key=open.get);
		distance = open[current];
		
		# processing it, so remove the node from the open points
		del open[current];
		# and add it to the closed points
		closed[current] = distance;
		
		# if we already reached the end, return the path
		if current == end:
			return MakePath(begin, end, dirs);
		
		# add the adjacent nodes to the queue
		for next in Data.GetLinks(current):
			# if we've already processed it, continue
			if next in closed:
				continue;
			
			# otherwise, calculate its distance
			newG = distance[1] + Distance(Data.nodes[current].pos, Data.nodes[next].pos);
			
			# if it's a good way to get there, save the new direction
			if next not in open or open[next][1] > newG:
				dirs[next] = current;
				open[next] = (newG + Distance(Data.nodes[next].pos, Data.nodes[end].pos), newG);
			
	print("No path between {} and {}".format(Data.NodeName(begin), Data.NodeName(end)));
	
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
