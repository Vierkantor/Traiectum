import re;

class ParseError(Exception):
	def __init__(self, message):
		self.message = message;
	
	def __str__(self):
		return self.message;

# makes a possibly negative or None key into a positive one
def regularize(key, start, stop, default = 0):
	if key == None:
		return default;
	
	if key < 0:
		return stop + key + 1;
	
	return start + key;

# to make slicing long strings easier
# instead of creating a copy of the text, create a copy of the start pointer
class StringSlice:
	def __init__(self, text, start = None, stop = None):
		self.text = text;
		
		self.start = regularize(start, 0, len(self.text), 0);
		self.stop = regularize(stop, 0, len(self.text), len(self.text));
	
	# force slicing
	def __str__(self):
		return self.text[self.start:self.stop];
	
	def __eq__(self, other):
		if isinstance(other, StringSlice):
			return self.text == other.text and self.start == other.start and self.end == other.end;
		else:
			return self.text[self.start:self.stop] == other;
	
	def __len__(self):
		return int(self.stop - self.start);
	
	def __getitem__(self, key):
		# key should be a slice or an int
		if isinstance(key, int):
			# int: return character at that position (like a regular string)
			return self.text[regularize(key, self.start, self.stop)];
		elif isinstance(key, slice):
			# slice: make a *_new_* StringSlice object (note the new!)
			return StringSlice(self.text, regularize(key.start, self.start, self.stop, self.start), regularize(key.stop, self.start, self.stop, self.stop));
		else:
			raise TypeError("string indices must be integers or slices")
	
	def __iter__(self):
		for i in xrange(self.start, self.end):
			yield self.text[i];

# returns a string, starting from the first non-whitespace character
whitespace = " \t\n\r#"
newlines = "\n\r"
def SkipWhitespace(text):
	try:
		while text[0] in whitespace:
			# ignore comments
			if text[0] == "#":
				text = text[1:];
				# take out everything up to a newline, which is taken care of by the regular whitespace removing
				while text[0] not in newlines:
					text = text[1:];
			else:
				text = text[1:];
	except IndexError:
		return "";
	
	return text;

# checks that the text starts with the literal
def MatchText(literal):
	def MatchLiteral(text):
		text = SkipWhitespace(text);
		if text[:len(literal)] == literal:
			return (text[len(literal):], literal);
		raise ParseError("Expected {}, received {}".format(literal, text[:len(literal)]));
	
	# partial application!
	return MatchLiteral;

# checks that the text starts with an integer
def MatchInt(text, signed = True):
	text = SkipWhitespace(text);
	startText = text[:16];
	
	length = 0;
	try:
		if signed:
			# check if the int is negative
			negative = False;
			if text[0] == "+":
				text = text[1:];
			elif text[0] == "-":
				text = text[1:];
				negative = True;
		else:
			# it's always positive
			negative = False;
	
		# actually make it into an int
		number = 0;
		while text[0] in '0123456789':
			number *= 10;
			number += int(text[0]);
			text = text[1:];
			length += 1;
	except IndexError:
		# end of file, so stop trying to parse
		pass;
	
	# make sure there are digits
	if length == 0:
		raise ParseError("Expected <int>, received {}".format(startText));
	
	return text, ((-number) if negative else number);

# checks that the text starts with a float (or integer)
def MatchFloat(text):
	# start with a (non-optional) integer part
	text, intPart = MatchInt(text);
	floatPart = "";
	try:
		# and an optional point after the dot
		text, _ = MatchText(".")(text);
		text, floatPart = MatchInt(text, signed = False);
	except ParseError:
		pass;
	
	# make it into a nice float
	return text, float(intPart) + float("0." + floatPart);

# a name (used as key, so anything up to a ':' or ',')
def MatchName(text):
	text = SkipWhitespace(text);
	name = [];
	try:
		while text[0] not in ":,\n\r":
			name.append(text[0]);
			text = text[1:];
	except IndexError:
		pass;
	
	if name == []:
		raise ParseError("Expected <name>, received {}".format(text[:16]));
	
	return text, "".join(name);

# matches a list of Match... functions
def ParseFormat(text, syntax):
	result = [];
	
	for element in syntax:
		text, value = element(text);
		result.append(value);
	
	return text, result;
