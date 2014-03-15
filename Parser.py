import re;

class ParseError(Exception):
	def __init__(self, message):
		self.message = message;
	
	def __str__(self):
		return self.message;

# returns a string, starting from the first non-whitespace character
def SkipWhitespace(text):
	while text[0] == " " or text[0] == "\t" or text[0] == "\n":
		text = text[1:];
	return text;

# checks that the text starts with the literal
def MatchText(text, literal):
	text = SkipWhitespace(text);
	if text[:len(literal)] == literal:
		return (text[len(literal):], literal);
	raise ParseError("Expected {}, received {}".format(literal, text[:len(literal)]));

# checks that the text starts with an integer
intRegex = re.compile(r"\+?(\-?\d+)");
def MatchInt(text):
	text = SkipWhitespace(text);
	match = intRegex.match(text);
	if match != None:
		return (text[match.end(1):], int(match.group(1)));
	raise ParseError("Expected <int>, received {}".format(text[:16]));

# checks that the text starts with a float (or integer)
floatRegex = re.compile(r"\+?(\-?\d+(.\d*)?)");
def MatchFloat(text);
	text = SkipWhitespace(text);
	match = floatRegex.match(text);
	if match != None:
		return (text[match.end(1):], float(match.group(1)));
	raise ParseError("Expected <float>, received {}".format(text[:16]));

# a name (used as key, so anything up to a ':')
nameRegex = re.compile(r"([^\:]+)");
def MatchName(text):
	text = SkipWhitespace(text);
	match = nameRegex.match(text);
	if match != None:
		return (text[match.end(1):], match.group(1));
	raise ParseError("Expected <name>, received {}".format(text[:16]));
