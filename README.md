# mbtaonbus
On-bus prediction screen prototype using MBTA API.  (Ubuntu/Python/Flask) 
{not affiliated with the [MBTA](https://www.mbta.com/)}

### Project Goal:
Demonstrate an on board passenger information screen for a transit vehicle showing a map of the current 
location, route/stops, rail lines and a list of upcoming stops with predictions.  Keep the setup lightweight
on a simple Ubuntu/Python/Flask platform for quick demonstration in a virtual machine for eventual installation
on on-board router or Raspbery Pi equipment.  

See image at ExampleScreenShot.png included in the repository.  
![ExampleScreenShot](https://github.com/mhaynes001/mbtaonbus/blob/master/ExampleScreenShot.png?raw=true)

### Setup: 
1. Get MBTA key
2. Get Mapbox key
3. Set up Ubuntu Server main user as "user" (command line only with Open SSH)
4. Pull down repositiry 'git ...'
5. Run '~/mbtaonbus/bash_scripts/setup.sh'
6. Navigate to http://mbtaonbus/ and pick a bus
7. Size window to nnn x nnn 
8. Optionally set up the screen user by running'~/mbtaonbus/bash_scripts/screen_setup.sh'

### Data Sources: 
- [MBTA GTFS](https://www.mbta.com/developers/gtfs)
- [MBTA V3 API](https://www.mbta.com/developers/v3-api)
- [MBTA V3 API Documentation & Key request](https://api-v3.mbta.com/)

### Back end: 
- [jquery](https://jquery.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Leaflet](https://leafletjs.com/)
- [Mapbox](https://www.mapbox.com/)

### To do: 
- [ ] Error handling
- [ ] List all buses on main page
- [ ] Set bus ID as system variable if exists go directly to predictions for that bus
- [ ] Black background version
- [ ] Set default virtual machine resolution on boot.
- [ ] Start brand new GitHub repository rebuilding based on GTFS-RT feed and test with other transit properties

