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

#from gimpfu import *

import os
import gzip
import string

#from synfigfu import *

# Localization (l10n)
#
# use with _("foo") around all strings, to indicate "translatable"
# ~ import gettext
# ~ locale_directory = gimp.locale_directory
# ~ gettext.install("gimp20-python", locale_directory, unicode=True)

# unicodedata used by valid_file_name
#import unicodedata
def export_synfig(procedure, run_mode, image, file, options, metadata, config, data):
    # ~ def write_file_str(zfile, fname, data):
        # ~ # work around a permission bug in the zipfile library:
        # ~ # http://bugs.python.org/issue3394
        # ~ zi = zipfile.ZipInfo(fname)
        # ~ zi.external_attr = int("100644", 8) << 16
        # ~ zfile.writestr(zi, data)

    Gimp.progress_init("Exporting SynfigStudio image")
    Gimp.message("Hello world!")

    # do what you want to do, then, in case of success, return:
    # ~ return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    Gimp.progress_end()

    return Gimp.ValueArray.new_from_values([
        GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)
    ])


class SynfigExport (Gimp.PlugIn):
    ## GimpPlugIn virtual methods ##
    def do_set_i18n (self, name): #https://discourse.gnome.org/t/gimp-3-how-to-set-up-localisation-for-my-plug-in/27010
        return False
        
    def do_query_procedures(self):
        return [ 'file-synfig-export' ]

    def do_create_procedure(self, name):
        procedure = None
        if name == 'file-synfig-export':
            procedure = Gimp.ExportProcedure.new(self, name,
                                                 Gimp.PDBProcType.PLUGIN,
                                                 False, export_synfig, None)

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

        return procedure

# ~ def register_save_handlers():
    # ~ gimp.register_save_handler('file-sifz-save', 'sifz', '')

# ~ register(
    # ~ 'file-sifz-save', # Function name
    # ~ _("Export document to synfig's (.sfiz) format"), # Blurb / description
    # ~ _("Export document to synfig's (.sfiz) format\nBy default, export invisible layers and put each Gimp layer into a Synfig Group layer"),
    # ~ 'AkhIL', # Author
    # ~ ("Creative Commons Attribution 3.0\n2008 - dooglus\n2015-2018 - d-j-a-y"), # Copyright notice
    # ~ '2018-10-23', # Version date
    # ~ "Synfig Studio Export",
    # ~ 'RGB*, GRAY*', # Image type
    # ~ [   # Input <save> args. Format (type, name, description, default [, extra])
        # ~ (PF_IMAGE, "image", "Input image", None),
        # ~ (PF_DRAWABLE, "drawable", "Input drawable", None),
        # ~ (PF_STRING, "filename", "The name of the file", None),
        # ~ (PF_STRING, "raw-filename", "The name of the file", None),
        # ~ (PF_STRING, "extra", "extra args", None),
        # ~ # Export SynfigStudio arg
        # ~ (PF_FLOAT,  "span",     _("Image Span"),9.1788),
        # ~ (PF_BOOL,   "doswitchgroup",   _("Group in a single Switch Layer (synfig >= 1.0)"), False),
        # ~ (PF_BOOL,   "doinvisible",   _("Export invisible layers"),True),
        # ~ (PF_BOOL,   "applymask",   _("Apply layer masks"),False),
        # ~ (PF_BOOL,   "dozoom",   _("Add zoom layers"),False),
        # ~ (PF_BOOL,   "dorot",   _("Add rotate layers"),False),
        # ~ (PF_BOOL,   "dotrans",   _("Add translate layers"),False)
    # ~ ],
    # ~ [],
    # ~ export_synfig,
    # ~ on_query = register_save_handlers,
    # ~ menu = '<Save>')

############################################################
# Entry point
############################################################
Gimp.main(SynfigExport.__gtype__, sys.argv)
