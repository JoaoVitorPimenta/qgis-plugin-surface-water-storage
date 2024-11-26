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

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingException,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber)
from numpy import savetxt
from .algorithms.algorithmGraph import executePlugin

class createAreaVolumeElevationGraphAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_DEM = 'INPUT_DEM'
    AREA = 'AREA'
    VERTICAL_SPACING = 'VERTICAL_SPACING (m)'
    DATA = 'DATA'
    GRAPH = 'GRAPH'


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DEM,
                self.tr('DEM'),
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.AREA,
                self.tr('Area'),
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.VERTICAL_SPACING,
                'Vertical step (in meters):',
                type=QgsProcessingParameterNumber.Double,
                defaultValue='0.00'
            )
        )


        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.DATA,
                self.tr('Data'),
                fileFilter='CSV files (*.csv)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.GRAPH,
                self.tr('Graph'),
                fileFilter='HTML files (*.html)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        demLayer = self.parameterAsRasterLayer(
                                             parameters,
                                             self.INPUT_DEM,
                                             context
                                             )
        areaInput = self.parameterAsVectorLayer(
                                                        parameters,
                                                        self.AREA,
                                                        context
                                                        )
        verticalSpacingInput = self.parameterAsDouble(
                                                        parameters,
                                                        self.VERTICAL_SPACING,
                                                        context
                                                        )
        # Compute the number of steps to display within the progress bar and
        # get features from source
        if verticalSpacingInput <=0:
            raise QgsProcessingException(
                'Vertical spacing must be greather than 0'
                                         )

        featuresCount = sum(1 for _ in areaInput.getFeatures())
        if featuresCount > 1:
            raise QgsProcessingException(
                'The layer has more than one feature!'
            )

        demPr = demLayer.dataProvider()
        demArray = []
        feature = next(areaInput.getFeatures())
        fGeometry = feature.geometry()
        fBBox = fGeometry.boundingBox()
        demBlock = demPr.block(1,fBBox,demLayer.width(),demLayer.height())
        demNoDataValue = demBlock.noDataValue()

        for j in range(demLayer.height()):
            for k in range(demLayer.width()):
                demArray.append((demBlock).value(j,k))

        if all(x == demNoDataValue for x in demArray):
            raise QgsProcessingException(
                'The feature is only in NODATA values'
                )

        if fGeometry.intersects(demLayer.extent()) is False:
            raise QgsProcessingException(
                "The feature don't intersects the DEM extent"
            )

        demCellX = demLayer.rasterUnitsPerPixelX()
        demCellY = demLayer.rasterUnitsPerPixelY()

        if (fBBox.width() < demCellX) and (fBBox.height() < demCellY):
            raise QgsProcessingException(
                'The feature is smaller than raster pixel size'
            )

        AHV, graph = executePlugin(demLayer,
                                    areaInput,
                                    verticalSpacingInput)

        areaHeightVolumeDataPath = self.parameterAsFileOutput(parameters,
                                                                self.DATA,
                                                                context)

        savetxt(
                areaHeightVolumeDataPath,
                AHV,
                delimiter=',',
                header='Area (m2),Height (m),Volume (m3)',
                comments='',
                fmt='%s'
                )

        graphPath = self.parameterAsFileOutput(parameters,
                                                self.GRAPH,
                                                context)

        graph.write_html(graphPath)

        return {self.DATA:areaHeightVolumeDataPath,
                self.GRAPH:graphPath}



    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Area-Volume-Elevation graph'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr("""
                <html>
                    <head>
                        <title>Area-Volume-Height graph</title>
                    </head>
                    <body>
                        <p>
                            The raster and the area needs be in projected CRS (use meters).
                        </p>
                        <p>
                            The DEM needs to be hydrologically consistent (no sinks).
                        </p>
                        <p>
                            Its recommended that the vertical step be 1.
                        </p>
                    </body>
                </html>
                """)

    def createInstance(self):
        return createAreaVolumeElevationGraphAlgorithm()