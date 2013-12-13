#!/usr/bin/python2.7

import Data;
import Graphics;
import Filefunc;

Filefunc.LoadData();

print("Enter command:");
print("[<h>elp] [<?>], [<s>plit] link, [<q>uit]");

while True:
	command = raw_input();
	print(command);
	if command[0] == "h" or command[0] == "?":
		print("Commands:");
		print("[<h>elp] [<?>], [<r>eload], [<s>ave], [<q>uit]");
	elif command[0] == "r":
		print("Sure?");
		print("[<y>es], [<n>o]");
		if command[0] == "y":
			Filefunc.LoadData();
	elif command[0] == "s":
		Filefunc.SaveData();
	elif command[0] == "q":
		print("Sure?");
		print("[<y>es], [<n>o]");
		if command[0] == "y":
			break;
