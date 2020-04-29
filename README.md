# Drone Navigation Component

Components:
- Positioning system (TBD)
- Setup and Routing system
- Drone Movement Command system

The Navigation Component is being developed alongside the computational platform's Inventorying Component and Communications Component.

Currently, vcm.py can, given a set of nodes, route a path through all nodes. The route passes through the entirety of the aisles between nodes and only switches aisles once the current one is fully traversed.
TBA: Vertical movement subsystem

Currently, tello_continuous_test can send commands to the drone in near-real-time through Wi-Fi.
