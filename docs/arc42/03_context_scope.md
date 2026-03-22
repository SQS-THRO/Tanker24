# 3. Context and scope
The system context and scope can be easily described with a C4-Model System Context (Level 1) diagram. It nicely displays all interacting partners on high level while specifying required interface to users and external systems.
### System Context Diagram (C4-Model Level 1)

=== "PlantUML"
    ```puml
    @startuml C4_Elements
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

    Person(user, "User", "German car driver")
    System(tanker24, "Tanker24", "Web system for checking gas prices in the users area.")
    System_Ext(tankerkoenig, "Tankerkönig", "Free data provider for gas price data based on the Bundeskartelamt API.")
    System_Ext(osm, "OpenStreeMap", "Free map data provider for visualisation.")
    Rel_R(user, tanker24, "Request gas prices for area.", "Web Interface")
    Rel_R(user, tanker24, "Save filling history.", "Web Interface")
    Rel_R(tanker24, tankerkoenig, "Request gas price Data", "REST")
    Rel(tanker24, osm, "Request map data", "REST")
    @enduml
    ```

=== "Structurizr"
    [System Context Diagram](../assets/images/Context_diagram_structurizer.svg)