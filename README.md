# Surface Water Storage
This plugin can help the user create a pre-design for a reservoir or study water storage in large lakes, for example.

## Technologies
The following technologies were used in processing the algorithms of this plugin:  
QGIS  
GDAL  
Numpy  
Scipy  
Plotly  

## Installation
With QGIS open, follow these steps: plugins -> manage and install plugins -> install from ZIP
Then select the ZIP containing this plugin -> install plugin    
or place this plugin in the folder corresponding to plugins installed in QGIS,
normally found in the path:   C:\Users\User\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\

## Tools
This plugin offers 2 tools to help with the study of a surface water storage, are they: 

Create a inundation area - this tool create a vectorized inundation area from a DEM, a area and from a parameter provided by the user, which could be elevation, height, area or volume

Create a graph - This tool creates an area x elevation x capacity graph, widely used to analyze how elevation relates to area and storable volume in topography, it also generates area, elevation and capacity data as a .csv file

## Recommendations 
All layers must be in a CRS that uses meters and the DEM needs to be hydrologically consistent (no sinks)

## Acknowledgment
Special thanks to the authors of all the technologies used in this plugin and who made it possible,
to my parents and friends, to my teachers, and to the giants who, by standing on their shoulders,
allowed me to see further.

## Contributing
This software readily accepts modifications and optimizations, as long as they make sense for proper functioning and user comfort.

## License
[GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html)