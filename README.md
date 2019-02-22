# mbtaonbus
On-bus prediction screen prototype using MBTA API.  (Ubuntu/Python/Flask) 
{not affiliated with the [MBTA](https://www.mbta.com/)}

>**Prototype code, not production ready!**

### Project Goal:
Demonstrate an on board passenger information screen for a transit vehicle showing a map of the current 
location, route/stops, rail lines and a list of upcoming stops with predictions.  Keep the setup lightweight
on a simple Ubuntu/Python/Flask platform for quick demonstration in a virtual machine for eventual installation
on on-board router or Raspbery Pi equipment.  

See image at ExampleScreenShot.png included in the repository:  
![ExampleScreenShot](ExampleScreenShot.png?raw=true)

### Setup: 
1. Get MBTA key [request here](https://api-v3.mbta.com/)
2. Get [Mapbox](https://www.mapbox.com/) key & set up map and style
3. Set up Ubuntu Server main user as "user" (command line only with Open SSH)
4. Pull down repositiry 'git ...' (Update variables.template as variables.env with your key values)
5. Run '~/mbtaonbus/bash_scripts/setup.sh'
6. Navigate to http://mbtaonbus/ on local network and pick a bus
   (or run screen_setup.sh to run a browser display locally in the VM)
7. Size VM window to 1024 x 786

### Data Sources: 
- [MBTA GTFS](https://www.mbta.com/developers/gtfs)
- [MBTA V3 API](https://www.mbta.com/developers/v3-api) with [Documentation & Key request](https://api-v3.mbta.com/)

### Back end: 
- [Ubuntu 18.04](https://www.ubuntu.com/download/server)
- [Python3](https://www.python.org/)
- [jquery](https://jquery.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Leaflet](https://leafletjs.com/)
- [Mapbox](https://www.mapbox.com/)

### To do: 
- [ ] Error handling
- [ ] List all buses on main page (not just first 50)
- [ ] Set bus ID as system variable if exists go directly to predictions for that bus
- [ ] Black background version
- [ ] Set default virtual machine resolution on boot.
- [ ] Start brand new GitHub repository rebuilding based on GTFS-RT feed and test with other transit properties

### Possible on-board solution: 
[LILEE Systems](https://www.lileesystems.com/) was the inspiration for this prototype.  They have an on-vehicle router that supports Ubuntu Virtual Machines and has an HDMI port to support a screen.  [STS Datasheet](https://www2.lileesystems.com/lilee-transair-sts-1020_datasheet).  Soon I will add in a small zip file of scripts to set up a Raspberry Pi 0W to power a 7" screen.     
