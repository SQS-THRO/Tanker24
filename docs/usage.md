---
icon: fontawesome/regular/play-circle
---

# Usage
The Tanker24 repository comes with two docker compose files. The file `compose.yaml` includes the default or so called skeleton version of the application. The database is completely empty and you must create an user on your own. The file `compose.demo.yaml` referes to a demo database which already includes some data and a user account with the username ``max@tanker24.eu`` with password ``Tanker24.eu``

## Start-up
Follow the [Installation Guide](installation.md) to start the necessary docker container. Then proceed with the steps below.

## Login

### Skeleton
The skeleton project is a blank installation of Tanker24. Before using the application, you need to create a user account with the invitation key that you specified in the `.env` file.

To create a user, open `localhost:3000` in your browser and click the **Get started** button in the top-right corner. A modal will appear and ask you to enter your user information and the invitation key.

### Demo
If you started the docker container with the demo composer command the database already contains a user. Go to `localhost:3000` and press the button labled "Sign in" to sign in as `max@tanker24.eu` with password `Tanker24.eu`.

## Usage

After logging in, you will be redirected to the map view. The map displays gas stations near your current location, including their current fuel prices. You can move around the map by dragging it with the left mouse button. 

On the left-hand side of the map view, you will find a list of nearby gas stations. This list is sorted by price in ascending order. You can change the selected fuel type using the dropdown menu next to the search bar at the top of the screen. The filter bar at the top of the list allows the user to filter through the list of stations in the current search radius by its location.

To record a refueling, click on a gas station icon on the map and then click **Record**. Enter the required data and click **Save**. Your refueling history can be viewed on your account page. From there, you can also delete records and export your refueling data as either a nested JSON file or a flat CSV file.

Tanker24 supports both light and dark themes. You can switch between them on your account page or by clicking the sun/moon icon next to the map button. For improved color accessibility, several color options are also available on the account page.
