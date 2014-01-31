TRAIECTUM
=========

Traiectum is a realistic* simulation** of trains***. It is meant to show a large-scale picture of a real train network, instead of the smaller-scale model railroad-type affairs.

Traiectum was (besides as an acronym for Not An Acronym For This Train Simulator) named after the Latin name for Utrecht, railway hub for the Netherlands and also the city of my university (cleverly named Utrecht University).

\* Not if you live outside the Netherlands or have any ideas how trains really work.

\*\* Simulating the wrong things mostly.

\*\*\* Dots that move over lines.

# Running

Find a nice version of [pygame](http://pygame.org) for your computer. Run train.py to start the simulation. After the data has been loaded, you will see a white (world) map with black lines and dots. Use the scroll wheel to zoom in or out and arrow keys (or WASD) to move.

# Data files

The simulation data is stored in data.txt and servicedata.txt, using a custom format. This is to make them human-readable(-ish) and easy to tweak by hand. Generally, different types of data are stored between type: and :end tokens. Data in the form of lists is usually represented by name: ... :end and other named things with name -> value. Other values are separated by commas.

# The map

The map is projected equirectangularly (with standard parallels at the center point to make it suck slightly less). This means that distances and shapes might be slightly messed up, but [who cares](http://xkcd.com/977/), right?

# Time

The clock starts at 2:00 in the night, when the Dutch train network starts up. There are a few trains already running around that time. Every second (very approximately, more like every 33 ticks), a minute will pass in the simulation. This speed can be adjusted with your +/- keys. Speeding up time might make things a little less accurate that it was before(!) but it shouldn't lead to catastrophes. When the next day rolls around, things will probably break because services will not end where they start. When they suddenly have to go back to where they started, things will get messy.

# Trains

Trains are represented by the red dots on your map. The label next to them is their name (which is usually their train type + number). A train has a schedule from the start of the day (2:00) up to the end of the day (26:00), made up of the services they do that day. They start out at the location of the initial order of their initial service, and wait until that order passes. If the next order is somewhere else, they will find the quickest (hopefully) path to their destination and go there. Currently, they continuously accelerate until the destination is the next node they will visit, then they will brake to arrive exactly on time. Obviously, this is inaccurate, but measuring distances gets hard quickly when you're doing it for hundreds of trains. After they stop at the destination, they will wait until it's time to leave again, and follow the next route to their next destination.

Trains are listed in servicedata.txt under trains:, in a named list of service names.

# Schedules

Schedules are a list of services a train follows. massage.py can generate these automatically or they can be manually entered.

In servicedata.txt, a train's schedule is listed under their name as a list of service names.

# Services

A service is a list of destinations and arrival/departure times. A train running a service will travel to each destination in turn, waiting until it can depart again. If the service lists two destinations that are the same (but with different times), the train will try to arrive at the first time and leave at the second time.

Services are listed in servicedata.txt under services:, as a named list of orders.

# Orders

An order is a single time-destination pair from a service. 

In servicedata.txt, their format is hours, minutes, location.

# Nodes

Nodes are just points on the map. Locations and lines are defined based on nodes.

In data.txt, nodes are listed under nodes:, as a named pair of coordinates.

# Locations

Locations are names for nodes. Multiple locations can point to the same node but not otherwise. An order's destination is its location.

In data.txt, locations are listed under places: as a named node id. To help manually inputting, they can also be added as a named node (which is still a named coordinate pair), in the nodes: section.

# Links

Links represent a route trains can travel on. They are generally two-directional (so a link from node 1 to 2 also makes a link between 2 and 1). A planned feature is to prevent this explicitly somewhere, but this is not yet implemented.

In data.txt, links are listed under links: as a pair of nodes. When reading this, train.py automagically adds in the opposite direction of this link if it doesn't exist yet.
