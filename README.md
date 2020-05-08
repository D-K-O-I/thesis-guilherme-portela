# Drone Navigation Component

Components:
- Positioning system (TBD)
- Setup and Routing system
- Drone Movement Command system

The Navigation Component is being developed alongside the computational platform's Inventorying Component and Communications Component.

Currently, vcm.py can, given a set of nodes through an interpreter, route a path through all nodes, one vertical layer at a time. The route passes through the entirety of the aisles between nodes and only switches aisles once the current one is fully traversed. A perimeter can be set to specify an area of inspection.

Currently, tello_continuous_test.py can send commands to the drone in near-real-time through Wi-Fi.

Sample commands are located in main.py
