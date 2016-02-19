#!/usr/bin/python

# <Image>/File/Export/Synfig
# exports gimp document to synfig's canvas and png images
# if output is omited then script saves image to same dir
# with source image

##
#   Author: IL'dar AKHmetgaleev aka AkhIL
#   e-mail: akhilman at gmail dot com
#   web:    http://akhilman.blogspot.com
#
#   This code is licensed under
#   Creative Commons Attribution 3.0 Unported License
#   http://creativecommons.org/licenses/by/3.0/
##

#
# History:
#   2008-01-31  first public release
#   2008-04-26  gimp-2.2 compatibility fix by dooglus
#   2008-08-18  now works without alpha channel
#   2015-11-25  this fork (https://github.com/d-j-a-y/Gimp2Synfig)
#   2015-12-03  fix empty name error + add choose file dialog
#

#TODO switch layer has option, fix accordlngly the canvas version

from gimpfu import *
import os
import gzip

documentbegin = """\
<canvas version="0.3" width="%(width)i" height="%(height)i" xres="%(xres)f" yres="%(yres)f" view-box="-%(x)f %(y)f %(x)f -%(y)f" >
  <name>%(name)s</name>
"""
documentend = """\
</canvas>
"""
inlinebegin = """\
  <layer type="PasteCanvas" active="%(active)s" version="0.1" desc="%(name)s">
    <param name="z_depth">
      <real value="0.0000000000"/>
    </param>
    <param name="amount">
      <real value="%(amount)f"/>
    </param>
    <param name="blend_method">
      <integer value="%(blend_method)i"/>
    </param>
    <param name="origin">
      <vector>
        <x>%(x)f</x>
        <y>%(y)f</y>
      </vector>
    </param>
    <param name="canvas">
      <canvas xres="10.000000" yres="10.000000">
"""
inlineend = """\
      </canvas>
    </param>
  </layer>
"""
imagelayer = """\
        <layer type="import" active="true" version="0.1" desc="%(name)s">
          <param name="z_depth">
            <real value="0.0000000000"/>
          </param>
          <param name="amount">
            <real value="%(amount)f"/>
          </param>
          <param name="blend_method">
            <integer value="%(blend_method)i"/>
          </param>
          <param name="tl">
            <vector>
              <x>-%(x)f</x>
              <y>%(y)f</y>
            </vector>
          </param>
          <param name="br">
            <vector>
              <x>%(x)f</x>
              <y>-%(y)f</y>
            </vector>
          </param>
          <param name="filename">
            <string>%(file)s</string>
          </param>
        </layer>
"""
zoomlayer = """
        <layer type="zoom" active="true" version="0.1" desc="%(name)s">
          <param name="amount">
            <real value="0.0000000000"/>
          </param>
          <param name="center">
            <vector>
              <x>0.0000000000</x>
              <y>0.0000000000</y>
            </vector>
          </param>
        </layer>
"""
rotatelayer = """
        <layer type="rotate" active="true" version="0.1" desc="%(name)s">
          <param name="origin">
            <vector>
              <x>0.0000000000</x>
              <y>0.0000000000</y>
            </vector>
          </param>
          <param name="amount">
            <angle value="0.000000"/>
          </param>
        </layer>
"""
translatelayer = """
        <layer type="translate" active="true" version="0.1" desc="%(name)s">
          <param name="origin">
            <vector>
              <x>0.0000000000</x>
              <y>0.0000000000</y>
            </vector>
          </param>
        </layer>
"""

switchlayerbegin = """
        <layer type="switch" active="%(active)s" exclude_from_rendering="false" version="0.0" desc="%(name)s">
         <param name="z_depth">
           <real value="0.0000000000"/>
         </param>
         <param name="amount">
          <real value="%(amount)f"/>
         </param>
         <param name="blend_method">
          <integer value="0" static="true"/>
         </param>
         <param name="origin">
          <vector>
            <x>0.0000000000</x>
            <y>0.0000000000</y>
          </vector>
         </param>
         <param name="transformation">
          <composite type="transformation">
           <offset>
            <vector>
              <x>0.0000000000</x>
              <y>0.0000000000</y>
            </vector>
           </offset>
           <angle>
            <angle value="0.000000"/>
           </angle>
        <skew_angle>
          <angle value="0.000000"/>
        </skew_angle>
        <scale>
          <vector>
            <x>1.0000000000</x>
            <y>1.0000000000</y>
          </vector>
        </scale>
        </composite>
       </param>
       <param name="canvas">
        <canvas>
"""

