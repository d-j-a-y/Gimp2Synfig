# synfigfu.py
# -*- coding: utf-8 -*-
# (draft) Synfig Studio python script module

############################################################
# Synfig Studio blend definition
############################################################
# from synfig-core/src/synfig/color.h
SYNFIG_BLEND_COMPOSITE=0
SYNFIG_BLEND_STRAIGHT=1
SYNFIG_BLEND_ONTO=13
SYNFIG_BLEND_STRAIGHT_ONTO=21
SYNFIG_BLEND_BEHIND=12
SYNFIG_BLEND_SCREEN=16
SYNFIG_BLEND_OVERLAY=20
SYNFIG_BLEND_HARD_LIGHT=17
SYNFIG_BLEND_MULTIPLY=6
SYNFIG_BLEND_DIVIDE=7
SYNFIG_BLEND_ADD=4
SYNFIG_BLEND_SUBTRACT=5
SYNFIG_BLEND_DIFFERENCE=18
SYNFIG_BLEND_BRIGHTEN=2
SYNFIG_BLEND_DARKEN=3
SYNFIG_BLEND_COLOR=8
SYNFIG_BLEND_HUE=9
SYNFIG_BLEND_SATURATION=10
SYNFIG_BLEND_LUMINANCE=11
SYNFIG_BLEND_ALPHA_BRIGHTEN=14
SYNFIG_BLEND_ALPHA_DARKEN=15
SYNFIG_BLEND_ALPHA_OVER=19


class SynfigObject:
	def __init__(self):
	############################################################
	# Synfig Studio layer xml templates
	############################################################
		self.document_begin = """
<canvas version="0.3" width="%(width)i" height="%(height)i" xres="%(xres)f" yres="%(yres)f" view-box="-%(x)f %(y)f %(x)f -%(y)f" >
        <name>%(name)s</name>
    """
		self.document_end = """\
</canvas>
"""
		self.layer_inline_begin = """\
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
		self.layer_inline_end = """\
	  </canvas>
	</param>
  </layer>
"""
		self.layer_image = """\
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
		self.layer_zoom = """
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
		self.layer_rotate = """
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
		self.layer_translate = """
		<layer type="translate" active="true" version="0.1" desc="%(name)s">
		  <param name="origin">
			<vector>
			  <x>0.0000000000</x>
			  <y>0.0000000000</y>
			</vector>
		  </param>
		</layer>
"""
		self.layer_switch_begin = """
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
		self.layer_switch_end = """
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
		self.name = 'synfig object'
		self.version = '0.0 - draft'

# Make usable as a script as well as an importable module
if __name__ == "__main__":
	import sys
	synfigfumainscript = SynfigObject()
	print ('synfigfu !\n*do nothing API*\n(draft proof of concept mode used by synfigexport.py Gimp to Synfig plugins)\n\n' + synfigfumainscript.name + ' (version : ' + synfigfumainscript.version + ')')
#	synfigfu(int(sys.argv[1]))
