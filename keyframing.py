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

        rig = scn.objects.active #bpy.data.objects[scn.MocanimTrgRig]

        bpy.ops.object.mode_set(mode = 'POSE')
        pbones = rig.pose.bones

        # BUG After bake with visual_keying on or after Apply Visual Transform the first ik bones are rescaled
        bones_to_rescale = [bone.name for bone in pbones if ('thigh_ik' in bone.name or 'upper_arm_ik' in bone.name)and(bone.bone.select)]
        scales = {}
        for b in bones_to_rescale:
            scales[b] = pbones[b].scale.copy()

        # Saving bones rotation
        rotations = {}
        for pb in pbones:
            if pb.rotation_mode == 'QUATERNION':
                rotations[pb.name] = pb.rotation_quaternion.copy()
            elif pb.rotation_mode == 'AXIS_ANGLE':
                rotations[pb.name] = pb.rotation_axis_angle.copy()
            else:
                rotations[pb.name] = pb.rotation_euler.copy()

        # if scn.MocanimForceInsert:
        #     bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')

        # bpy.ops.nla.bake(frame_start=scn.frame_current, frame_end=scn.frame_current, step=1, only_selected=scn.MocanimOnlySelected, visual_keying=False, clear_constraints=not scn.MocanimKeepConstraints, clear_parents=False, use_current_action= not scn.MocanimNewAction, bake_types={'POSE'})

        if scn.MocanimOnlySelected:
            bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')
            for pb in pbones:
                if pb.bone.select:
                    insertKeyFrame(pb)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            for pb in pbones:
                if pb.bone.select:
                    insertKeyFrame(pb)

        else:
            bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
            for pb in pbones:
                insertKeyFrame(pb)
                if pb.name in bones_to_rescale:
                    pb.scale = scales[pb.name]
                bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                insertKeyFrame(pb)


        #Correct scales

        # for b in bones_to_rescale:
        #     pbones[b].scale = scales[b]
        #     scn.update()
        #     insertKeyFrame(pbones[b])
        #
        # # Correct Rotations
        # for pb in pbones:
        #     if pb.rotation_mode == 'QUATERNION':
        #         pb.rotation_quaternion = rotations[pb.name]
        #     elif pb.rotation_mode == 'AXIS_ANGLE':
        #         pb.rotation_axis_angle = rotations[pb.name]
        #     else:
        #         pb.rotation_euler = rotations[pb.name]

        return {'FINISHED'}

class OBJECT_OT_ClearPose(bpy.types.Operator):
    """Delete current pose for selected bone"""
    bl_idname = "mocanim.clear_pose"
    bl_label = "Clear Pose"

    def execute(self, context):

        scn = context.scene

        rig = bpy.data.objects[scn.MocanimTrgRig]

        pbones = rig.pose.bones
        fcurves = rig.animation_data.action.fcurves

        for pb in pbones:
            if pb.bone.select == True:
                for curve in fcurves:
                    if pb.bone.name in curve.data_path:
                        if len(curve.keyframe_points) == 1:
                            fcurves.remove(curve)
                        else:
                            pb.keyframe_delete(curve.data_path.split('.')[-1])

        return {'FINISHED'}

class OBJECT_OT_KeepAction(bpy.types.Operator):
    """Transfer bvh action to target rig    """
    bl_idname = "mocanim.keep_action"
    bl_label = "Keep Action"

    def execute(self, context):

        scn = context.scene

        rig = scn.objects.active #bpy.data.objects[scn.MocanimTrgRig]

        bpy.ops.object.mode_set(mode = 'POSE')
        pbones = rig.pose.bones

        # BUG After bake with visual_keying on or after Apply Visual Transform the first ik bones are rescaled
        bones_to_rescale = [bone.name for bone in pbones if ('thigh_ik' in bone.name or 'upper_arm_ik' in bone.name)and(bone.bone.select)]
        scales = {}
        for b in bones_to_rescale:
            scales[b] = pbones[b].scale.copy()

        bpy.ops.nla.bake(frame_start=scn.MocanimStartFrame, frame_end=scn.MocanimEndFrame, step=scn.MocanimFrameStep, only_selected=scn.MocanimOnlySelected, visual_keying=True, clear_constraints=not scn.MocanimKeepConstraints, clear_parents=False, use_current_action= not scn.MocanimNewAction, bake_types={'POSE'})

        for f in range(scn.MocanimStartFrame, scn.MocanimEndFrame+1, scn.MocanimFrameStep):
            for b in bones_to_rescale:
                scn.frame_set(f)
                pbones[b].scale = scales[b]
                pbones[b].keyframe_insert('scale')

        return {'FINISHED'}

class OBJECT_OT_ClearAction(bpy.types.Operator):
    """Delete current action for selected bone"""
    bl_idname = "mocanim.clear_action"
    bl_label = "Clear Action"

    def execute(self, context):

        scn = context.scene

        rig = bpy.data.objects[scn.MocanimTrgRig]
        pbones = rig.pose.bones

        fcurves=rig.animation_data.action.fcurves

        for pb in pbones:
            if pb.bone.select:
                for fcurve in fcurves:
                    if pb.name in fcurve.data_path:
                        fcurves.remove(fcurve)

        scn.frame_set(scn.frame_current-1)
        scn.frame_set(scn.frame_current+1)


        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_KeepPose)
    bpy.utils.register_class(OBJECT_OT_KeepAction)
    bpy.utils.register_class(OBJECT_OT_ClearPose)
    bpy.utils.register_class(OBJECT_OT_ClearAction)

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
    bpy.utils.unregister_class(OBJECT_OT_ClearPose)
    bpy.utils.unregister_class(OBJECT_OT_ClearAction)