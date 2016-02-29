#!/usr/bin/env python
# -*- coding: utf-8 -*-

# <Image>/File/Export
# <Image>/File/Export As
# Open the export dialog box, select SynfigStudio has file type (.sifz)
# and exports gimp document to synfig's canvas and png images.

##
#   Initial Author: IL'dar AKHmetgaleev aka AkhIL
#   e-mail: akhilman at gmail dot com
#   web:    http://akhilman.blogspot.com
#
#   Contributors :
#       2008 - dooglus
#       2015-2016 - d-j-a-y
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
#   2016-02-19  registration into export dialog + localization
#   2016-02-22  synfig stuff to synfigfu module + fix #5 filename forbiden chars
#

#TODO switch layer has option, fix accordlngly the canvas version
#TODO gimp group layer compliant
#TODO fix color indexed files
#TODO gif animation layer notation support
#TODO synfig animation duration option
#TODO zipped file sif extension not sifz

#########################################################################
# GIMP python fu TIPS
#######################
# Python-Fu samples : http://registry.gimp.org/node/28124
#
# 1) On error :
#     "Removing duplicate PDB procedure 'my-python-fu' registered
#      by '/home/xxxxx/.gimp-2.8/plug-ins/pythonfu.py' "
#
# --> Check if not pythonfu.py~ file or any with same 'my-python-fu'
#
# 2) On error :
#     "attempted to install <Save> procedure "my-fu-save" which
#      does not take the standard <Save> Plug-In arguments:
#      (INT32, IMAGE, DRAWABLE, STRING, STRING)."
#
# ---> Check GIMP-Erreur: save handler "file-sifz-save" does not take the standard save handler args
# 3) On error:
#     TypeError: export_synfig() takes exactly 11 arguments (12 given)
# --> Check prototype handler and prototype arg declaration in register
#####################################


############################################################
# Libraries
############################################################

from gimpfu import *
import os
import gzip
import string

from synfigfu import *

# Localization (l10n)
#
# use with _("foo") around all strings, to indicate "translatable"

import gettext
locale_directory = gimp.locale_directory
gettext.install("gimp20-python", locale_directory, unicode=True)

# unicodedata used by valid_file_name
import unicodedata

############################################################
# Main functions & content
############################################################
validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
# valid_filename original name "removeDisallowedFilenameChars" from http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
def valid_filename(filename):
    cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def gimp2synfig_mode_converter(mode):
    """
    converts gimp's layer compositing mode to synfig's blend method
    """
    modes = {
        NORMAL_MODE :       SYNFIG_BLEND_COMPOSITE,
        DISSOLVE_MODE :     SYNFIG_BLEND_COMPOSITE,
        BEHIND_MODE :       SYNFIG_BLEND_BEHIND,
        MULTIPLY_MODE :     SYNFIG_BLEND_MULTIPLY,
        SCREEN_MODE :       SYNFIG_BLEND_SCREEN,
        OVERLAY_MODE :      SYNFIG_BLEND_OVERLAY,
        DIFFERENCE_MODE :   SYNFIG_BLEND_DIFFERENCE,
        ADDITION_MODE :     SYNFIG_BLEND_ADD,
        SUBTRACT_MODE :     SYNFIG_BLEND_SUBTRACT,
        DARKEN_ONLY_MODE :  SYNFIG_BLEND_DARKEN,
        LIGHTEN_ONLY_MODE : SYNFIG_BLEND_BRIGHTEN,
        HUE_MODE :          SYNFIG_BLEND_HUE,
        SATURATION_MODE :   SYNFIG_BLEND_SATURATION,
        COLOR_MODE :        SYNFIG_BLEND_COLOR,
        VALUE_MODE :        SYNFIG_BLEND_LUMINANCE,
        DIVIDE_MODE :       SYNFIG_BLEND_DIVIDE,
        DODGE_MODE :        SYNFIG_BLEND_BRIGHTEN,
        BURN_MODE :         SYNFIG_BLEND_MULTIPLY,
        HARDLIGHT_MODE :    SYNFIG_BLEND_HARD_LIGHT,
        SOFTLIGHT_MODE :    SYNFIG_BLEND_COMPOSITE,
        GRAIN_EXTRACT_MODE: SYNFIG_BLEND_COMPOSITE,
        GRAIN_MERGE_MODE :  SYNFIG_BLEND_COMPOSITE,
        COLOR_ERASE_MODE :  SYNFIG_BLEND_COMPOSITE,
    }
    return modes[mode]

