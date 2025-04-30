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
import json
import math


 

def LoadDesRules(json_filename):
    # Get the absolute path to the plugin directory
    plugin_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the folder containing this script
    json_path = os.path.join(plugin_dir, json_filename)  # Construct absolute path

    # Load the JSON file
    with open(json_path, 'r') as f:
        design_rules = json.load(f)

    return design_rules

# Mutual inductance calculation, from article
def inductanceCalc(w, h, mu_0=4 * math.pi * 1e-7):
    
    
    term1 = math.log(((2 * h) / (w)) + 0.5)
    
    return ((mu_0) / (2 * math.pi)) * term1  

# Get distance between traces
def GetTraceDistance(track1, track2):
    start1, end1 = track1.GetStart(), track1.GetEnd()
    start2, end2 = track2.GetStart(), track2.GetEnd()
    
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
    
    return max(min(distance(start1, start2),
                   distance(start1, end2),
                   distance(end1, start2),
                   distance(end1, end2)), 1e-6)  


    

# Adjust trace width iteratively
def WidenTraces(board, target_inductance =  300e-9):
    max_width = pcbnew.FromMM(2)  # Limit
    tracks = list(board.GetTracks())
    
    for track in tracks:
        if isinstance(track, pcbnew.PCB_TRACK):
            wit = track.GetWidth()
            width = pcbnew.ToMM(wit)
            widthCalc = width * 1e-3
            orig = inductanceCalc(widthCalc, 1.51e-3)
            for other_track in tracks:
                if track != other_track:
                    distance = GetTraceDistance(track, other_track)
                    inductance = inductanceCalc(widthCalc, 1.51e-3) # Hardcoded height, can change to user config
                    print(f"Inductance: {inductance}, Width: {pcbnew.ToMM(width)} mm, Distance: {pcbnew.ToMM(distance)} mm")
                    
                    while inductance > target_inductance:
                        width += pcbnew.FromMM(0.01)
                        track.SetWidth(int(width))
                        widthCalc = pcbnew.ToMM(width) * 1e-3
                        inductance = inductanceCalc(widthCalc, 1.51e-3)
                        print(f"Updated Width: {pcbnew.ToMM(width)} mm, New Inductance: {inductance}")
                        
                        if int(width) >= max_width:
                            break
    
    pcbnew.Refresh()
    
    return orig


    



