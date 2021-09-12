# Contributing to FastenerWB

Table of Contents:

- [Contributing to FastenerWB](#contributing-to-fastenerwb)
- [Adding new fasteners](#adding-new-fasteners)
  - [Creating data files](#creating-data-files)
    - [Converting data to a csv file](#converting-data-to-a-csv-file)
    - [Required files and their purpose](#required-files-and-their-purpose)
  - [writing code to generate the fastener](#writing-code-to-generate-the-fastener)
    - [adding functionality to screw_maker](#adding-functionality-to-screw_maker)
    - [Additional changes](#additional-changes)
    - [Reusing existing code](#reusing-existing-code)
  - [Making icons](#making-icons)
  - [Appendix A - useful resources](#appendix-a---useful-resources)
  - [Appendix B - fasteners to add](#appendix-b---fasteners-to-add)

# Adding new fasteners

This is  a step-by-step guide to adding a new type of screw to FastenersWorkbench.

## Creating data files

The workbench pulls data from `.csv` files, stored in the `FsData` directory.
Let's Implement a new type of fastener - a carriage bolt:

![](Resources/FSexampletable.png)

### Converting data to a csv file

The advantage of using the plain text `.csv` format is that there are lots of
tools that work well with these files e.g.:

- [LibreOffice Calc]() or an equivalent spreadsheet editor.
- [GImageReader](https://github.com/manisandro/gImageReader) - for reading text from pdf files
- A text editor with [multi-cursor support](https://code.visualstudio.com/docs/editor/codebasics#_multiple-selections-multicursor)


### Required files and their purpose

We actually need three separate csv files:

- `FsData/{fastenertype}def.csv` - specifies the dimensions of the head of the fastener.
- `FsData/{fastenertype}length.csv` - specifies the discrete fastener lengths that are available for this type of fastener.
- `FsData/{fastenertype}range.csv` - for each available fastener diameter, this file provides the upper and lower bound (inclusive) of lengths that are available.

An example of how this data scheme works in practice:

The first 2 lines of `FsData/iso7379def.csv` are:

``` csv
"Dia","P","d1","d3","l2","l3","SW"
"M3",0.5,4,7,7,3,2
```

Note that the first line is a header (it is skipped when `screw_maker.py` reads
the file) and string values are double quoted.

For each subsequent line:
- The first column is the diameter that the line corresponds to
- The remaining columns are dimensions needed to generate the object 

`FsData/{fastenertype}length.csv` stores a list of standard lengths that apply
to a particular fastener. These files have a 3 column structure: The first
column is the nominal length, and the second and third columns are the minimum
and maximum actual lengths permissible when a fastener of that length is
manufactured. 

E.G.: `iso7379length.csv`

``` csv
"Nominal","Min","Max"
"4",3.76,4.24
"5",4.76,5.24
"6",5.76,6.24
"8",7.71,8.29
"10",9.71,10.29
```

The files `iso888length.csv` and `inch_fs_length.csv` provide generalized
length tables that you can use if they work well with the fastener you want 
to implement.

Finally, the `FsData/{fastenertype}range.csv` file determines which lengths defined
in a fasteners' corresponding length file are available for each diameter.
For example, in `iso7379range.csv`, we have:

``` csv
"Dia","Min_L","Max_L"
"M3","4","30"
"M4","5","40"
"M5","10","80"
"M6","16","100"
```

Note that all values are strings, since they correspond to string values
in the `def` and `length` files.

## writing code to generate the fastener

### adding functionality to screw_maker

Open `screw_maker.py` in your preferred text editor.
We will be extending the `Screw` class to generate a new fastener.

``` python
  def makeCarriageBolt(self, SType = 'ASMEB18.5.2', Threadtype = '1/4in', l = 25.4) :
    d = self.getDia(Threadtype, False)
    if SType == 'ASMEB18.5.2':
      tpi,_,A,H,O,P,_,_ = FsData["asmeb18.5.2def"][Threadtype]
      A,H,O,P = (25.4*x for x in (A,H,O,P))
      pitch = 25.4/tpi
      if l <= 152.4:
        L_t = d*2+6.35
      else:
        L_t = d*2+12.7
    # lay out points for head generation
    p1 = Base.Vector(0,0,H)
    head_r = A/math.sqrt(2)
    p2 = Base.Vector(head_r*math.sin(math.pi/8),0,H-head_r+head_r*math.cos(math.pi/8))
    p3 = Base.Vector(A/2,0,0)
    p4 = Base.Vector(math.sqrt(2)/2*O,0,0)
    p5 = Base.Vector(math.sqrt(2)/2*O,0,-1*P+(math.sqrt(2)/2*O-d/2))
    p6 = Base.Vector(d/2,0,-1*P)
    # arcs must be converted to shapes in order to be merged with other line segments 
    a1 = Part.Arc(p1,p2,p3).toShape()
    l2 = Part.makeLine(p3,p4)
    l3 = Part.makeLine(p4,p5)
    l4 = Part.makeLine(p5,p6)
    wire1 = Part.Wire([a1,l2,l3,l4])
    head_shell = wire1.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    if not self.rThread:
      # simplified threaded section
      p7 = Base.Vector(d/2,0,-1*l+d/10)
      p8 = Base.Vector(d/2-d/10,0,-1*l)
      p9 = Base.Vector(0,0,-1*l)
      l5 = Part.makeLine(p6,p7)
      l6 = Part.makeLine(p7,p8)
      l7 = Part.makeLine(p8,p9)
      thread_profile_wire = Part.Wire([l5,l6,l7])
      shell_thread = thread_profile_wire.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
    else:
      # modeled threaded section
      # calculate the number of thread half turns
      if l <= L_t:  # fully threaded fastener
        residue, turns = math.modf((l-P)/pitch)
        halfturns = 2*int(turns)
        if residue > 0.5:
          halfturns = halfturns+1
        shell_thread = self.makeShellthread(d,pitch,halfturns,False,0)
        shell_thread.translate(Base.Vector(0,0,-2*pitch-P))
      else:  # partially threaded fastener
        residue, turns = math.modf((L_t-P)/pitch)
        halfturns = 2*int(turns)
        if residue > 0.5:
          halfturns = halfturns+1
        shell_thread = self.makeShellthread(d,pitch,halfturns,False,0)
        shell_thread.translate(Base.Vector(0,0,-2*pitch-P-(l-L_t)))
        p7 = Base.Vector(d/2,0,-1*P-(l-L_t))
        helper_wire = Part.Wire([Part.makeLine(p6,p7)])
        shank = helper_wire.revolve(Base.Vector(0,0,0),Base.Vector(0,0,1),360)
        shell_thread = Part.Shell(shell_thread.Faces+shank.Faces)
    p_shell = Part.Shell(head_shell.Faces+shell_thread.Faces)
    p_solid = Part.Solid(p_shell)
    # cut 4 flats under the head
    for i in range(4):
      p_solid = p_solid.cut(Part.makeBox(d,A,P,Base.Vector(d/2,-1*A/2,-1*P)).rotate(Base.Vector(0,0,0),Base.Vector(0,0,1),i*90))
    # removeSplitter is equivalent to the 'Refine' option for FreeCAD PartDesign objects
    return p_solid.removeSplitter()
```

FreeCAD's `Part` Module works somewhat like a clunkier version of OpenCAD.
We lay out points and build them up into 3D shells, then merge them together
to return a solid object. The call to `makeShellthread` returns a modelled 
thread as a shell. Remember that `Part.Show(object)` will show `object` in 
the current FreeCAD document. This function gives us an equivalent to print
debugging. 

We also need a few additional lines to make the rest of the class aware 
of our additions to it. It should look something like this:

```python
  def check_Data(self, ST_text, ND_text, NL_text):
    ...
    if ST_text[:-1] == 'ASMEB18.5.5':
      table = FsData["asmeb18.5.2def"]
      tab_len = FsData["inch_fs_length"]
      tab_range = FsData["asmeb18.5.2range"]
      Type_text = 'Screw'
    ...
  def createScrew(self, ST_text, ND_text, NL_text, threadType, shapeOnly = False):
    ...
        if ST_text == 'ASMEB18.5.2':
           table = FsData["asmeb18.5.2def"]
    ...
```

You can review the code added to `screw_maker.py` for this example
[HERE](add_link_when_merged).

### Additional changes

`ScrewMaker.py` needs an entry added to the `screwTables` variable to match our added fastener

``` python
screwTables = {
  ...
  'ASMEB18.5.2': ("Screw", FsData["asmeb18.5.2def"], FsData["inch_fs_length"], FsData["asmeb18.5.2range"], -1, 0),
  ...
}
```

Check out the corresponding commit [HERE](add_link_when_merged).

- `FastenersCmd.py` needs a line to initialize a new toolbar command for the workbench. 

``` python
FSAddScrewCommand("ASMEB18.5.2", "ASME B18.5 UNC Round head square neck bolts", "Other head")
```

Check out the corresponding commit [HERE](add_link_when_merged).

### Reusing existing code

The `screw_maker.Screw` class generally has one method to create a 
particular type of fastener. That code can then be reused to create 
multiple similar parts. See the following snippet :

``` python
  # also used for ISO 7046 countersunk flat head screws with H cross recess
  # also used for ISO 7047 raised countersunk head screws with H cross recess
  # also used for ISO 10642 Hexagon socket countersunk head screws
  # also used for ISO 14582 Hexalobular socket countersunk head screws, high head
  # also used for ISO 14584 Hexalobular socket raised countersunk head screws
  def makeIso7046(self, SType ='ISO7046', ThreadType ='M6',l=25.0):
    ...
```

If you choose to reuse an existing method, you must determine which dimensions
it uses to generate a shape. This can usually be accomplished by looking 
at standards tables for parts the method already implements, or measuring
existing fasteners in FreeCAD.

## Making icons

Dust off your graphic design skills.

The easiest way to create an icon for your new fastener type is as follows:
- Create a TechDraw view of the fastener from a close-to-isometric view angle
- export the page and import it into Inkscape
- You can now recolor the view of the part to look like the workbenches icons
- Icons should be 48x48px plain svg files

![](Resources/FSIconProcess.png)

## Appendix A - useful resources

Some websites that provide free-to-view data on standard fasteners:

- [https://www.fasteners.eu/](https://www.fasteners.eu/)
- [https://torqbolt.com/](https://torqbolt.com/)
- [https://www.mcmaster.com/](https://www.mcmaster.com/)

## Appendix B - fasteners to add

[ISO standards related to fasteners](https://www.iso.org/ics/21.060/x/)

ASME standards related to fasteners:

|Item | Standard |
|-----|----------|
| Small Solid Rivets | B18.1.1-1972(R2006) |
| Large Rivets | B18.1.2-1972(R2006) |
| Metric Small Solid Rivets | B18.1.3M-1983(R2006) |
| Square and Hex Bolts and Screws (Inch Series) | B18.2.1-1996(R2005) |
| Square and Hex Nuts (Inch Series) | B18.2.2-1987(R2005) |
| Metric Hex Cap Screws | B18.2.3.1M-1999(R2005) |
| Metric Formed Hex Screws | B18.2.3.2M-2005 |
| Metric Heavy Hex Screws | B18.2.3.3M-1979(R2001) |
| Metric Hex Flange Screws | B18.2.3.4M-2001(R2006) |
| Metric Hex Bolts | B18.2.3.5M-1979(R2006) |
| Metric Heavy Hex Bolts | B18.2.3.6M-1979(R2006) |
| Metric Heavy Hex Structural Bolts | B18.2.3.7M-1979(R2006) |
| Metric Hex Lag Screws | B18.2.3.8M-1981(R2005) |
| Metric Heavy Hex Flange Screws | B18.2.3.9M-2001(R2006) |
| Square Head Bolts (Metric Series) | B18.2.3.10M-1996(R2003) |
| Metric Hex Nuts,Style1 | B18.2.4.1M-2002(R2007) |
| Metric Hex Nuts,Style2 | B18.2.4.2M-2005 |
| Metric Slotted Hex Nuts | B18.2.4.3M-1979(R2006) |
| Metric Hex Flange Nuts | B18.2.4.4M-1982(R2005) |
| Metric Hex Jam Nuts | B18.2.4.5M-1979(R2003) |
| Metric Heavy Hex Nuts | B18.2.4.6M-1979(R2003) |
| Fasteners for Use in Structural Applications | B18.2.6-2006 |
| Metric12-Spline Flange Screws | B18.2.7.1M-2002(R2007) |
| Clearance Holes for Bolt,Screws,and Studs | B18.2.8-1999(R2005) |
| Straightness Gage and Gaging for Bolts and Screws | B18.2.9-2007 |
| Socket Cap,Shoulder,and Set Screws,Hex and Spline Keys (Inch Series) | B18.3-2003(R2008) |
| Socket Head Cap Screws (Metric Series) | B18.3.1M-1986(R2008) |
| Metric Series Hexagon Keys and Bits | B18.3.2M-1979(R2008) |
| Hexagon Socket Head Shoulder Screws (Metric Series) | B18.3.3M-1986(R2008) |
| Hexagon Socket Button Head Cap Screws (Metric Series) | B18.3.4M-1986(R2008) |
| Hexagon Socket Flat Countersunk Head Cap Screws (Metric Series) | B18.3.5M-1986(R2008) |
| Metric Series Socket Set Screws | B18.3.6M-1986(R2008) |
| Round Head Bolts (Inch Series) | B18.5-1990(R2003) |
| Metric Round Head Short Square Neck Bolts | B18.5.2.1M-2006 |
| Metric Round Head Square Neck Bolts | B18.5.2.2M-1982(R2005) |
| Round Head Square Neck Bolts With Large Head (Metric Series) | B18.5.2.3M-1990(R2003) |
| Wood Screws (Inch Series) | B18.6.1-1981(R2008) |
| Slotted Head Cap Screws,Square Head Set Screws,and Slotted Headless Set Screws (Inch Series) | B18.6.2-1998(R2005) |
| Machine Screws and Machine Screw Nuts | B18.6.3-2003(R2008) |
| Thread Forming and Thread Cutting Tapping Screws and Metallic Drive Screws (Inch Series) | B18.6.4-1998(R2005) |
| Metric Thread-Forming and Thread-Cutting Tapping Screws | B18.6.5M-2000(R2005) |
| Metric Machine Screws | B18.6.7M-1999(R2005) |
| General Purpose Semi-Tubular Rivets,Full Tubular Rivets,Split Rivets and Rivet Caps | B18.7-2007 |
| Metric General Purpose Semi-Tubular Rivets | B18.7.1M-2007 |
| Clevis Pins and Cotter Pins (Inch Series) | B18.8.1-1994(R2000) |
| Taper Pins,Dowel Pins,Straight Pins,Grooved Pins,and Spring Pins (Inch Series) | B18.8.2-2000 |
| Spring Pins:Coiled Type,Spring Pins:Slotted,Machine Dowel Pins:Hardened Ground,and Grooved Pins (Metric Series) | B18.8.100M-2000(R2005) |
| Cotter Pins,Headless Clevis Pins,and Headed Clevis Pins (Metric Series) | B18.8.200M-2000(R2005) |
| Plow Bolts | B18.9-2007 |
| Track Bolts and Nuts | B18.10-1982(R2005) |
| Miniature Screws | B18.11-1961(R2005) |
| Glossary of Terms for Mechanical Fasteners | B18.12-2001(R2006) |
| Screw and Washer Assemblies—Sems (Inch Series) | B18.13-1996(R2003) |
| Screw and Washer Assemblies:Sems (Metric Series) | B18.13.1M-1998(R2003) |
| Forged Eyebolts | B18.15-1985(R2003) |
| Metric Lifting Eyes | B18.15M-1998(R2004) |
| Prevailing-Torque Type Steel Metric Hex Nuts and Hex Flange Nuts | B18.16M-2004 |
| Serrated Hex Flange Locknuts90,000psi (Inch Series) | B18.16.4-2008 |
| Nylon Insert Locknuts (Inch Series) | B18.16.6-2008 |
| Inspection and Quality Assurance for General Purpose Fasteners | B18.18.1-2007 |
| Inspection and Quality Assurance for High-Volume Machine Assembly Fasteners | B18.18.2M-1987(R2005) |
| Inspection and Quality Assurance for Special Purpose Fasteners | B18.18.3M-1987(R2005) |
| Inspection and Quality Assurance for Fasteners for Highly Specialized Engineered Applications | B18.18.4M-1987(R2005) |
| Inspection and Quality Assurance Plan Requiring In-Process Inspection and Controls | B18.18.5M-1998(R2003) |
| Quality Assurance Plan for Fasteners Produced in a Third Party Accreditation System | B18.18.6M-1998(R2003) |
| Quality Assurance Plan for Fasteners Produced in a Customer Approved Control Plan | B18.18.7M-1998(R2003) |
| Lock Washers (Inch Series) | B18.21.1-1999(R2005) |
| Lock Washers (Metric Series) | B18.21.2M-1999(R2005) |
| Double Coil Helical Spring Lock Washers for Wood Structures | B18.21.3-2008 |
| Metric Plain Washers | B18.22M-1981(R2005) |
| Plain Washers | B18.22.1-1965(R2003) |
| Part Identifying Number (PIN)Code System for B18Fastener Products | B18.24-2004 |
| Square and Rectangular Keys and Keyways | B18.25.1M-1996(R2003) |
| Woodruff Keys and Keyways | B18.25.2M-1996(R2003) |
| Square and Rectangular Keys and Keyways:Width Tolerances and |
| Deviations Greater Than Basic Size | B18.25.3M-1998(R2003) |
| Tapered and Reduced Cross Section Retaining Rings (Inch Series) | B18.27-1998(R2005) |
| Helical Coil Screw Thread Inserts—Free Running and Screw Locking (Inch Series) | B18.29.1-1993(R2007) |
| Helical Coil Screw Thread Inserts:Free Running and Screw Locking (Metric Series) | B18.29.2M-2005 |
| Open-End Blind Rivets With Break Mandrels (Metric Series) | B18.30.1M-2000(R2005) |
| Metric Continuous and Double-End Studs | B18.31.1M-2008 |
