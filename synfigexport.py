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

# ~ from gimpfu import *

import os
# ~ import gzip
import string
import zipfile

from synfigfu import *

# Localization (l10n)
#
# use with _("foo") around all strings, to indicate "translatable"
# ~ import gettext
# ~ locale_directory = gimp.locale_directory
# ~ gettext.install("gimp20-python", locale_directory, unicode=True)

# unicodedata used by valid_file_name
#import unicodedata

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

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

        dialog = GimpUi.ProcedureDialog.new(procedure, config, _("Synfig Studio Export..."))
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

    invisible_layers    = config.get_property("do-invisible")
    mask_layers    = config.get_property("do-mask")
    zoom_layers = config.get_property("do-zoom")
    rotate_layers = config.get_property("do-rotate")
    translate_layers = config.get_property("do-translate")

    Gimp.progress_init("Exporting SynfigStudio image")

    Gimp.message("Hello world!")
    echo("inv:",invisible_layers, " rot:",rotate_layers)

    sifzfile = zipfile.ZipFile(file.peek_path(), 'w', compression=zipfile.ZIP_STORED)

    span = 9.1788
    imgw = image.get_width()
    imgh = image.get_height()
    pixelsize = 1/(imgw**2 + imgh**2)**0.5*span
    imgname = os.path.split(image.get_name())[1]

    mysynfig = SynfigObject()

    sif_header = mysynfig.document_begin %{ \
     "width":imgw, \
     "height":imgh, \
     "xres":image.get_resolution().xresolution*39.37007904, \
     "yres":image.get_resolution().yresolution*39.37007904, \
     "xres":90, \
     "yres":90, \
     "x":round(imgw*pixelsize/2, 5), \
     "y":round(imgh*pixelsize/2, 5), \
     "name": imgname \
    }

    sif_file_name = os.path.splitext(imgname)[0] + '.' + mysynfig.file_ext
    sif_file_data = sif_header + mysynfig.document_end
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
