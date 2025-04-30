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
import wx
import pcbnew
import importlib.util
from pcbnew import ActionPlugin
from CompMovEng import shiftAdjComp as default_shiftAdjComp
from LoopIndOptim import WidenTraces as default_WidenTraces
from LoopIndOptim import LoadDesRules as default_LoadDesRules
from GerberExporter import GerberExporter

targetInd = 1e-9
targetPercentage = 0.2
orig = float(0)

# SMART Goal Extensibility Class
class PluginManager:
    def __init__(self, script_folder="scripts"):
        self.script_folder = script_folder
        self.plugins = {}
        self.callbacks = {
            "on_component_shifted": [],
            "on_traces_widened": [],
            "on_rules_loaded": []
        }
        self.load_plugins()
    
    def load_plugins(self):
        if not os.path.exists(self.script_folder):
            os.makedirs(self.script_folder)
        
        for filename in os.listdir(self.script_folder):
            if filename.endswith(".py"):
                plugin_name = filename[:-3]
                plugin_path = os.path.join(self.script_folder, filename)
                
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.plugins[plugin_name] = module
                print(f"Loaded plugin: {plugin_name}")
                
                if hasattr(module, "register_callbacks"):
                    module.register_callbacks(self)
    
    def register_callback(self, event_name, callback):
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)
            print(f"Registered callback for event: {event_name}")
        else:
            print(f"Warning: Event {event_name} is not recognized.")
    
    def trigger_event(self, event_name, *args, **kwargs):
        callbacks = self.callbacks.get(event_name, [])
        if callbacks:
            for cb in callbacks:
                print(f"[Callback] {cb.__name__}")
                cb(*args, **kwargs)
        else:
            print(f"[Default] Running fallback for {event_name}")
            if event_name == "on_component_shifted":
                default_shiftAdjComp(*args, **kwargs)
            elif event_name == "on_traces_widened":
                default_WidenTraces(*args, **kwargs)
            elif event_name == "on_rules_loaded":
                default_LoadDesRules(*args, **kwargs)

class ParameterDialog(wx.Dialog):
    def __init__(self, parent, title, managePlugin):
        super().__init__(parent, title=title, size=(400, 400))
        self.managePlugin = managePlugin
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(panel, label="Target Inductance (<number> e-9):")
        vbox.Add(self.label, flag=wx.LEFT | wx.TOP, border=10)
        self.text_ctrl = wx.TextCtrl(panel)
        vbox.Add(self.text_ctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        self.label2 = wx.StaticText(panel, label="Enter Shift Component Percentage (0.0-1.0):")
        vbox.Add(self.label2, flag=wx.LEFT | wx.TOP, border=10)
        self.text_ctrl2 = wx.TextCtrl(panel)
        vbox.Add(self.text_ctrl2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        self.ok_button = wx.Button(panel, label="OK")
        self.ok_button.Bind(wx.EVT_BUTTON, self.afterOk)
        vbox.Add(self.ok_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.export_button = wx.Button(panel, label="Export as Gerber")
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export_gerber)
        vbox.Add(self.export_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)
    
    def afterOk(self, event):
        value = self.text_ctrl.GetValue()
        value2 = self.text_ctrl2.GetValue()
        try:
            global targetInd
            targetInd = float(value)
            global targetPercentage
            targetPercentage = float(value2)
            self.Close()
        except ValueError:
            wx.MessageBox("Please enter a valid number", "Error", wx.OK | wx.ICON_ERROR)
    
    
    def on_export_gerber(self, event):
        board = pcbnew.GetBoard()
        if not board:
            wx.MessageBox("Error: No board loaded", "Error", wx.OK)
            return
        
        with wx.DirDialog(None, "Select Directory to Save Gerber Files", "", wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            outputDir = dialog.GetPath()
            GerberExporter(board, outputDir)
            gerber_files = os.listdir(outputDir)
        if gerber_files:
            print(f"Gerber files exported successfully: {gerber_files}")
            wx.MessageBox(f"Gerber files exported successfully\nOriginal Inductance: {orig * 1e6} nH/mm", "Success", wx.OK | wx.ICON_INFORMATION)
        else:
            print("Error: No files generated!")
            wx.MessageBox("Error: No Gerber files were generated!", "Error", wx.OK | wx.ICON_ERROR)

class EnhancedPCBPlugin(ActionPlugin):
    def defaults(self):
        self.name = "Enhanced PCB Plugin"
        self.category = "Modify PCB"
        self.description = "Automates component movement and widens traces to reduce loop inductance"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
    
    def Run(self):
        SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

# Ensure the script directory exists
        if not os.path.exists(SCRIPTS_DIR):
            os.makedirs(SCRIPTS_DIR)
        board = pcbnew.GetBoard()
        managePlugin = PluginManager()
        dialog = ParameterDialog(None, "Enter target inductance & component shift percentage", managePlugin)
        dialog.ShowModal()
        global orig
        default_LoadDesRules("design_rules.json")
      # managePlugin.trigger_event("on_rules_loaded", "design_rules.json")
        orig = default_WidenTraces(board, targetInd) # returns original inductance which is displayed after exporting gerber
      # managePlugin.trigger_event("on_traces_widened", board, "design_rules.json", targetInd)
        default_shiftAdjComp(board, targetPercentage)
      # managePlugin.trigger_event("on_component_shifted", board, targetPercentage)
        
        pcbnew.Refresh()

EnhancedPCBPlugin().register()
