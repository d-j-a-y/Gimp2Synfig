# synfigexport.py

Fork of [synfigexport.py](https://sites.google.com/site/akhilman/synfigexport.py)

[GIMP](https://www.gimp.org) to [Synfig](https://www.synfig.org) file export plugin.

Export a GIMP multi-layered image to a corresponding Synfig, an awesome 2D animation software, project.

## Installation

* 0- Locate the GIMP __plugins directory__ from \<Edit\> / Preferences: Folders → Plugins.
* 1- Extract/Copy/Move/... __synfigexport.py__ and __synfigfu.py__ files to the GIMP plugins directory.
* 2- (re)Load GIMP to __refresh__ the Plugins system
* 3- Do your stuff and export as synfig studio format and __enjoy__ your project in synfig studio format :D

For up to date and complete infos, please refer to the official Gimp's plugins installation (this plugin is part of the "Python-Fu" family) : [GIMP 2.10 - scripting -](https://docs.gimp.org/2.10/en/gimp-scripting.html) or [GIMP 2.8 - scripting -](https://docs.gimp.org/2.8/en/gimp-scripting.html) or ...

NOTA : __synfigfu.py__ must be present in __PYTHONPATH__ (or at least in same folder than synfigexport.py)


## Usage
```
<Image>/File/Export/
```

Open the Export (or "Export As") dialog box, select "Synfig Studio" has file type (.sifz),
choose a destination folder and a name, and exports gimp document to synfig's canvas and png images.

See also [Gimp2Synfig](http://wiki.synfig.org/Doc:Gimp2synfig) from Synfig documentation.

## Know Issue

### "can't pickle Grouplayer objects!!!"
In fact, this is a [GIMP issue](https://gitlab.gnome.org/GNOME/gimp/issues/1119).
To work around, you must select any layer than a layer group before exporting.


## Author
IL'dar AKHmetgaleev aka AkhIL - [blog akhil](http://blog.akhil.ru/)

### Contribution
* dooglus
* [d.j.a.y](https://github.com/d-j-a-y/Gimp2Synfig)


## Licence
This program is licensed under [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/)

__Distribution and updating of the code is appreciated.__

## History
* 2008-01-31  first public release
* 2008-04-26  gimp-2.2 compatibility fix by dooglus
* 2008-08-18  now works without alpha channel
* 2015-11-25  this fork
* 2015-12-03  fix empty name error + add choose file dialog
* 2016-02-19  registration into export dialog + localization mechanism
* 2016-02-22  synfig stuff to synfigfu module + fix issue #5 filename forbiden chars
* 2016-02-25  switch group option
* 2018-10-23  GIMP 2.10 compliant!