def export_synfig(img, drawable, filename, raw_filename, extra, span, doswitchgroup, doinvisible, applymask, dozoom, dorot, dotrans):
#    gimp.message("WARNING : You are running a development version.\nStable version can be catch from https://github.com/d-j-a-y/Gimp2Synfig master branch.")
    if not pdb.gimp_image_is_valid(img):
        gimp.message(_("The image file is not valid !?"))
        return

    if not img.filename:
        gimp.message(_("The original image haven't been saved. Save the image and retry."))
        return

    # system file name ouput generation
    default_prefix = img.filename.split('.xcf')[0]
    if filename:
        prefix = os.path.splitext(filename)[0]
        suffix = os.path.splitext(filename)[1]
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

    mysynfig = SynfigObject()
    # sif file generation
    pixelsize = 1/(img.width**2 + img.height**2)**0.5*span

    siffile.write(mysynfig.document_begin %{ \
     "width":img.width, \
     "height":img.height, \
     "xres":pdb.gimp_image_get_resolution(img)[0]*39.37007904, \
     "yres":pdb.gimp_image_get_resolution(img)[1]*39.37007904, \
     "x":img.width*pixelsize/2, \
     "y":img.height*pixelsize/2, \
     "name":img.name \
    })


    # applying layer masks
    if applymask:
        img = img.duplicate()
        for l in img.layers:
            if not l.visible and not doinvisible:
                continue # don't process invisible
            if pdb.gimp_layer_get_mask(l):
                pdb.gimp_layer_remove_mask(l, 0)

    totallayers = len(img.layers)
    donelayers = 0

    if doswitchgroup:
        siffile.write(mysynfig.layer_switch_begin % {\
                      "name":img.name \
                      })

    # exporting layers
    for l in reversed(img.layers):
        if not l.visible:
            if not doinvisible:
                continue # don't process invisible
            else:
                active = 'false'
        else:
            active = 'true'

        valid_image_name = valid_filename(l.name)

        if not doswitchgroup:
            siffile.write(mysynfig.layer_inline_begin % {\
             "name":valid_image_name, \
             "amount":l.opacity*0.01, \
             "active":active, \
             "blend_method":gimp2synfig_mode_converter(l.mode), \
             "x":(l.width/2.0+pdb.gimp_drawable_offsets(l)[0]-img.width/2.0)*pixelsize, \
             "y":(l.height/2.0+pdb.gimp_drawable_offsets(l)[1]-img.height/2.0)*pixelsize*-1 \
            })

        # making file names
        filename = "%s.png"%valid_image_name
        maskname = "%s_mask.png"%valid_image_name

        # exporting layer
        newimg = gimp.Image(l.width,l.height,img.base_type)
        pdb.gimp_edit_copy(l)
        newlayer = gimp.Layer(newimg, l.name, l.width, l.height, l.type, 1, NORMAL_MODE)
        pdb.gimp_drawable_fill(newlayer, TRANSPARENT_FILL)
        newimg.add_layer(newlayer)
        pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(newlayer, True))
        pdb.gimp_file_save(newimg, newlayer, os.path.join(layersprefix,filename), filename)
        pdb.gimp_image_delete(newimg)

        siffile.write(mysynfig.layer_image % {\
         "name":filename, \
         "file":os.path.join("%s_layers"%name,filename), \
         "blend_method":SYNFIG_BLEND_COMPOSITE, \
         "amount":1.0, \
         "x":l.width/2*pixelsize, \
         "y":l.height/2*pixelsize \
        })

        if doswitchgroup and donelayers == 0:
            switchactive = filename

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
            siffile.write(mysynfig.layer_image % {\
             "name":maskname, \
             "file":os.path.join("%s_layers"%name,maskname), \
             "blend_method":SYNFIG_BLEND_ALPHA_OVER, \
             "amount":1.0, \
             "x":l.width/2*pixelsize, \
             "y":l.height/2*pixelsize \
            })

        # adding transform layers
        if dozoom:
            siffile.write(mysynfig.layer_zoom%{"name":"%s_scale"%l.name})
        if dorot:
            siffile.write(mysynfig.layer_rotate%{"name":"%s_rot"%l.name})
        if dotrans:
            siffile.write(mysynfig.layer_translate%{"name":"%s_loc"%l.name})

        if not doswitchgroup:
            siffile.write(mysynfig.layer_inline_end)

        donelayers += 1

    if applymask:
        pdb.gimp_image_delete(img)

    if doswitchgroup:
        siffile.write(mysynfig.layer_switch_end%{"name":switchactive})

    siffile.write(mysynfig.document_end)
    siffile.close()

############################################################
# Echo args (for debug usage)
############################################################

def echo(*args):
    """Print the arguments on standard output"""
    print "echo:", args

############################################################
# Register function
############################################################

def register_save_handlers():
    gimp.register_save_handler('file-sifz-save', 'sifz', '')

register(
    'file-sifz-save', # Function name
    _("Export document to synfig's (.sfiz) format"), # Blurb / description
    _("Export document to synfig's (.sfiz) format\nBy default, export invisible layers and put each Gimp layer into a Synfig Group layer"),
    'AkhIL', # Author
    'AkhIL', # Copyright notice
    '2016-02-19-Alpha', # Version date
    "Synfig Studio",
    'RGB*, GRAY*', # Image type
    [   # Input <save> args. Format (type, name, description, default [, extra])
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_STRING, "filename", "The name of the file", None),
        (PF_STRING, "raw-filename", "The name of the file", None),
        (PF_STRING, "extra", "extra args", None),
        # Export SynfigStudio arg
        (PF_FLOAT,  "span",     _("Image Span"),9.1788),
        (PF_BOOL,   "doswitchgroup",   _("Group in a single Switch Layer (synfig >= 1.0)"), False),
        (PF_BOOL,   "doinvisible",   _("Export invisible layers"),True),
        (PF_BOOL,   "applymask",   _("Apply layer masks"),False),
        (PF_BOOL,   "dozoom",   _("Add zoom layers"),False),
        (PF_BOOL,   "dorot",   _("Add rotate layers"),False),
        (PF_BOOL,   "dotrans",   _("Add translate layers"),False)
    ],
    [],
    export_synfig,
    on_query = register_save_handlers,
    menu = '<Save>')

main()
