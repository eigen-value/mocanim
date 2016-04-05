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

# <pep8 compliant>

import bpy

def getKeyedFrames(rig):
    frames=[]
    if rig.animation_data:
        if rig.animation_data.action:
            fcus = rig.animation_data.action.fcurves
            for fc in fcus:
                for kp in fc.keyframe_points:
                    if kp.co[0] not in frames:
                        frames.append(kp.co[0])

    frames.sort()

    return frames

def insertKeyFrame(pb):
    pb.keyframe_insert('location')
    if pb.rotation_mode == 'QUATERNION':
        pb.keyframe_insert('rotation_quaternion')
    else:
        pb.keyframe_insert('rotation_euler')

class OBJECT_OT_KeepPose(bpy.types.Operator):
    """Insert a keyframe for current pose"""
    bl_idname = "mocanim.keep_pose"
    bl_label = "Keep Pose"

    def execute(self,context):
        scn = context.scene

        rig = bpy.data.objects[scn.MocanimTrgRig]

#         bpy.ops.object.mode_set(mode = 'POSE')
#         pbones = rig.pose.bones
#
#         bpy.ops.pose.select_all(action='SELECT')
#         bpy.ops.pose.visual_transform_apply()

        if scn.MocanimForceInsert:
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')

        bpy.ops.nla.bake(frame_start=scn.frame_current, frame_end=scn.frame_current, step=1, only_selected=scn.MocanimOnlySelected, visual_keying=True, clear_constraints=not scn.MocanimKeepConstraints, clear_parents=False, use_current_action= not scn.MocanimNewAction, bake_types={'POSE'})


#         for pb in pbones:
#             insertKeyFrame(pb)

        return {'FINISHED'}

class OBJECT_OT_KeepAction(bpy.types.Operator):
    """Transfer bvh action to target rig    """
    bl_idname = "mocanim.keep_action"
    bl_label = "Keep Action"

    def execute(self,context):

        scn = context.scene


        bpy.ops.nla.bake(frame_start=scn.MocanimStartFrame, frame_end=scn.MocanimEndFrame, step=scn.MocanimFrameStep, only_selected=scn.MocanimOnlySelected, visual_keying=True, clear_constraints=not scn.MocanimKeepConstraints, clear_parents=False, use_current_action= not scn.MocanimNewAction, bake_types={'POSE'})

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_KeepPose)
    bpy.utils.register_class(OBJECT_OT_KeepAction)

    bpy.types.Scene.MocanimOnlySelected = bpy.props.BoolProperty(name="Only Selected", description="Keep Pose on selected bones only", default=True)
    bpy.types.Scene.MocanimStartFrame = bpy.props.IntProperty(name="Start Frame", description="First Frame to Bake", default=0, min= 0)
    bpy.types.Scene.MocanimEndFrame = bpy.props.IntProperty(name="End Frame", description="Last Frame to Bake", default=0, min= 0)
    bpy.types.Scene.MocanimFrameStep = bpy.props.IntProperty(name="Frame Step", description="Bake Frame Step", default=1, min= 1)
    bpy.types.Scene.MocanimNewAction = bpy.props.BoolProperty(name="Create New Action", description="Bake bvh mocap into new Action", default=False)
    bpy.types.Scene.MocanimKeepConstraints = bpy.props.BoolProperty(name="Keep Constraints", description="Keep Constraints after Bake", default=True)
    bpy.types.Scene.MocanimForceInsert = bpy.props.BoolProperty(name="Force Insert", description="Force keyframe on all channels", default=True)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_KeepPose)
    bpy.utils.unregister_class(OBJECT_OT_KeepAction)