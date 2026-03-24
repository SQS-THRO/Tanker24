# 4. Solution strategy
This chapter describes the fundamental architecture decisions made by the project team. These decisions shape the architecture of our product.

## Container Diagram (C4-Model Level 2)
The container diagram shows how Tanker24 is structured internaly without putting a too big focus on implementation details.
=== "PlantUML"
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
        Container(web_app, "User Interface", "VueJS", $tags="webApp")
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
    [System Context Diagram](../assets/images/Container_diagram_structurizer.svg)


## Technology decisions
As per organizational constrainc OC-3 all relevant technology decisions need to be documented as architecture decision records (ADR). The following page lists all ADRs: [here](../decisions/index.md) To ensure the quality of the ADRs they use a shared comprehensive template.

## Quality Goals

!!! warning
    How to write quality goals for the functional staibility aspect?
    Maybe specify the solution approach with TDD?

|Quality Goal|Scenario|Solution approach|Link to Details|
|--|---|--|--|
|Reliability|The Tankerkoenig data API is unavailable.|Implement soft retry with increasing waits.|link to issue|
|Reliability|The Tankerkoenig data API is unavailable.|Implement caching to deliver at least information on gas stations in the area.|link to issue|
|Reliability|The Tankerkoenig data API is unavailable.|Implement soft retry with increasing waits.|link to issue|
|Security|A user requests user specific data.|Implement a secure user based authentication system with e.g. pin codes in the API and login.|link to issue|
|Transferability|The user wants to export it's data as JSON.|Extend a generic data aggregation class to output the data in JSON format.|Link to issue|
|Transferability|The user wants to export it's data as a semicolon separated csv.|Extend a generic data aggregation class to output the data in the semicolon separated csv format.|Link to issue|
