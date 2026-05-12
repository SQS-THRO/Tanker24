---
icon: fontawesome/solid/cubes
---

# Entity-Relationship Model
```puml
@startuml
left to right direction

entity "User" as User {
  *id
  *invitation_key_id
  --
  email
  hashed_password
  is_active
  is_superuser
  is_verified
  forename
  surname
}

entity "Cars" as Car {
  *id
  *owner_id
  --
  type
  license_plate_number
}

entity "Fuel Types" as FuelType {
  *id
  --
  name
}

entity "History Records" as HistoryRecord {
  *id
  *car_id
  *fuel_type_id
  --
  timestamp
  mileage
  price_per_litre
  litres
}

entity "Tankerkoening Stations" as TankerkoenigStation {
  *tankerkoenig_id
  --
  name
  brand
  street
  house_number
  post_code
  place
  latitude
  longitude
  distance
  diesel
  e5
  e10
  is_open
  cached_at
  cache_lat
  cache_lon
  cache_radius
}

entity "Stations" as Stations {
  *id
  *owner_id
  --
  name
  description
  latitude
  longitude
}

entity "Invitation Keys" as InvitationKeys{
  *id
  --
  key
}

User ||--|| InvitationKeys: has
User ||--o{ Car : owns
Car ||--o{ HistoryRecord : has
FuelType ||--o{ HistoryRecord : has

@enduml
```