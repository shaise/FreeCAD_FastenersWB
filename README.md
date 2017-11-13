# FreeCAD Fasteners Workbench
A FreeCAD workbench to add/attach various fasteners to parts  

![Fasteners_toolbar](https://user-images.githubusercontent.com/4140247/32561138-815cc5f8-c479-11e7-988e-3be19d3e98c3.png)
![image](https://user-images.githubusercontent.com/4140247/32561849-4276249a-c47b-11e7-9977-110be802d624.png)
![image](https://user-images.githubusercontent.com/4140247/32561853-466e708e-c47b-11e7-9029-923256e50650.png)![image](https://user-images.githubusercontent.com/4140247/32561890-5a563096-c47b-11e7-9026-cf81bea25834.png)![image](https://user-images.githubusercontent.com/4140247/32562381-82b2e8d0-c47c-11e7-828d-1e1b361c6f12.png)



### Installation
Starting from FreeCAD v0.17.9940 an Addons Installer has been built-in to FreeCAD and can be accessed from the Tools menu. 
You can use said Addon Installer to seamlessly install Fasteners Workbench.
Versions before FreeCAD require manual installation, please see how via http://theseger.com/projects/2015/06/fasteners-workbench-for-freecad/


### Usage
Please see http://theseger.com/projects/2015/06/fasteners-workbench-for-freecad/ for a synopsis on how to use Fasteners Workbench.

### Note for FreeCAD 0.17 Part Design:
To attach a fastener to a feature created with part design, it must be attached to the body, rather then one of its inner elements. To do so, first switch the "Display Mode" of the body from "Through" to "Tip". This can be found in the "View" tab of the Body's properties panel. To continue editing the Body, switch back to "Through" 

#### Release notes
* V0.2.14  19 Jun 2017:  Fix countersunk function bug. Merge Maurice's fix for screw generation
* V0.2.13  01 Oct 2015:  Add generation of BOM
* V0.2.11  24 Aug 2015:  Add inner/outer match attribute to screws. Fix several bugs
* V0.2.10  23 Aug 2015:  Add new command: Batch change fasteners parameters
* V0.2.09  23 Aug 2015:  Fixed screw creation bug when not attached to geometry
* V0.2.08  06 Aug 2015:  Add threaded rod item. Fix loading issue 
* V0.2.07  05 Aug 2015:  Add option to select auto crew diameter matching method: 
                         by inner or outer thread diameter
* V0.2.06  02 Aug 2015:  Added hole diameter calculator helper.
* V0.2.05  01 Aug 2015:  Option to select type of screw for countersunk holes.
* V0.2.03  30 Jul 2015:  Separate option for grouping icons as toolbars or as drop-down buttons   
* V0.2.01  28 Jul 2015:  Update to Ulrich's V2.0 screw maker. many more screws, and nuts with threads!   
* V0.1.04  21 Jul 2015:  Drop-down buttons can be enabled in Preferences unser Fasteners.   
* V0.1.03  15 Jul 2015:  Disable drop-down buttons. It will be used only when screw items count will be too big.   
* V0.1.02  14 Jul 2015:  Group screws in drop-down buttons (works for FreeCAD 0.16 and up)  
* V0.1.01  13 Jul 2015:  Add a command to make recessed holes for countersunk screws.  
* V0.0.10  29 Jun 2015:  Add PEM Metric Studs.  
* V0.0.09  28 Jun 2015:  Selecting a face will put a fastener in all holes in that face.  
                         Caching of fasteners speed up generation of same shape ones
* V0.0.08  27 Jun 2015:  Edge selection over multiple objects when generating fasteners now works.
* V0.0.07  26 Jun 2015:  Add PEM Standoffs
* V0.0.06  25 Jun 2015:  Show only applicable M values and lengths, add descriptive name
* V0.0.05  24 Jun 2015:  Add simplify object function, Change icon colors
* V0.0.04  23 Jun 2015:  Add ISO 4032 Metric Hex Nut
* V0.0.03  21 Jun 2015:  Add PEM Metric Press-Nut (Self clinching nut)
* V0.0.02  18 Jun 2015:  Save/Load issue fixed
* V0.0.01  18 Jun 2015:  Initial version

 
#### Developers
* ScrewMaker: Ulrich Brammer <ulrich1a[at]users.sourceforge.net> [@ulrich1a](https://github.com/ulrich1a)
* Workbench wrapper:  Shai Seger [@shaise](https://github.com/shaise)

### Feedback
For further discussion, feel free to open a forum thread on [FreeCAD Open Discussion subforum](https://forum.freecadweb.org/viewforum.php?f=8&sid=853eff68d2a09bfd39fb3508d038af97) 
and make sure to ping user 'shaise'.   
