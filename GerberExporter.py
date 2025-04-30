# This file is part of Loop Inductance Minimizer KiCad plug-in 
# Copyright (C) 2025 Deverneton Saint Paul 
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, version 3. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program.  If not, see <https://www.gnu.org/licenses/>. 

import os
import pcbnew

def GerberExporter(board, outputDir):
    # Exports the PCB design as Gerber files into the selected directory
    
    # Ensure output directory exists
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # Initialize Gerber file writer
    plotctrl = pcbnew.PLOT_CONTROLLER(board)
    plotopt = plotctrl.GetPlotOptions()

    # Export options (per JLCPCB requirements) 
    plotopt.SetOutputDirectory(outputDir)
    plotopt.SetPlotValue(True)
    plotopt.SetPlotReference(True)
    plotopt.SetPlotInvisibleText(False)
    plotopt.SetUseAuxOrigin(True)
    #plotopt.SetExcludeEdgeLayer(False)
    plotopt.SetSketchPadsOnFabLayers(False)  
    #plotopt.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE) 
    plotopt.SetScale(1.0)  
    #plotopt.SetPlotMode(pcbnew.PCB_PLOT_PARAMS.FILLED) 
    plotopt.SetUseGerberAttributes(True)  
    plotopt.SetUseGerberX2format(True)  
    #plotopt.SetTentVias(True)  

    # Gerber Layers
    gerbLayers = [
        (pcbnew.F_Cu, "F_Cu"),
        (pcbnew.B_Cu, "B_Cu"),
        (pcbnew.F_Paste, "F_Paste"),
        (pcbnew.B_Paste, "B_Paste"),
        (pcbnew.F_SilkS, "F_SilkScreen"),
        (pcbnew.B_SilkS, "B_SilkScreen"),
        (pcbnew.F_Mask, "F_Mask"),
        (pcbnew.B_Mask, "B_Mask"),
        (pcbnew.Edge_Cuts, "Edge_Cuts"),
    ]

    print(f"Exporting Gerber files to {outputDir}...")
    # Set and plot all layers
    for layer, layerName in gerbLayers:
        print(f"Processing {layerName}...")
        plotctrl.SetLayer(layer)
        if plotctrl.OpenPlotfile(layerName, pcbnew.PLOT_FORMAT_GERBER, layerName):
            plotctrl.PlotLayer()
        else:
            print(f"Error: Could not open plot file for {layerName}")

    plotctrl.ClosePlot()
    
    # Export drill files
    drill_writer = pcbnew.EXCELLON_WRITER(board)
    drill_writer.SetOptions(
        aMirror=False, aMinimalHeader=False, aOffset=pcbnew.VECTOR2I(0, 0), aMerge_PTH_NPTH=False)
    drill_writer.SetRouteModeForOvalHoles(aUseRouteModeForOvalHoles=False)
    drill_writer.SetFormat(True, pcbnew.EXCELLON_WRITER.DECIMAL_FORMAT)
    drill_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_GERBER)

    print("Exporting drill files...")
    drill_writer.CreateDrillandMapFilesSet(outputDir, True, False)

    # Verify files were written
    gerber_files = os.listdir(outputDir)
    if gerber_files:
        print(f"Gerber export completed. Files generated: {gerber_files}")
    else:
        print(f"Error: No files generated in {outputDir}")
