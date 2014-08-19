import Data;
import SimObject;

services = {};

class Service(SimObject.SimObject):
	def __init__(self, attrs, name, orders):
		SimObject.SimObject.__init__(self, attrs);
		
		self.name = name;
		self.orders = orders;
	
	# add a new order to our orders
	def Append(self, order):
		self.orders.append(order);

# returns a new service that starts the specified amount of time later
def Add(time, service):
	return Service(service.attrs, service.name, list((order[0] + time, order[1]) for order in service.orders));

# turns a list of service names into an actual schedule
def TrainSchedule(serviceNames):
	result = [];
	
	for name in serviceNames:
		try:
			for order in services[name].orders:
				result.append((order[0], Data.Place(order[1])));
		except KeyError:
			print(services);
	
	# add orders for the start and end of the day
	result.append((0, result[0][1]));
	result.append((1560, result[-1][1]));
	
	# make sure the orders are in chronological... order
	return sorted(result);
