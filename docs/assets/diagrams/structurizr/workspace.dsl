workspace "Tanker24 - System Context" "System context diagram for the Tanker24 application" {

    !identifiers hierarchical

    model {
        user = person "User" "Car drivers"
        
        tanker24 = softwareSystem "Tanker24" "Web system for checking gas prices in the user's area."{
            webApp = container "User Interface" "VueJS" "Provides the web interface for searching gas prices and storing filling data."
            postgre = container "Data Store & Cache" "PostgreSQL" "Stores user data and caches gas price data."{
                tags "Database"
            }
            backend = container "Tanker24 Backend" "Python 3" "Handles business logic, user data, and integration with external services."
        
        }

        tankerkoenig = softwareSystem "Tankerkönig" "Free data provider for gas price data based on the Bundeskartellamt API." {
            tags "External"
        }

        osm = softwareSystem "OpenStreetMap" "Free map data provider for visualisation." {
            tags "External"
        }


        user -> tanker24.webApp "Request gas prices in area" "UI interaction"
        user -> tanker24.webApp "Store filling data" "UI interaction"

        tanker24.webApp -> tanker24.backend "Request user data" "REST"
        tanker24.backend -> tanker24.postgre "Reads user data" "SOCKET"
        tanker24.backend -> tanker24.postgre "Read gas price cache" "SOCKET"

        tanker24.backend -> tankerkoenig "Get current gas prices" "REST"
        tanker24.webApp -> osm "Get map" "REST"
    }

    views {
        systemContext tanker24 "Diagram1" {
            include *
        }

        container tanker24 "Diagram2" {
            include *
        }

        styles {
            element "Element" {
                color #f88728
                stroke #f88728
                strokeWidth 7
                shape roundedbox
            }
            element "Person" {
                color #0773af
                stroke #0773af
                shape person
            }
            element "Database" {
                color #04b015
                stroke #04b015
                shape cylinder
            }
            element "Boundary" {
                strokeWidth 5
            }
            
            element "External"{
                color #ed3124
                stroke #ed3124
            }
            relationship "Relationship" {
                thickness 4
            }
        }
    }

    configuration {
        scope softwaresystem
    }

}