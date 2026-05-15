---
icon: fontawesome/regular/play-circle
---

# Usage
The Tanker24 repository comes with two docker compose files. The file `compose.yaml` includes the default or so called skeleton version of the application. The database is completely empty and you must create an user on your own. The file `compose.demo.yaml` referes to a demo database which already includes some data and a user account with the username ``max@tanker24.eu`` with password ``Tanker24.eu``

## Start-up
Follow the [Installation Guide](installation.md) to start the necessary docker container. Then proceed with the steps below.

## Skeleton
The skeleton is a blank installation of the project. You must create a user with the invitation key specified by you in the .env file. To create the user go to: `localhost:3000` and press the button labeled "Get started" in the top right corner.

The modal will prompt you to enter your user information and the invitation key.

Once logged in you are forwarded to the map. The map will display all gas stations around you with their current prices. Move around the map by either using left click + drag or by entering a location in the search bar.

continue once frontend is done...

## Demo
The database already contains a user. Go to `localhost:3000` and press the button labled "Sign in" to sign in as `max@tanker24.eu` with password `Tanker24.eu`.

Once logged in you are forwarded to the map. The map will display all gas stations around you with their current prices. Move around the map by either using left click + drag or by entering a location in the search bar.

continue once frontend is done...