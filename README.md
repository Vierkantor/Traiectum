TRAIECTUM
=========

Traiectum is a realistic* simulation** of trains***. It is meant to show a large-scale picture of a real train network, instead of the smaller-scale model railroad-type affairs.

Traiectum was (besides as an acronym for Not An Acronym For This Train Simulator) named after the Latin name for Utrecht, railway hub for the Netherlands and also the city of my university (cleverly named Utrecht University).

\* Not if you live outside the Netherlands or have any ideas how trains really work.

\*\* Simulating the wrong things mostly.

\*\*\* Dots that move over lines.

# Running

Find a nice version of [pygame](http://pygame.org) for your computer. Run train.py to start the simulation. (Note that it by default, and probably exclusively, runs under python 3.) After the data has been loaded, you will see a white (world) map with black lines and dots. Use the scroll wheel to zoom in or out and arrow keys (or WASD) to move.

# Data files

The simulation data is stored in data.txt and servicedata.txt, using a custom format. This is to make them human-readable(-ish) and easy to tweak by hand. Generally, different types of data are stored between type: and :end tokens. Data in the form of lists is usually represented by name: ... :end and other named things with name -> value. Other values are separated by commas. These files are encoded in UTF-8, because that is the only useful encoding ever made.

The program group.py takes all the text files in a folder called DataSources and makes one big servicedata.txt from them, automagically smooshing all service information together and generating enough trains to do these services. Pipe the output of this program to a **new** file to make sure it's correct, and replace servicedata.txt with it when you're satisfied it works.

# The map

The map is projected equirectangularly (with standard parallels at the center point to make it suck slightly less). This means that distances and shapes might be slightly messed up, but [who cares](http://xkcd.com/977/), right?

# Time

The clock starts at 2:00 in the night, when the Dutch train network starts up. There are a few trains already running around that time. Every second (very approximately, more like every 33 ticks), a minute will pass in the simulation. This speed can be adjusted with your +/- keys. Speeding up time might make things a little less accurate that it was before(!) but it shouldn't lead to catastrophes. When the next day rolls around, things will probably break because services will not end where they start. When they suddenly have to go back to where they started, things will get messy.

# Trains

Trains are represented by the red dots on your map. The label next to them is their name (which is usually their train type + number). A train has a schedule from the start of the day (2:00) up to the end of the day (26:00), made up of the services they do that day. They start out at the location of the initial order of their initial service, and wait until that order passes. If the next order is somewhere else, they will find the quickest (hopefully) path to their destination and go there. Currently, they continuously accelerate until the destination is the next node they will visit, then they will brake to arrive exactly on time. Obviously, this is inaccurate, but measuring distances gets hard quickly when you're doing it for hundreds of trains. After they stop at the destination, they will wait until it's time to leave again, and follow the next route to their next destination.

Schedules are the list of services a train follows. group.py generates these automatically based on the files in DataSources.

# Services

A service is a list of destinations and arrival/departure times. A train running a service will travel to each destination in turn, waiting until it can depart again. If the service lists two destinations that are the same (but with different times), the train will try to arrive at the first time and leave at the second time. An order is a single time-destination pair from a service.

Services are listed in servicedata.txt under services:, as a named list of orders, also created by group.py. You can add new ones by making a text file in DataSources and filling it. The syntax looks like this:

    Eurostar 9080:
    	6, 40, STP
    	6, 58, EBD
    	7, 24, AFK
    	9, 17, Paris_Nord
    :end

# Nodes

Nodes are just points on the map. Places and lines are defined based on nodes.

In data.txt, nodes are listed under nodes:, as a named pair of coordinates.

# Places

Places are names for nodes. Multiple places can point to the same node but not otherwise. An order's destination is a place.

In data.txt, places are listed under places: as a named node id. To help manually inputting, they can also be added as a named node (which is still a named coordinate pair), in the nodes: section. For example:

    places:
    	Paris_Nord: 225
    :end

or:

    nodes:
    	Paris_Nord: 225: 48.88055, 2.35493
    :end

# Stations

Stations are groups of locations where passengers can transfer between trains.

In data.txt, stations are listed under stations: as a named location name. For example:

    stations:
    	Paris_Nord: Paris_Nord
    :end

# Links

Links represent a route trains can travel on. They are generally two-directional (so a link from node 1 to 2 also makes a link between 2 and 1). A planned feature is to prevent this explicitly somewhere, but this is not yet implemented.

In data.txt, links are listed under links: as a pair of nodes. When reading this, train.py automagically adds in the opposite direction of this link if it doesn't exist yet. Also, to link a series of nodes you can simply write <begin> ... <end>, which will link everything between the beginning and end node in order (numerically). For example:

    links:
    	225: 1492
    	
    	1943 ... 1515
    :end

# Pathfinding

Every time a train gets a new destination, it finds a path towards it. This is done with the A* algorithm. If there is no connection to the start and end nodes, the train will search through all the nodes in the map before giving up, which will take quite a bit of time. If you notice lag spikes, make sure there is a connection between all the nodes in your map! To help you find the problem, a debug message is emitted when the route can't be found. (Also, you can see trains with a giant delay because they can't follow a non-existent route).
