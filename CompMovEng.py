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

import pcbnew
import math
import itertools

# Constants for movement range (performance requirements)
MIN_SPACING = pcbnew.FromMM(0.127)  
MAX_SPACING = pcbnew.FromMM(2.0)  
ADJACENCY_THRESHOLD = pcbnew.FromMM(10.0)  

def getDistance(fp1, fp2):
    # Calculate distance between two footprints (only in x-direction).
    pos1, pos2 = fp1.GetPosition(), fp2.GetPosition()
    dx = abs(pos2.x - pos1.x)  # Only consider horizontal distance
    return dx

def moveFootprint(fp1, fp2, move_distance, moved_components):
    # Move two footprints closer together left and right only
    ref1, ref2 = fp1.GetReference(), fp2.GetReference()

    if ref1 in moved_components or ref2 in moved_components:
        return  # Skip if either component has already been moved

    pos1, pos2 = fp1.GetPosition(), fp2.GetPosition()
    dx = pos2.x - pos1.x  # Determine relative position

    if dx > 0:  # fp2 is to the right of fp1
        new_x1 = pos1.x + move_distance / 2
        new_x2 = pos2.x - move_distance / 2
    else:  # fp1 is to the right of fp2
        new_x1 = pos1.x - move_distance / 2
        new_x2 = pos2.x + move_distance / 2

    # Set new positions
    fp1.SetPosition(pcbnew.VECTOR2I(int(new_x1), pos1.y))
    fp2.SetPosition(pcbnew.VECTOR2I(int(new_x2), pos2.y))

    # Mark footprints as moved using their reference designators
    moved_components.add(ref1)
    moved_components.add(ref2)

    # movement details
    print(f"Moved {ref1} and {ref2} closer "
          f"by {pcbnew.ToMM(move_distance):.3f} mm in x-direction.")

def findAdjComp(footprints):
    # Find pairs of footprints that are within the adjacency threshold
    adj_pairs = []
    
    for fp1, fp2 in itertools.combinations(footprints, 2):
        dist = getDistance(fp1, fp2)

        # Only consider components that are horizontally close
        if MIN_SPACING < dist <= ADJACENCY_THRESHOLD and abs(fp1.GetPosition().y - fp2.GetPosition().y) < pcbnew.FromMM(1.0):
            adj_pairs.append((fp1, fp2, dist))

    return adj_pairs

def shiftAdjComp(board, distance_percentage = 0.2):
    # Move adjacent components closer in the x-direction
    footprints = list(board.GetFootprints())
    adjacent_pairs = findAdjComp(footprints)
    moved_components = set()

    for fp1, fp2, distance in adjacent_pairs:
        ref1, ref2 = fp1.GetReference(), fp2.GetReference()

        if ref1 in moved_components or ref2 in moved_components:
            continue  # Skip if already moved

        # Calculate movement as 20% of current distance (may be user input later)
        move_distance = distance * distance_percentage

        # Ensure movement doesn't violate minimum spacing
        if distance - move_distance < MIN_SPACING:
            move_distance = distance - MIN_SPACING

        if move_distance > 0:
            moveFootprint(fp1, fp2, move_distance, moved_components)


