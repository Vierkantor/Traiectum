#!/usr/bin/python2.7

import Data;
import Graphics;
import Filefunc;

Filefunc.LoadData();

commands = "[<h>elp] [<?>], [<l>ink], [<u>nlink], [<r>eload], [<s>ave], [<q>uit]";

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
	elif command[0] == "r":
		print("Sure?");
		print("[<y>es], [<n>o]");
		command = raw_input();
		if command[0] == "y":
			Filefunc.LoadData();
	elif command[0] == "s":
		Filefunc.SaveData();
	elif command[0] == "q":
		print("Sure?");
		print("[<y>es], [<n>o]");
		command = raw_input();
		if command[0] == "y":
			break;
