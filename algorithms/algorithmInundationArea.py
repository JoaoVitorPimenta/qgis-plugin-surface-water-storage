"""
/***************************************************************************
 SurfaceWaterStorage
                                 A QGIS plugin
 This plugin calculates the inundation area by water volume, height, elevation
 or area, and the Area-Elevation-Volume graph
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-11-13
        copyright            : (C) 2024 by João Vitor Pimenta
        email                : jvpjoaopimenta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessingException,
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsField)
import processing
from numpy import loadtxt, append, column_stack
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d

def executePlugin (dem,area,selectedParameter,parameterValue,spacing):
    '''
    uses input parameters to execute plugin functions
    '''
    hypsometricCurve = generateHypsometricCurves(dem,area,spacing)
    verifyNumberOfPointsInCurve(hypsometricCurve)
    AHV = calculateAreaHeightVolume(hypsometricCurve)
    verifyIfParameterValueIsInTheCurve (AHV,selectedParameter,parameterValue,spacing)
    waterElevation, waterHeight, waterArea, waterVolume = findParameter(AHV,
                                                    selectedParameter,
                                                    parameterValue,
                                                    spacing)
    inundAreaClipped = clipInundationArea(dem,area)
    inundAreaReclassified = reclassifyInundationArea(inundAreaClipped,
                                                    waterElevation)
    inundAreaVectorized = vectorizeInundationArea(inundAreaReclassified)
    inundAreaDissolved = dissolveInundationArea(inundAreaVectorized)
    inundAreaWAttributes = addAttributes(inundAreaDissolved,
                                            waterElevation,
                                            waterHeight,
                                            waterArea,
                                            waterVolume)

    return inundAreaWAttributes
def generateHypsometricCurves (dem,area,step):
    '''
    generates hypsometric curve data
    '''
    params = {
            'INPUT_DEM':dem,
            'BOUNDARY_LAYER':area,
            'STEP':step,
            'USE_PERCENTAGE':False,
            'OUTPUT_DIRECTORY':'TEMPORARY_OUTPUT'
    }
    hypsometricCurve = processing.run(
                                      "qgis:hypsometriccurves",
                                      params
                                      )['OUTPUT_DIRECTORY']
    maskName = area.sourceName()
    features = area.getFeatures()
    feature = next(features, None)
    featureID = feature.id()
    path = hypsometricCurve+'/histogram_'+maskName+'_'+str(featureID)+'.csv'

    return path
def verifyNumberOfPointsInCurve (areaHeightCurve):
    '''
    Checks whether there are a sufficient number of points
    on the generated curve for numerical integration
    '''
    data = loadtxt(areaHeightCurve, delimiter=',',skiprows=1)

    if len(data) <= 2:
        raise QgsProcessingException(
            'Insufficient number of points for the Area-Volume-Elevation curve!'
        )
def calculateAreaHeightVolume (areaHeightCurve):
    '''
    integrates the hypsometric curve, generating elevation-area-volume data
    '''
    data = loadtxt(areaHeightCurve, delimiter=',',skiprows=1)

    xd = data[:, 0].tolist()
    yd = data[:, 1].tolist()

    integration = cumulative_trapezoid(xd,yd)
    integrationComplet = append(integration,0)
    data_with_integration = column_stack((data,integrationComplet))
    dataWoLastRow = data_with_integration[:-1]

    return dataWoLastRow
def verifyIfParameterValueIsInTheCurve (dataAHV,parameter,parameterValue,verticalSpacing):
    '''
    Checks whether in the curve with area, elevation and volume data
    the value given as input by the user exists in the curve
    '''
    HEIGHT_PARAMETER = 'HEIGHT (m)'
    ELEVATION_PARAMETER = 'ELEVATION (m)'
    AREA_PARAMETER = 'AREA (m2)'
    VOLUME_PARAMETER = 'VOLUME (m3)'

    volumes = dataAHV[:, 2]
    elevations = dataAHV[:, 1]
    areas = dataAHV[:, 0]

    errorMessageBelow = (
        'This value is below the minimum value of the curve: '
        )
    errorMessageAbove = (
        'This value is above the maximum value of the curve: '
        )

    if parameter == HEIGHT_PARAMETER:

        if parameterValue < verticalSpacing:
            raise QgsProcessingException(
                errorMessageBelow + str(verticalSpacing)
                )
        if parameterValue > (elevations[-1]-elevations[0] + verticalSpacing):
            raise QgsProcessingException(
                errorMessageAbove + str(elevations[-1]-elevations[0] + verticalSpacing)
                )
                                                                                                
    if parameter == ELEVATION_PARAMETER:

        if parameterValue < elevations[0]:
            raise QgsProcessingException(
                errorMessageBelow + str(elevations[0])
                )
        if parameterValue > elevations[-1]:
            raise QgsProcessingException(
                errorMessageAbove + str(elevations[-1])
                )
        
    if parameter == AREA_PARAMETER:

        if parameterValue < areas[0]:
            raise QgsProcessingException(
                errorMessageBelow + str(areas[0])
                )
        if parameterValue > areas[-1]:
            raise QgsProcessingException(
                errorMessageAbove + str(areas[-1])
                )
        
    if parameter == VOLUME_PARAMETER:

        if parameterValue < volumes[0]:
            raise QgsProcessingException(
                errorMessageBelow + str(volumes[0])
                )
        if parameterValue > volumes[-1]:
            raise QgsProcessingException(
                errorMessageAbove + str(volumes[-1])
                )
def findParameter (dataAHV,parameter,parameterValue,verticalSpacing):
    '''
    from the elevation-area-volume data, interpolates the parameter value
    provided by the user in the curves and finds the equivalent elevation
    '''
    volumes = dataAHV[:, 2]
    elevations = dataAHV[:, 1]
    areas = dataAHV[:, 0]

    HEIGHT_PARAMETER = 'HEIGHT (m)'
    ELEVATION_PARAMETER = 'ELEVATION (m)'
    AREA_PARAMETER = 'AREA (m2)'
    VOLUME_PARAMETER = 'VOLUME (m3)'

    if parameter == HEIGHT_PARAMETER:

        heightAreaInterpolation = interp1d(elevations, areas, kind='linear')
        heightVolInterpolation = interp1d(elevations, volumes, kind='linear')

        waterElevation = float(parameterValue+elevations[0]-1)
        waterHeight = float(parameterValue)
        waterArea = float(heightAreaInterpolation(parameterValue+elevations[0]-1))
        waterVolume = float(heightVolInterpolation(parameterValue+elevations[0]-1))
        return waterElevation, waterHeight, waterArea, waterVolume

    if parameter == ELEVATION_PARAMETER:

        heightAreaInterpolation = interp1d(elevations, areas, kind='linear')
        heightVolInterpolation = interp1d(elevations, volumes, kind='linear')

        waterElevation = float(parameterValue)
        waterHeight = float(waterElevation - elevations[0] + verticalSpacing)
        waterArea = float(heightAreaInterpolation(parameterValue))
        waterVolume = float(heightVolInterpolation(parameterValue))

        return waterElevation, waterHeight, waterArea, waterVolume

    if parameter == AREA_PARAMETER:

        areaVolInterpolation = interp1d(areas, volumes, kind='linear')
        areaHeightInterpolation = interp1d(areas, elevations, kind='linear')

        waterElevation = float(areaHeightInterpolation(parameterValue))
        waterHeight = float(waterElevation - elevations[0] + verticalSpacing)
        waterArea = float(parameterValue)
        waterVolume = float(areaVolInterpolation(parameterValue))
        return waterElevation, waterHeight, waterArea, waterVolume

    if parameter == VOLUME_PARAMETER:

        volAreaInterpolation = interp1d(volumes, areas, kind='linear')
        volHeightInterpolation = interp1d(volumes, elevations, kind='linear')

        waterElevation = float(volHeightInterpolation(parameterValue))
        waterHeight = float(waterElevation - elevations[0] + verticalSpacing)
        waterArea = float(volAreaInterpolation(parameterValue))
        waterVolume = float(parameterValue)

        return waterElevation, waterHeight, waterArea, waterVolume
def clipInundationArea (dem, mask):
    '''
    clip the raster with the vector layer
    '''
    params = {
            'INPUT':dem,
            'MASK':mask,
            'NODATA':-99999,
            'CROP_TO_CUTLINE':False,
            'OUTPUT':'TEMPORARY_OUTPUT'
            }
    clip = processing.run(
                        "gdal:cliprasterbymasklayer",
                        params
    )['OUTPUT']
    demClipped = QgsRasterLayer(clip)

    return demClipped
def reclassifyInundationArea (demClipped,waterElev):
    '''
    reclassifies the raster based on the elevation obtained
    from the interpolation of the given parameter
    '''
    params = {
            'INPUT_RASTER':demClipped,
            'RASTER_BAND':1,
            'TABLE':['0',waterElev,'1',waterElev,'40000','0'],
            'NO_DATA':-9999,
            'RANGE_BOUNDARIES':0,
            'NODATA_FOR_MISSING':False,
            'DATA_TYPE':6,
            'OUTPUT':'TEMPORARY_OUTPUT'}
    reclassifing = processing.run(
                                    "native:reclassifybytable",
                                    params
    )['OUTPUT']
    demReclassified = QgsRasterLayer(reclassifing)

    return demReclassified
def vectorizeInundationArea (demReclassified):
    '''
    vectorizes the reclassified raster
    '''
    params = {
            'INPUT':demReclassified,
            'OUTPUT':'TEMPORARY_OUTPUT'
            }

    vectorization = processing.run(
                                    "gdal:polygonize",
                                    params
    )['OUTPUT']

    demVectorized = QgsVectorLayer(vectorization)

    return demVectorized
def dissolveInundationArea (vectorizedInundationArea):
    '''
    dissolves the flooded area features
    '''
    pr = vectorizedInundationArea.dataProvider()
    pr.setSubsetString("\"DN\" = 1")

    params = {
            'INPUT': vectorizedInundationArea,
            'FIELD':['DN'],
            'SEPARATE_DISJOINT':False,
            'OUTPUT':'memory:inundationArea'
            }
    inundationAreaDissolved = processing.run("native:dissolve",params)['OUTPUT']

    return inundationAreaDissolved
def addAttributes (inundArea, waterElev, waterHeight, waterArea, waterVolume):
    '''
    adds elevation-area-volume curve data to the flooded area attribute table
    '''
    elevField = QgsField('Elevation (m)', QVariant.Double,len=10, prec=2)
    heightField = QgsField('Height (m)', QVariant.Double, len=10, prec=2)
    areaField = QgsField('Area (m2)', QVariant.Double, len=10, prec=2)
    volumeField = QgsField('Volume (m3)', QVariant.Double, len=10, prec=2)
    inundationAreaPr = inundArea.dataProvider()
    inundationAreaPr.addAttributes([elevField,
                                    heightField,
                                    areaField,
                                    volumeField])
    inundArea.updateFields()
    inundArea.startEditing()
    elevationFieldID = inundArea.fields().indexOf('Elevation (m)')
    heightFieldID = inundArea.fields().indexOf('Height (m)')
    areaFieldID = inundArea.fields().indexOf('Area (m2)')
    volumeFieldID = inundArea.fields().indexOf('Volume (m3)')
    for features in inundArea.getFeatures():
        features.setAttribute(elevationFieldID, waterElev)
        features.setAttribute(heightFieldID, waterHeight)
        features.setAttribute(areaFieldID, waterArea)
        features.setAttribute(volumeFieldID, waterVolume)
        inundArea.updateFeature(features)
    inundArea.deleteAttributes([0,1])
    inundArea.commitChanges()

    return inundArea