switchlayerend = """
      </canvas>
    </param>
    <param name="time_dilation">
      <real value="1.0000000000"/>
    </param>
    <param name="time_offset">
      <time value="0s"/>
    </param>
    <param name="children_lock">
      <bool value="true" static="true"/>
    </param>
    <param name="outline_grow">
      <real value="0.0000000000"/>
    </param>
    <param name="layer_name">
      <string>%(name)s</string>
    </param>
  </layer>
"""

# from synfig-core/src/synfig/color.h
BLEND_COMPOSITE=0
BLEND_STRAIGHT=1
BLEND_ONTO=13
BLEND_STRAIGHT_ONTO=21
BLEND_BEHIND=12
BLEND_SCREEN=16
BLEND_OVERLAY=20
BLEND_HARD_LIGHT=17
BLEND_MULTIPLY=6
BLEND_DIVIDE=7
BLEND_ADD=4
BLEND_SUBTRACT=5
BLEND_DIFFERENCE=18
BLEND_BRIGHTEN=2
BLEND_DARKEN=3
BLEND_COLOR=8
BLEND_HUE=9
BLEND_SATURATION=10
BLEND_LUMINANCE=11
BLEND_ALPHA_BRIGHTEN=14
BLEND_ALPHA_DARKEN=15
BLEND_ALPHA_OVER=19

def gimp2synfig_mode_converter(mode):
    """
    converts gimp's layer compositning mode to synfig's blend method
    """
    modes = {
        NORMAL_MODE :       BLEND_COMPOSITE,
        DISSOLVE_MODE :     BLEND_COMPOSITE,
        BEHIND_MODE :       BLEND_BEHIND,
        MULTIPLY_MODE :     BLEND_MULTIPLY,
        SCREEN_MODE :       BLEND_SCREEN,
        OVERLAY_MODE :      BLEND_OVERLAY,
        DIFFERENCE_MODE :   BLEND_DIFFERENCE,
        ADDITION_MODE :     BLEND_ADD,
        SUBTRACT_MODE :     BLEND_SUBTRACT,
        DARKEN_ONLY_MODE :  BLEND_DARKEN,
        LIGHTEN_ONLY_MODE : BLEND_BRIGHTEN,
        HUE_MODE :          BLEND_HUE,
        SATURATION_MODE :   BLEND_SATURATION,
        COLOR_MODE :        BLEND_COLOR,
        VALUE_MODE :        BLEND_LUMINANCE,
        DIVIDE_MODE :       BLEND_DIVIDE,
        DODGE_MODE :        BLEND_BRIGHTEN,
        BURN_MODE :         BLEND_MULTIPLY,
        HARDLIGHT_MODE :    BLEND_HARD_LIGHT,
        SOFTLIGHT_MODE :    BLEND_COMPOSITE,
        GRAIN_EXTRACT_MODE: BLEND_COMPOSITE,
        GRAIN_MERGE_MODE :  BLEND_COMPOSITE,
        COLOR_ERASE_MODE :  BLEND_COMPOSITE,
    }
    return modes[mode]

