#!/usr/bin/python2.7

import Data;
import Graphics;
import Filefunc;

import svgwrite;

Filefunc.LoadData();

commands = "[<h>elp] [<?>], [<l>ink], [<u>nlink], [<i>nsert node], [<r>eload], [<s>ave], [<e>xport to SVG], [<q>uit]";

print("Enter command:");
print(commands);

while True:
	command = raw_input();
	print(command);
	if command[0] == "h" or command[0] == "?":
		print("Commands:");
		print(commands);
	elif command[0] == "l":
		print("Node 1:");
		begin = int(raw_input());
		print("Node 2:");
		end = int(raw_input());
		Data.AddLink(begin, end);
	elif command[0] == "u":
		print("Node 1:");
		begin = int(raw_input());
		print("Node 2:");
		end = int(raw_input());
		try:
			Data.links[begin].remove(end);
			Data.links[end].remove(begin);
		except KeyError:
			pass;
	elif command[0] == "i":
		print("Node 1:");
		begin = int(raw_input());
		print("Node 2:");
		end = int(raw_input());
		print("New node:");
		new = int(raw_input());
		try:
			Data.links[begin].remove(end);
			Data.links[end].remove(begin);
			Data.links[begin].append(new);
			Data.links[new].append(begin);
			Data.links[new].append(end);
			Data.links[end].append(new);
		except KeyError:
			pass;
	elif command[0] == "r":
		print("Sure?");
		print("[<y>es], [<n>o]");
		command = raw_input();
		if command[0] == "y":
			Filefunc.LoadData();
	elif command[0] == "s":
		Filefunc.SaveData();
	elif command[0] == "e":
		drawing = svgwrite.Drawing("track.svg", profile="full");
		for begin in Data.links:
			for end in Data.links[begin]:
				if begin < end:
					path = drawing.path();
					path.push("M");
					path.push(Graphics.SVGPos(Data.nodes[begin]));
					path.push(Graphics.SVGPos(Data.nodes[end]));
					drawing.add(path.stroke('black', width=0.01));
		drawing.save();
		print("Done.");
	elif command[0] == "q":
		print("Sure?");
		print("[<y>es], [<n>o]");
		command = raw_input();
		if command[0] == "y":
			break;
