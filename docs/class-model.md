---
icon: simple/uml
---

# Class model

## System Context Diagram (C4-Model Level 1)
!!! info

    === "Plant UML"

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

        ```
        ```


## Container Diagram (C4-Model Level 2)
!!! info

    === "Plant UML"

        ```puml
        @startuml
        !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

        !define osaPuml https://raw.githubusercontent.com/Crashedmind/PlantUML-opensecurityarchitecture2-icons/master
        !include osaPuml/Common.puml
        !include osaPuml/User/all.puml

        !include <office/Servers/database_server>
        !include <office/Servers/file_server>
        !include <office/Servers/application_server>
        !include <office/Concepts/service_application>
        !include <office/Concepts/firewall>

        AddPersonTag("customer", $sprite="osa_user_large_group", $legendText="aggregated user")

        AddContainerTag("webApp", $sprite="application_server", $legendText="web app container")
        AddContainerTag("db", $sprite="database_server", $legendText="database container")
        AddContainerTag("conApp", $sprite="service_application", $legendText="console app container")

        Person_Ext(user, "German car drivers", $tags= "customer")

        System_Boundary(tanker24Application, "Tanker24"){
            Container(web_app, "User Interface", "Svelte", $tags="webApp")
            ContainerDb(postgre, "Data Store & Cache", "PostgreSQL", $tags="db")
            Container(backend, "Tanker24 Backend", "Python 3", $tags="conApp")

            Rel_D(web_app, backend, "Request user data", "REST")
            Rel_L(backend, postgre, "Reads user data", "SOCKET")
            Rel_L(backend, postgre, "Read gas price cache", "SOCKET")
        }

        Rel(user, web_app, "Request gas prices in area.", "UI interaction")
        Rel(user, web_app, "Store filling data", "UI interaction")

        Container_Ext(tankerkoenig, "Tankerkönig", $tags="conApp")
        Rel_R(backend, tankerkoenig, "Get current gas prices", "REST")
        Container_Ext(osm, "OpenStreetMap", $tags= "conApp")
        Rel_R(web_app,osm,"Get map", "REST")

        @enduml
        ```

    === "Structurizr"

        ```
        ```

