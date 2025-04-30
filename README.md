# Loop-Inductance-Minimizer-KiCad-Plug-In

This KiCad 8 Plugin moves adjacent components closer together and widens traces to reduce loop inductance. Made for ECE Capstone II at the University of Missouri.

To add this plugin, go to the KiCad directory in file system -> 8.0 -> scripting

Include all project files in the scripting directory.

Go to KiCad application -> PCB Editor -> Tools -> External Plugins -> Refresh Plugins

Click on plugin icon (right next to scripting icon), enter target inductance and component shift percentage.

Original inductance will be displayed once gerber files are generated and exported.

This plugin is licensed under the GNU General Public License v3.0 (GPL-3.0).
You are free to:
•	Use this plugin for any purpose
•	Modify it to suit your needs
•	Share it with others
•	Distribute modified versions
Under these conditions:
•	You must keep this license when distributing the code
•	If you distribute a modified version, you must also share the source code
•	This plugin is provided without any warranty
For full license terms, see the LICENSE file or visit https://www.gnu.org/licenses/gpl-3.0.html
