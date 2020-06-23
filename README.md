# Drone Navigation Component

Components:
- Positioning system (TODO - Integration with RFID)
- Setup and Routing system (Complete for VCM)
- Drone Movement Command system (Complete for VCM)

The Navigation Component is being developed alongside the computational platform's Inventorying Component and Communications Component.

Currently, vcm.py can, given a set of nodes, route a path through all nodes, one vertical layer at a time. The route passes through the entirety of the aisles between nodes and only switches aisles once the current one is fully traversed. A perimeter can be set to specify an area of inspection.

Currently, tello_continuous_test.py can send commands to the drone in near-real-time through Wi-Fi.

Currently, main.py executes the route by giving the drone physical movement commands based on rotation by angle, horizontal traversal and vertical traversal.

Currently, tello_test.py can be used to produce graphs on the latest flight.