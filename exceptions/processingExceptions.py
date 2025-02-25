# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SurfaceWaterStorage
                                 A QGIS plugin
 This plugin calculates the area flooded by water volume, height, elevation 
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

__author__ = 'João Vitor Pimenta'
__date__ = '2024-07-13'
__copyright__ = '(C) 2024 by João Vitor Pimenta'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingException

def verifyIfHeightValueIsInTheCurve (parameterValue,elevations,verticalSpacing):
    '''
    Check if the height value is on the curve
    '''

    if parameterValue < verticalSpacing:
        raise QgsProcessingException(
            'This value is below the minimum value of the curve: ' + str(verticalSpacing)
            )
    if parameterValue > (elevations[-1]-elevations[0] + verticalSpacing):
        raise QgsProcessingException(
            'This value is above the maximum value of the curve: ' + str(elevations[-1]-elevations[0] + verticalSpacing)
            )
def verifyIfElevationValueIsInTheCurve (parameterValue,elevations):
    '''
    Check if the elevation value is on the curve
    '''

    if parameterValue < elevations[0]:
        raise QgsProcessingException(
            'This value is below the minimum value of the curve: ' + str(elevations[0])
            )
    if parameterValue > elevations[-1]:
        raise QgsProcessingException(
            'This value is above the maximum value of the curve: ' + str(elevations[-1])
            )
def verifyIfAreaValueIsInTheCurve (parameterValue,areas):
    '''
    Check if the area value is on the curve
    '''

    if parameterValue < areas[0]:
        raise QgsProcessingException(
            'This value is below the minimum value of the curve: ' + str(areas[0])
            )
    if parameterValue > areas[-1]:
        raise QgsProcessingException(
            'This value is above the maximum value of the curve: ' + str(areas[-1])
            )
def verifyIfVolumeValueIsInTheCurve (parameterValue,volumes):
    '''
    Check if the volume value is on the curve
    '''

    if parameterValue < volumes[0]:
        raise QgsProcessingException(
            'This value is below the minimum value of the curve: ' + str(volumes[0])
            )
    if parameterValue > volumes[-1]:
        raise QgsProcessingException(
            'This value is above the maximum value of the curve: ' + str(volumes[-1])
            )
def verifyNumberOfPointsInCurve (areaHeightCurve):
    '''
    Checks whether there are a sufficient number of points
    on the generated curve for numerical integration
    '''

    if len(areaHeightCurve) <= 2:
        raise QgsProcessingException(
            'Insufficient number of points for the Area-Volume-Elevation curve!'
        )
