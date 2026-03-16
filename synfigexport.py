#!/usr/bin/env python3
#coding: utf-8

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
#FIXME
#       2015-2018 - d-j-a-y
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
#   2016-02-25  switch group option
#   2018-10-23  GIMP 2.10 compliant!
#FIXME

#TODO switch layer has option, fix accordlngly the canvas version
#TODO gimp group layer compliant
#TODO fix color indexed files
#TODO gif animation layer notation support
#TODO synfig animation duration option
#TODO zipped file sif extension not sifz

#REGRESSION
# the double argument in ui is trunc at 0.01 precision but we need more precisition for image span value


#########################################################################
# GIMP python fu TIPS
#######################
# Python-Fu samples : http://registry.gimp.org/node/28124
#
# 1) On error :
#     "Removing duplicate PDB procedure 'my-python-fu' registered
#      by '/home/xxxxx/.gimp-2.8/plug-ins/pythonfu.py' " FIXME
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
import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

import os, string
import tempfile, zipfile
# unicodedata used by valid_file_name
import unicodedata

from synfigfu import *

NESTED_STACK_END = object()

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
# from http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
def valid_filename(filename):
    # ~ cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def export_synfig(procedure, image, doinvisible, applymask, dozoom, dorot, dotrans):
    # ~ gimp.message("WARNING : You are running a development version.\nStable version can be catch from https://github.com/d-j-a-y/Gimp2Synfig master branch.")
    echo("mas:",applymask, " rot:",dorot)

    if not pdb.gimp_image_is_valid(image):
        gimp.message(_("The image file is not valid !?"))
        return

    if not img.filename:
        gimp.message(_("The original image haven't been saved. Save the image and retry."))
        return

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def export_run(procedure, run_mode, image, file, options, metadata, config, data):
    def write_file_str(zfile, fname, data):
        # work around a permission bug in the zipfile library:
        # http://bugs.python.org/issue3394
        zi = zipfile.ZipInfo(fname)
        zi.external_attr = int("100644", 8) << 16
        zfile.writestr(zi, data)

    #TODO check is image exist, check file saved once?
    # ~ if not pdb.gimp_image_is_valid(image):
        # ~ gimp.message(_("The image file is not valid !?"))
        # ~ return

    # ~ if not img.filename:
        # ~ gimp.message(_("The original image haven't been saved. Save the image and retry."))
        # ~ return

    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("file-synfig-export")

        # ~ dialog = GimpUi.ProcedureDialog.new(procedure, config, _("Synfig Studio Export..."))
        dialog = GimpUi.ProcedureDialog.new(procedure, config, "Synfig Studio Export...")
        dialog.fill(None)

        # ~ if not dialog.run():
            # ~ return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                               # ~ GLib.Error())
        is_ok_pressed = dialog.run()
        if not is_ok_pressed:
            dialog.destroy()
            return proc.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
    else: #fixme not interactive #TODO add console mode ?
       return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                           GLib.Error())

    do_invisible_layers    = config.get_property("do-invisible")
    do_switch_group    = config.get_property("do-switchgroup")
    do_mask_layers    = config.get_property("do-mask")
    do_zoom_layers = config.get_property("do-zoom")
    do_rotate_layers = config.get_property("do-rotate")
    do_translate_layers = config.get_property("do-translate")

    Gimp.progress_init("Exporting SynfigStudio image")

    Gimp.message("Hello world!")
    echo("inv:",do_invisible_layers, " rot:",do_rotate_layers)

    sifzfile = zipfile.ZipFile(file.peek_path(), 'w', compression=zipfile.ZIP_STORED)
    tempdir = tempfile.mkdtemp('gimp-plugin-file-synfig')

    span = 9.1788
    imgw = image.get_width()
    imgh = image.get_height()
    pixelsize = 1/(imgw**2 + imgh**2)**0.5*span
    img_name = os.path.split(image.get_name())[1]

    mysynfig = SynfigObject()

    stack = """<layer type="stack"/>""" #FIXME

    sif_header = mysynfig.document_begin %{ \
     "width":imgw, \
     "height":imgh, \
     "xres":image.get_resolution().xresolution*39.37007904, \
     "yres":image.get_resolution().yresolution*39.37007904, \
     "xres":90, \
     "yres":90, \
     "x":round(imgw*pixelsize/2, 5), \
     "y":round(imgh*pixelsize/2, 5), \
     "name": img_name \
    }
    sif_file_data = sif_header

    total_layers = len(image.get_layers())
    echo("total layers : ",total_layers)

    # applying layer masks
    if do_mask_layers:
        echo("applymask")
        # ~ img = img.duplicate()
        # ~ for l in img.layers:
            # ~ if not l.visible and not doinvisible:
                # ~ continue # don't process invisible
            # ~ if pdb.gimp_layer_get_mask(l):
                # ~ pdb.gimp_layer_remove_mask(l, 0)

    if do_switch_group:
        sif_file_data += mysynfig.layer_switch_begin % {\
                      "name":img_name \
                      }

    def store_synfig_layer(image, drawable, path):
        tmp = os.path.join(tempdir, 'tmp.png')
        interlace, compression = 0, 2

        width, height = drawable.get_width(), drawable.get_height()
        tmp_img = Gimp.Image.new(width, height, image.get_base_type())
        tmp_layer = Gimp.Layer.new_from_drawable (drawable, tmp_img)
        tmp_img.insert_layer (tmp_layer, None, 0)

        pdb_proc   = Gimp.get_pdb().lookup_procedure('file-png-export')
        pdb_config = pdb_proc.create_config()
        pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
        pdb_config.set_property('image', tmp_img)
        pdb_config.set_property('file', Gio.File.new_for_path(tmp))
        pdb_config.set_property('options', None)
        pdb_config.set_property('interlaced', interlace)
        pdb_config.set_property('compression', compression)
        # write all PNG chunks except oFFs(ets)
        pdb_config.set_property('bkgd', True)
        pdb_config.set_property('offs', False)
        pdb_config.set_property('phys', True)
        pdb_config.set_property('time', True)
        pdb_config.set_property('save-transparent', True)
        pdb_proc.run(pdb_config)
        if (os.path.exists(tmp)):
            sifzfile.write(tmp, path)
            os.remove(tmp)
        else:
            print("Gimp:File:Export:Synfig: Error removing ", tmp)

        tmp_img.delete()

    def add_synfig_layer(parent, x, y, opac, gimp_layer, path, is_visible):
        echo ("    adding layer ",gimp_layer.get_name())
        active=is_visible

        sifdata = mysynfig.layer_image % {\
         "name":gimp_layer.get_name(), \
         "file":path, \
         "blend_method":SYNFIG_BLEND_COMPOSITE, \
         "amount":1.0, \
         "x":x/2*pixelsize, \
         "y":y/2*pixelsize \
        }

        store_synfig_layer(image, gimp_layer, path)
        return sifdata

    def enumerate_gimp_layers(layers):
        for layer in layers:
            if not layer.is_group():
                yield layer
            else:
                yield layer
                for sublayer in enumerate_gimp_layers(layer.get_children()):
                    yield sublayer
                yield NESTED_STACK_END


    # prepare for layers
    parent_groups = []
    i = 0

    layer_stack = image.get_layers()
    # Number of top level layers for tracking progress
    lay_cnt = len(layer_stack)

    folder_name = "%s_layers"%os.path.splitext(img_name)[0]
    for lay in enumerate_gimp_layers(layer_stack):
        prev_lay = i
        if lay is NESTED_STACK_END:
            if parent_groups:
                parent_groups.pop()
            continue
        _, offset_x, offset_y = lay.get_offsets()
        opac = lay.get_opacity () # / 100.0 # needs to be between 0.0 and 1.0
        echo("offsets : ", offset_x, offset_y, "opacity ", opac)

        # ~ valid_image_name = valid_filename(lay.get_name())
        valid_image_name = (lay.get_name())
        # making file names
        filename = "%s.png"%valid_image_name
        maskname = "%s_mask.png"%valid_image_name

        if not parent_groups:
            path_name = os.path.join(folder_name, filename)
            # ~ path_name = folder_name + '/{:03d}.png'.format(i)
            i += 1
        else:
            path_name = os.path.join(folder_name, filename)
            # ~ path_name = folder_name + '/{}-{:03d}.png'.format(
                # ~ parent_groups[-1][1], parent_groups[-1][2])
            parent_groups[-1][2] += 1

        parent = stack if not parent_groups else parent_groups[-1][0]

        if lay.is_group():
            echo("add group ",parent, opac, lay, path_name, lay.get_name(), lay.get_visible())
            # ~ group = add_group_layer(parent, opac, lay, lay.get_visible())
            # ~ group_path = ("{:03d}".format(i) if not parent_groups else
                # ~ parent_groups[-1][1] + "-{:03d}".format(parent_groups[-1][2]))
            # ~ parent_groups.append([group, group_path , 0])
        else:
            echo("add layer", offset_x, offset_y, opac, lay, path_name, valid_image_name, lay.get_name(), lay.get_visible())
            if lay.get_visible():
                sif_file_data += add_synfig_layer(parent, offset_x, offset_y, opac, lay, path_name, "true")
            elif do_invisible_layers:
                sif_file_data += add_synfig_layer(parent, offset_x, offset_y, opac, lay, path_name, "false")

        if (i > prev_lay):
            Gimp.progress_update(i/lay_cnt)

    # applying layer inv
    if do_invisible_layers:
        echo("apply inv")

    # applying layer zoom
    if do_zoom_layers:
        echo("apply zoom")

    # applying layer rotate
    if do_rotate_layers:
        echo("apply rotate")

    # applying layer translate
    if do_translate_layers:
        echo("apply translate")

    switchactive = "fixme"
    if do_switch_group:
        sif_file_data += mysynfig.layer_switch_end%{"name":switchactive}

    sif_file_name = os.path.splitext(img_name)[0] + '.' + mysynfig.file_ext
    sif_file_data += mysynfig.document_end
    write_file_str(sifzfile, sif_file_name, sif_file_data)

    sifzfile.close()

    Gimp.progress_end()

    return Gimp.ValueArray.new_from_values([
        GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)
    ])

