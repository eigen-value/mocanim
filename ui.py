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
    bl_label = "Metarig to BVH"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'
    
    def draw(self, context):
        layout = self.layout
        scn=context.scene
        
        row = layout.row(align = True)
        row.operator('mocanim.create_metarig',text = 'Create Mocanim Metarig', icon = 'POSE_DATA')
        row = layout.row(align=True)
        row.operator('mocanim.export_metarig',text='Export Metarig to BVH', icon = 'EXPORT')
        row = layout.row(align=True)
        row.prop(scn, "MocanimExportPath")
        #row.operator('mocanim.export_path', text='', icon = 'FILESEL')

class VIEW3D_PT_bind_animation(bpy.types.Panel):
    bl_label = "Create Constraints"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_options = {'DEFAULT_CLOSED'}
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

        #layout.label('Advanced Options')
        layout.prop(scn, "MocanimAdvOptions")
        layout.separator()
        if scn.MocanimAdvOptions:
            layout.prop(scn, "MocanimConstrainRoot")
            layout.prop(scn, "MocanimConstrainSpine")
            if scn.MocanimConstrainSpine:
                row = layout.row(align = True)
                row.prop(scn, "MocanimConstrainHips")
                row.prop(scn, "MocanimFollowThigh")
                layout.prop(scn, "MocanimConstrainTorso")
                layout.prop(scn, "MocanimConstrainChest")
            layout.prop(scn, "MocanimConstrainArms")
            layout.prop(scn, "MocanimConstrainLegs")
            layout.prop(scn, 'MocanimUseLimits')

class VIEW3D_PT_constraint_limits(bpy.types.Panel):
    bl_label = "Constraint Limits"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'Mocanim'

    @classmethod
    def poll(cls,context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):

        scn = context.scene
        rig = bpy.data.objects[scn.MocanimTrgRig]
        #pbones = [pb for pb in rig.pose.bones if pb.bone.select == True]
        pbones = rig.pose.bones
        layout = self.layout

        if rig.mode == 'POSE':

            for pb in pbones:
                for cns in pb.constraints:
                    if ('Limit' in cns.name) and ('-mcn' in cns.name):
                        box = layout.box()
                        row = box.row(align = True)
                        row.label(pb.name + ': ' + cns.name)
                        #row.prop(cns, 'mute')
                        if cns.mute:
                            row.prop(cns, 'mute', icon = 'VISIBLE_IPO_OFF',emboss= False, icon_only=True)
                        else:
                            row.prop(cns, 'mute', icon = 'VISIBLE_IPO_ON',emboss=False, icon_only=True)

                        if 'Rotation' in cns.name:
                            row = box.row(align = False)
                            col = row.column(align = True)
                            col.prop(cns, 'use_limit_x')
                            col.prop(cns, 'min_x', text='Min')
                            col.prop(cns, 'max_x', text='Max')
                            col = row.column(align = True)
                            col.prop(cns, 'use_limit_y')
                            col.prop(cns, 'min_y',text='Min')
                            col.prop(cns, 'max_y', text='Max')
                            col = row.column(align = True)
                            col.prop(cns, 'use_limit_z')
                            col.prop(cns, 'min_z',text='Min')
                            col.prop(cns, 'max_z', text='Max')
                        elif 'Location' in cns.name:
                            col = box.column(align = True)
                            col.prop(cns, 'use_min_z')
                            col.prop(cns, 'min_z',text='')
                            col.prop(cns, 'use_transform_limit')
                        row = box.row(align = False)
                        row.separator()

class VIEW3D_PT_keyframing(bpy.types.Panel):
    bl_label = "Keyframing"
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
        #row.prop(scn, "MocanimForceInsert")
        #row = layout.row(align=True)
        row.prop(scn, "MocanimKeepConstraints")
        row = layout.row(align=True)
        row.operator("mocanim.keep_pose", icon = 'KEY_HLT')
        row.operator("mocanim.clear_pose", icon = 'KEY_DEHLT')
        row = layout.row(align=True)
        row.operator("mocanim.keep_action", icon = 'ACTION_TWEAK')
        row.operator("mocanim.clear_action", icon= 'CANCEL')
        row = layout.row(align=True)
        row.prop(scn,"MocanimStartFrame")
        row.prop(scn,"MocanimEndFrame")
        row.operator("mocanim.get_frame_range", icon='TIME', text='')
        row = layout.row(align=True)
        row.prop(scn,"MocanimFrameStep")
        row = layout.row(align=True)
        row.prop(scn,"MocanimNewAction")

class VIEW3D_PT_transfer_animation(bpy.types.Panel):
    bl_label = "Transfer Animation"
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
        row.prop(scn, "MocanimTransferOnlySelected")
        row = layout.row(align=True)
        row.operator("mocanim.ik2fk", text='IK2FK Pose', icon = 'SNAP_ON')
        row.operator("mocanim.fk2ik", text='FK2IK Pose', icon = 'SNAP_ON')
        row = layout.row(align=True)
        row.operator("mocanim.transfer_fk_to_ik", text='IK2FK Action', icon = 'ACTION_TWEAK')
        row.operator("mocanim.transfer_ik_to_fk", text='FK2IK Action', icon = 'ACTION_TWEAK')
        row = layout.row(align=True)
        row.operator("mocanim.clear_animation", text="Clear IK Action", icon = 'CANCEL').type = "IK"
        row.operator("mocanim.clear_animation", text="Clear FK Action", icon = 'CANCEL').type = "FK"
        row = layout.row(align=True)
        row.prop(scn, 'MocanimTransferStartFrame')
        row.prop(scn, 'MocanimTransferEndFrame')
        row.operator("mocanim.get_transfer_frame_range", icon='TIME', text='')
        # if not scn.MocanimTransferOnlySelected:
        #     row = layout.row(align=True)
        #     row.prop(scn, "MocanimFkIkArms")
        #     row.prop(scn, "MocanimFkIkLegs")

class VIEW3D_PT_fk_ik(bpy.types.Panel):
    bl_label = "FK/IK"
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

def register():

    bpy.utils.register_class(VIEW3D_PT_meta_bvh)
    bpy.utils.register_class(VIEW3D_PT_bind_animation)
    bpy.utils.register_class(VIEW3D_PT_constraint_limits)
    bpy.utils.register_class(VIEW3D_PT_keyframing)
    bpy.utils.register_class(VIEW3D_PT_transfer_animation)
    bpy.utils.register_class(VIEW3D_PT_fk_ik)
    
def unregister():

    bpy.utils.unregister_class(VIEW3D_PT_meta_bvh)
    bpy.utils.unregister_class(VIEW3D_PT_bind_animation)
    bpy.utils.unregister_class(VIEW3D_PT_constraint_limits)
    bpy.utils.unregister_class(VIEW3D_PT_keyframing)
    bpy.utils.unregister_class(VIEW3D_PT_transfer_animation)
    bpy.utils.unregister_class(VIEW3D_PT_fk_ik)