def python_fu_exportsynfig(img, layer, output, span, doswitchgroup, doinvisible, applymask, dozoom, dorot, dotrans):
    default_prefix = img.filename.split('.xcf')[0]
    if output:
        prefix = os.path.splitext(output)[0]
        suffix = os.path.splitext(output)[1]
        suffix = "sifz"
    else:
        prefix = default_prefix
        suffix = "sifz"
    name = os.path.basename(prefix)
    if not len(name):
        name = os.path.basename(default_prefix)

    prefix = os.path.dirname(prefix)
    layersprefix = os.path.join(prefix,"%s_layers"%name)

    if not os.path.isdir(layersprefix):
        os.makedirs(layersprefix) # make path for layers

    siffile = gzip.open("%s.%s"%(os.path.join(prefix,name), suffix),"w")
    pixelsize = 1/(img.width**2 + img.height**2)**0.5*span


    siffile.write(documentbegin %{ \
     "width":img.width, \
     "height":img.height, \
     "xres":pdb.gimp_image_get_resolution(img)[0]*39.37007904, \
     "yres":pdb.gimp_image_get_resolution(img)[1]*39.37007904, \
     "x":img.width*pixelsize/2, \
     "y":img.height*pixelsize/2, \
     "name":img.name \
    })


    # aplying layer masks
    if applymask:
        img = img.duplicate()
        for l in img.layers:
            if not l.visible and not doinvisible:
                continue # don't process invisible
            if pdb.gimp_layer_get_mask(l):
                pdb.gimp_layer_remove_mask(l, 0)

    # exporting layers
    totallayers = len(img.layers)
    donelayers = 0
    for l in reversed(img.layers):
        if not l.visible:
            if not doinvisible:
                continue # don't process invisible
            else:
                active = 'false'
        else:
            active = 'true'

        siffile.write(inlinebegin % {\
         "name":l.name, \
         "amount":l.opacity*0.01, \
         "active":active, \
         "blend_method":gimp2synfig_mode_converter(l.mode), \
         "x":(l.width/2.0+pdb.gimp_drawable_offsets(l)[0]-img.width/2.0)*pixelsize, \
         "y":(l.height/2.0+pdb.gimp_drawable_offsets(l)[1]-img.height/2.0)*pixelsize*-1 \
        })

        # maknig file names
        filename = "%s.png" % ( \
            l.name.replace(" ","_").replace('#',"_",) \
        )
        maskname = "%s_mask.png" % ( \
            l.name.replace(" ","_").replace("#","_") \
        )

        # exporting layer
        newimg = gimp.Image(l.width,l.height,img.base_type)
        pdb.gimp_edit_copy(l)
        newlayer = gimp.Layer(newimg, l.name, l.width, l.height, l.type, 1, NORMAL_MODE)
        pdb.gimp_drawable_fill(newlayer, TRANSPARENT_FILL)
        newimg.add_layer(newlayer)
        pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(newlayer, True))
        pdb.gimp_file_save(newimg, newlayer, os.path.join(layersprefix,filename), filename)
        pdb.gimp_image_delete(newimg)

        siffile.write(imagelayer % {\
         "name":filename, \
         "file":os.path.join("%s_layers"%name,filename), \
         "blend_method":BLEND_COMPOSITE, \
         "amount":1.0, \
         "x":l.width/2*pixelsize, \
         "y":l.height/2*pixelsize \
        })

        # exporting layer mask
        if pdb.gimp_layer_get_mask(l):
            newimg = gimp.Image(l.width,l.height,GRAY)
            pdb.gimp_edit_copy(pdb.gimp_layer_get_mask(l))
            newlayer = gimp.Layer(newimg, l.name, l.width, l.height, GRAYA_IMAGE)
            pdb.gimp_drawable_fill(newlayer, TRANSPARENT_FILL)
            newimg.add_layer(newlayer)
            pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(newlayer, True))
            pdb.gimp_invert(newlayer)
            mask = pdb.gimp_layer_create_mask(newlayer,ADD_COPY_MASK)
            pdb.gimp_image_add_layer_mask(newimg,newlayer,mask)
            pdb.gimp_layer_remove_mask(newlayer, 0)
            pdb.gimp_file_save(newimg, newlayer, os.path.join(layersprefix,maskname), filename)
            pdb.gimp_image_delete(newimg)
            siffile.write(imagelayer % {\
             "name":maskname, \
             "file":os.path.join("%s_layers"%name,maskname), \
             "blend_method":BLEND_ALPHA_OVER, \
             "amount":1.0, \
             "x":l.width/2*pixelsize, \
             "y":l.height/2*pixelsize \
            })

        # adding transform layers
        if dozoom:
            siffile.write(zoomlayer%{"name":"%s_scale"%l.name})
        if dorot:
            siffile.write(rotatelayer%{"name":"%s_rot"%l.name})
        if dotrans:
            siffile.write(translatelayer%{"name":"%s_loc"%l.name})

        siffile.write(inlineend)
        donelayers += 1

    if applymask:
        pdb.gimp_image_delete(img)

    siffile.write(documentend)
    siffile.close()


register(
    "python_fu_exportsynfig",
    "Export document to synfig's format",
    "Export document to synfig's format\nBy default saves to same dir as source image",
    "AkhIL",
    "AkhIL",
    "2015-12-03",
    "<Image>/File/Export/Export to S_ynfig",
    "RGB*, GRAY*",
    [
        (PF_FILE, "output",   "output path (optional)", ""),
        (PF_FLOAT,  "span",     "Image Span",9.1788),
        (PF_BOOL,   "doswitchgroup",   "Group in a single Switch Layer (synfig >= 1.0) ",True),
        (PF_BOOL,   "doinvisible",   "Export invisible layers",True),
        (PF_BOOL,   "applymask",   "Apply layer masks",False),
        (PF_BOOL,   "dozoom",   "Add zoom layers",False),
        (PF_BOOL,   "dorot",   "Add rotate layers",False),
        (PF_BOOL,   "dotrans",   "Add translate layers",False)
    ],
    [],
    python_fu_exportsynfig)

main()