############################################################
# Echo args (for debug usage)
############################################################
def echo(*args):
    """Print the arguments on standard output"""
    print ("synfigexport>", args)

class SynfigExport (Gimp.PlugIn):
    ## GimpPlugIn virtual methods ##
    def do_set_i18n (self, name): #https://discourse.gnome.org/t/gimp-3-how-to-set-up-localisation-for-my-plug-in/27010
        return False

    def do_query_procedures(self):
        return [ 'file-synfig-export' ] #todo check in procedure browser to consistancy

    def do_create_procedure(self, name):
        procedure = None
        if name == 'file-synfig-export':
            procedure = Gimp.ExportProcedure.new(self, name,
                                                 Gimp.PDBProcType.PLUGIN,
                                                 False, export_run, None)

            procedure.set_image_types("RGB*,GRAY*")

            procedure.set_menu_label("Synfig Studio Export")
            procedure.set_extensions ("sifz");

            # In the new API, use File/[Save] for the Save section of the File menu
            # https://gitlab.gnome.org/GNOME/gimp/-/blob/master/NEWS?ref_type=heads#L85
            # ~ procedure.add_menu_path('<Image>/File/[Save]')

            procedure.set_documentation("Export document to synfig's (.sfiz) format",
                                        "Export document to synfig's (.sfiz) format\nBy default, export invisible layers and put each Gimp layer into a Synfig Group layer",
                                        name)
            procedure.set_attribution("AkhIL", "Creative Commons Attribution 3.0\n2008 - dooglus\n2015-2026 - d-j-a-y", "2026-02-XX")

            procedure.add_boolean_argument ("do-switchgroup",   _("Group in a single S_witch Layer"),  _("Group in a single Switch Layer"),
                                            False, GObject.ParamFlags.READWRITE)
            procedure.add_boolean_argument ("do-invisible",   _("Export _invisible layers"),  _("Export invisible layers"),
                                            False, GObject.ParamFlags.READWRITE)
            procedure.add_boolean_argument ("do-mask",   _("Apply _layer masks"),  _("Apply layer masks"),
                                            False, GObject.ParamFlags.READWRITE)
            procedure.add_boolean_argument ("do-zoom",   _("Export _zoom layers"), _("Export zoom layers"),
                                            False, GObject.ParamFlags.READWRITE)
            procedure.add_boolean_argument ("do-rotate",   _("Export r_otate layers"), _("Export rotate layers"),
                                            False, GObject.ParamFlags.READWRITE)
            procedure.add_boolean_argument ("do-translate",   _("Add _translate layers"), _("Export translate layers"),
                                            False, GObject.ParamFlags.READWRITE)
            # ~ the double is trunc at 0.01 precision! here we sneed more precisition !
            # ~ procedure.add_double_argument ("image-span", _("Image _Span"), _("Image Span"),
                                          # ~ 0.001, 15.0, 9.1788, GObject.ParamFlags.READWRITE)

        return procedure

############################################################
# Entry point
############################################################
Gimp.main(SynfigExport.__gtype__, sys.argv)
