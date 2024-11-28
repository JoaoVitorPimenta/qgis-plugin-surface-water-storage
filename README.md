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

# Tools
This plugin offers 2 tools to help with the study of a surface water storage, are they: 

## Create a inundation area
This tool create a vectorized inundation area from a DEM, a area and from a parameter provided by the user, which could be elevation, height, area or volume

Inputs:
DEM - Digital Elevation Model with altimetry related to the area to be analyzed
Area - Vector polygon that is the area to be analyzed
Parameter - Parameter of the Area-Volume-Elevation curve used to find the elevation that the water reaches and return the other parameters of the curve to the user
Parameter Value - The value of the chosen parameter, in meters, meters squared or meters cubed
Vertical step - The differencial in elevation for calculating the Area-Volume-Elevation curve (the smaller the value, the more accurate and slow the algorithm will be)

Output:
Inundation area - The area flooded by elevation as a function of the parameter


## Create a graph 
This tool creates an area x elevation x capacity graph, widely used to analyze how elevation relates to area and storable volume in topography, it also generates area, elevation and capacity data as a .csv file

Inputs:
DEM - Digital Elevation Model with altimetry related to the area to be analyzed
Area - Vector polygon that is the area to be analyzed
Vertical step - The difference in elevation for calculating the Area-Volume-Elevation curve (the smaller the value, the more accurate and slow the algorithm will be)

Output: 
Data - The data of the points used to form the area-elevation-volume graph, in .csv
Graph - The area-elevation-volume graph for the area and using the DEM data


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