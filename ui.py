#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================


import bpy
from .bind_animation import *
from .keyframing import *
from .fkik import *
from _sqlite3 import Row

class VIEW3D_PT_meta_bvh(bpy.types.Panel):
    bl_label = "Mocanim: Metarig to BVH"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'
    
    def draw(self, context):
        layout = self.layout
        scn=context.scene
        
        row = layout.row(align = True)
        row.operator('mocanim.create_metarig',text = 'Create Mocanim Metarig', icon = 'POSE_DATA')

class VIEW3D_PT_bind_animation(bpy.types.Panel):
    bl_label = "Mocanim: Create Constraints"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'
    
    def draw(self,context):
        layout = self.layout
        scn=context.scene
        
        col = layout.column(align = True)
        col.label(text = "Performer Rig:")
        row = layout.row(align = True)
        row.prop(scn, 'MocanimSrcRig', text = '', icon = 'ARMATURE_DATA')
        row.operator('mocanim.select_source', text = '', icon = 'CURSOR')
         
        col = layout.column(align = True)
        col.label(text = "Character Rig:")
        row = layout.row(align = True)
        row.prop(scn, 'MocanimTrgRig', text = '', icon = 'ARMATURE_DATA')
        row.operator('mocanim.select_target', text = '', icon = 'CURSOR')
        
                
        col = layout.column(align=True)
        col.separator()
        
        layout.label('Constraints:')
        row = layout.row(align = True)
        row.operator('mocanim.create_constraints', text = 'Create/Update', icon = 'SNAP_ON')
        row.operator('mocanim.delete_constraints', text = 'Delete', icon = 'SNAP_OFF')

        row = layout.row(align = True)
        row.operator('mocanim.enable_constraints', text = 'Enable all', icon = 'RESTRICT_VIEW_OFF')
        row.operator('mocanim.disable_constraints', text = 'Disable all', icon = 'RESTRICT_VIEW_ON')

        layout.label('Advanced Options')
        layout.prop(scn, "MocanimConstrainRoot")
        layout.prop(scn, "MocanimConstrainSpine")
        layout.prop(scn, "MocanimConstrainArms")
        layout.prop(scn, "MocanimConstrainLegs")

class VIEW3D_PT_keyframing(bpy.types.Panel):
    bl_label = "Mocanim: Keyframing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'
    
    @classmethod
    def poll(cls,context):
        if context.object and context.object.type == 'ARMATURE':
            return True
    
    def draw(self,context):
        layout = self.layout
        scn = context.scene
        
        row = layout.row(align=True)
        row.prop(scn, "MocanimOnlySelected")
        row.prop(scn, "MocanimForceInsert")
        row = layout.row(align=True)
        row.prop(scn, "MocanimKeepConstraints")
        row = layout.row(align=True)
        row.operator("mocanim.keep_pose", icon = 'KEY_HLT')
        row = layout.row(align=True)
        row.operator("mocanim.keep_action", icon = 'ACTION_TWEAK')
        row = layout.row(align=True)
        row.prop(scn,"MocanimStartFrame")
        row.prop(scn,"MocanimEndFrame")
        row = layout.row(align=True)
        row.prop(scn,"MocanimFrameStep")
        row = layout.row(align=True)
        row.prop(scn,"MocanimNewAction")
        
class VIEW3D_PT_fk_ik(bpy.types.Panel):
    bl_label = "Mocanim: FK/IK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'
    
    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True
        
    def draw(self,context):
        layout = self.layout
        scn = context.scene
        
        rig = context.object
        #CHECK IF rig is Pitchipoy
        
        layout.label('Use IK')
        row = layout.row(align=True)
        row.prop(scn, "MocanimArmsIk")
        row = layout.row(align=True)
        row.prop(scn, "MocanimLegsIk")
        row = layout.row(align=True)
        row.operator("mocanim.limb_switch", icon = "FILE_REFRESH")
        layout.label('Transfer Animation')
        row = layout.row(align=True)
        row.prop(scn, "MocanimFkIkArms")
        row.prop(scn, "MocanimFkIkLegs")
        row = layout.row(align=True)
        row.operator("mocanim.transfer_fk_to_ik")
        row = layout.row(align=True)
        row.operator("mocanim.transfer_ik_to_fk")
        row = layout.row(align=True)
        row.operator("mocanim.clear_animation", text="Clear IK Animation").type = "IK"
        row = layout.row(align=True)
        row.operator("mocanim.clear_animation", text="Clear FK Animation").type = "FK"
        

def register():
    bpy.utils.register_class(VIEW3D_PT_meta_bvh)
    bpy.utils.register_class(VIEW3D_PT_bind_animation)
    bpy.utils.register_class(VIEW3D_PT_keyframing)
    bpy.utils.register_class(VIEW3D_PT_fk_ik)


    
def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_meta_bvh)
    bpy.utils.unregister_class(VIEW3D_PT_bind_animation)
    bpy.utils.unregister_class(VIEW3D_PT_keyframing)
    bpy.utils.unregister_class(VIEW3D_PT_fk_ik)

