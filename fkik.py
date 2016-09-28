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
# from mathutils import Vector, Matrix
import datetime
from bpy.props import *
from .utils import *
from .keyframing import *

SnapBonesRigify = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm.fk", "forearm.fk", "hand.fk"],
    "ArmIK" : ["hand_ik", "elbow_target.ik"],
    "Leg"   : ["thigh", "shin", "foot"],
    "LegFK" : ["thigh.fk", "shin.fk", "foot.fk"],
    "LegIK" : ["foot.ik", "foot_roll.ik", "knee_target.ik"],
}

SnapBonesRigifyPitchipoy = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm_fk", "forearm_fk", "hand_fk"],
    "ArmIK" : ["hand_ik", "upper_arm_ik"],
    "Leg"   : ["thigh", "shin", "foot"],
    "LegFK" : ["thigh_fk", "shin_fk", "foot_fk", "toe"],
    "LegIK" : ["thigh_ik", "foot_ik", "foot_heel_ik", "toe"],
}


def updateView3D():
    
    cframe=bpy.context.scene.frame_current
    bpy.context.scene.frame_set(cframe)
    
def FktoIkRigify(rig,scn):
    pass

def IktoFkRigify(rig,scn):
    pass

def FktoIkPitchipoy(rig,scn, window='ALL'):
    from .fkik_extras import ik2fk_arm, ik2fk_leg

    if window == 'ALL':
        frames = getKeyedFrames(rig)
        frames = [f for f in frames if f in range(scn.MocanimTransferStartFrame, scn.MocanimTransferEndFrame+1)]
    elif window == 'CURRENT':
        frames = [scn.frame_current]
    
    for f in frames:
        scn.frame_set(f)
        if scn.MocanimFkIkArms:
            for suffix in [".L", ".R"]:
                uarm  = "upper_arm_fk"+suffix
                farm  = "forearm_fk"+suffix
                hand  = "hand_fk"+suffix
                uarmi = "upper_arm_ik"+suffix
                farmi = "MCH-upper_arm_ik"+suffix
                handi = "hand_ik"+suffix

                fk = [uarm,farm,hand]
                ik = [uarmi,farmi,handi]
                ik2fk_arm(rig, fk, ik)

                # insertKeyFrame(rig.pose.bones[uarmi])
                # insertKeyFrame(rig.pose.bones[farmi])
                # insertKeyFrame(rig.pose.bones[handi])


                print('arm' + suffix)
                
        if scn.MocanimFkIkLegs:
            for suffix in [".L", ".R"]:
                thigh  = "thigh_fk"+suffix
                shin   = "shin_fk"+suffix
                foot   = "foot_fk"+suffix
                mfoot  = "MCH-foot_fk"+suffix
                thighi = "thigh_ik"+suffix
                shini  = "MCH-thigh_ik"+suffix
                footi  = "foot_ik"+suffix
                footroll = "foot_heel_ik"+suffix
                mfooti = "MCH-thigh_ik_target"+suffix

                fk = [thigh,shin,mfoot,foot]
                ik = [thighi,shini,footi,footroll,mfooti]
                
                rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = 1.0
                updateView3D()
                ik2fk_leg(rig, fk, ik)

                # insertKeyFrame(rig.pose.bones[thighi])
                # insertKeyFrame(rig.pose.bones[shini])
                # insertKeyFrame(rig.pose.bones[footi])
                # insertKeyFrame(rig.pose.bones[footroll])
                # insertKeyFrame(rig.pose.bones[mfooti])

                print('leg' + suffix)
        bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        #bpy.ops.nla.bake(frame_start=f, frame_end=f, step=1, only_selected=scn.MocanimTransferOnlySelected, visual_keying=True, clear_constraints=False, clear_parents=False, use_current_action= True, bake_types={'POSE'})

    for suffix in [".L", ".R"]:
        if scn.MocanimFkIkArms:
            rig.pose.bones["MCH-upper_arm_parent"+suffix]["IK/FK"] = 0.0
            updateView3D()
        if scn.MocanimFkIkLegs:
            rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = 0.0
            updateView3D()
            
def IktoFkPitchipoy(rig,scn, window='ALL'):
    from .fkik_extras import fk2ik_arm, fk2ik_leg

    if window == 'ALL':
        frames = getKeyedFrames(rig)
        frames = [f for f in frames if f in range(scn.MocanimTransferStartFrame, scn.MocanimTransferEndFrame+1)]
    elif window == 'CURRENT':
        frames = [scn.frame_current]
    
    for f in frames:
        scn.frame_set(f)
        if scn.MocanimFkIkArms:
            for suffix in [".L", ".R"]:
                uarm  = "upper_arm_fk"+suffix
                farm  = "forearm_fk"+suffix
                hand  = "hand_fk"+suffix
                uarmi = "upper_arm_ik"+suffix
                farmi = "MCH-upper_arm_ik"+suffix
                handi = "hand_ik"+suffix

                fk = [uarm,farm,hand]
                ik = [uarmi,farmi,handi]
                fk2ik_arm(rig, fk, ik)

                # insertKeyFrame(rig.pose.bones[uarm])
                # insertKeyFrame(rig.pose.bones[farm])
                # insertKeyFrame(rig.pose.bones[hand])

        if scn.MocanimFkIkLegs:
            for suffix in [".L", ".R"]:
                thigh  = "thigh_fk"+suffix
                shin   = "shin_fk"+suffix
                foot   = "foot_fk"+suffix
                mfoot  = "MCH-foot_fk"+suffix
                thighi = "thigh_ik"+suffix
                shini  = "MCH-thigh_ik"+suffix
                footi  = "MCH-thigh_ik_target"+suffix
                mfooti = "MCH-thigh_ik_target"+suffix

                fk = [thigh,shin,foot,mfoot]
                ik = [thighi,shini,footi,mfooti]
                fk2ik_leg(rig, fk, ik)

                # insertKeyFrame(rig.pose.bones[thigh])
                # insertKeyFrame(rig.pose.bones[shin])
                # insertKeyFrame(rig.pose.bones[foot])
                # insertKeyFrame(rig.pose.bones[mfoot])
        bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        #bpy.ops.nla.bake(frame_start=f, frame_end=f, step=1, only_selected=scn.MocanimTransferOnlySelected, visual_keying=True, clear_constraints=False, clear_parents=False, use_current_action= True, bake_types={'POSE'})


    for suffix in [".L", ".R"]:
        if scn.MocanimFkIkArms:
            rig.pose.bones["MCH-upper_arm_parent"+suffix]["IK/FK"] = 1.0
            updateView3D()
        if scn.MocanimFkIkLegs:
            rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = 1.0
            updateView3D()

def LimbSwitchRigify(rig,scn):
    pass

def LimbSwitchPitchipoy(rig,scn):
    
    for suffix in [".L", ".R"]:
        if scn.MocanimArmsIk:
            rig.pose.bones["MCH-upper_arm_parent"+suffix]["IK/FK"] = 0.0
            updateView3D()
        else:
            rig.pose.bones["MCH-upper_arm_parent"+suffix]["IK/FK"] = 1.0
            updateView3D()
        if scn.MocanimLegsIk:
            rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = 0.0
            updateView3D()
        else:
            rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = 1.0
            updateView3D()
            
    if scn.MocanimArmsIk:
        rig.data.layers[7] = True
        rig.data.layers[10] = True
        rig.data.layers[8] = False
        rig.data.layers[11] = False
    else:
        rig.data.layers[7] = False
        rig.data.layers[10] = False
        rig.data.layers[8] = True
        rig.data.layers[11] = True

    if scn.MocanimLegsIk:
        rig.data.layers[13] = True
        rig.data.layers[16] = True
        rig.data.layers[14] = False
        rig.data.layers[17] = False
    else:
        rig.data.layers[13] = False
        rig.data.layers[16] = False
        rig.data.layers[14] = True
        rig.data.layers[17] = True

def clearAnimation(rig, scn, act, type, snapBones):

    ikBones = []
    if scn.MocanimFkIkArms:
        for bname in snapBones["Arm" + type]:
            if bname is not None:
                ikBones += [bname+".L", bname+".R"]
    if scn.MocanimFkIkLegs:
        for bname in snapBones["Leg" + type]:
            if bname is not None:
                ikBones += [bname+".L", bname+".R"]

    ikFCurves = []
    for fcu in act.fcurves:
        words = fcu.data_path.split('"')
        if (words[0] == "pose.bones[" and
            words[1] in ikBones):
            ikFCurves.append(fcu)

    if ikFCurves == []:
        return
    
    for fcu in ikFCurves:
        act.fcurves.remove(fcu)
    
    # Put cleared bones back to rest pose
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.scale_clear()
    
    updateView3D()

class OBJECT_OT_IK2FK(bpy.types.Operator):
    """ Snaps IK limb on FK limb at current frame"""
    bl_idname = "mocanim.ik2fk"
    bl_label = "IK2FK"
    bl_description = "Snaps IK limb on FK"

    def execute(self,context):
        scn = context.scene
        rig = context.object

        if isRigify(rig):
            FktoIkRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            FktoIkPitchipoy(rig,scn, window='CURRENT')

        rig.data.layers = [False, False, False, True, False, False, False, True, False, False, True, False, False, True, False, False, True, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False]

        return {'FINISHED'}

class OBJECT_OT_FK2IK(bpy.types.Operator):
    """ Snaps FK limb on IK limb at current frame"""
    bl_idname = "mocanim.fk2ik"
    bl_label = "FK2IK"
    bl_description = "Snaps FK limb on IK"

    def execute(self,context):
        scn = context.scene
        rig = context.object

        if isRigify(rig):
            IktoFkRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            IktoFkPitchipoy(rig,scn, window='CURRENT')
        return {'FINISHED'}

class OBJECT_OT_TransferFKtoIK(bpy.types.Operator):
    """Transfers FK animation to IK"""
    bl_idname = "mocanim.transfer_fk_to_ik"
    bl_label = "Transfer FK anim to IK"
    bl_description = "Transfer FK animation to IK bones"

    expected_time = StringProperty(name = 'Estimated Time (H:M:S):', default = '')

    def invoke(self,context,event):

        rig=context.object

        frames = len(getKeyedFrames(rig))
        time_sec = 5*frames

        self.expected_time = str(datetime.timedelta(seconds=time_sec))

        return context.window_manager.invoke_props_dialog(self)

    def execute(self,context):
        scn = context.scene
        rig = context.object
        
        if isRigify(rig):
            FktoIkRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            FktoIkPitchipoy(rig,scn,window='ALL')
        
        rig.data.layers = [False, False, False, True, False, False, False, True, False, False, True, False, False, True, False, False, True, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False]        
        
        return {'FINISHED'}
    
class OBJECT_OT_TransferIKtoFK(bpy.types.Operator):
    """Transfers IK animation to FK"""
    bl_idname = "mocanim.transfer_ik_to_fk"
    bl_label = "Transfer IK anim to FK"
    bl_description = "Transfer IK animation to FK bones"
    
    def execute(self,context):
        scn = context.scene
        rig = context.object
        
        if isRigify(rig):
            IktoFkRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            IktoFkPitchipoy(rig,scn, window='ALL')
        
        return {'FINISHED'}

class OBJECT_OT_LimbSwitch(bpy.types.Operator):
    """Switches limbs between FK and IK"""
    bl_idname = "mocanim.limb_switch"
    bl_label = "Switch limbs"
    bl_description = "Switches limbs between FK and IK"
    
    def execute(self,context):
        scn = context.scene
        rig = context.object
        
        if isRigify(rig):
            LimbSwitchRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            LimbSwitchPitchipoy(rig,scn)
        
        return {'FINISHED'}
    
class OBJECT_OT_ClearAnimation(bpy.types.Operator):
    bl_idname = "mocanim.clear_animation"
    bl_label = "Clear Animation"
    bl_description = "Clear Animation For FK or IK Bones"
    type = StringProperty()

    def execute(self, context):
        
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            rig = context.object
            scn = context.scene
            if not rig.animation_data:
                return{'FINISHED'}
            act = rig.animation_data.action
            if not act:
                return{'FINISHED'}
 
#             if isMhxRig(rig):
#                 clearAnimation(rig, scn, act, self.type, SnapBonesAlpha8)
#                 setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, (self.type=="FK"))

            elif isRigify(rig):
                clearAnimation(rig, scn, act, self.type, SnapBonesRigify)
            elif isRigifyPitchipoy(rig):
                clearAnimation(rig, scn, act, self.type, SnapBonesRigifyPitchipoy)
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return{'FINISHED'}

class OBJECT_OT_GetTransferFrameRange(bpy.types.Operator):
    """Get start and end frame range"""
    bl_idname = "mocanim.get_transfer_frame_range"
    bl_label = "Get Frame Range For Transfer"

    def execute(self,context):

        scn = context.scene

        scn.MocanimTransferStartFrame = scn.frame_start
        scn.MocanimTransferEndFrame = scn.frame_end

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_IK2FK)
    bpy.utils.register_class(OBJECT_OT_FK2IK)
    bpy.utils.register_class(OBJECT_OT_TransferFKtoIK)
    bpy.utils.register_class(OBJECT_OT_TransferIKtoFK)
    bpy.utils.register_class(OBJECT_OT_ClearAnimation)
    bpy.utils.register_class(OBJECT_OT_LimbSwitch)
    bpy.utils.register_class(OBJECT_OT_GetTransferFrameRange)
    bpy.types.Scene.MocanimTransferStartFrame = bpy.props.IntProperty(name="Start Frame", description="First Frame to Transfer", default=0, min= 0)
    bpy.types.Scene.MocanimTransferEndFrame = bpy.props.IntProperty(name="End Frame", description="Last Frame to Transfer", default=0, min= 0)
    bpy.types.Scene.MocanimTransferOnlySelected = bpy.props.BoolProperty(name="Transfer Only Selected", description="Transfer selected bones only", default=False)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_IK2FK)
    bpy.utils.unregister_class(OBJECT_OT_FK2IK)
    bpy.utils.unregister_class(OBJECT_OT_TransferFKtoIK)
    bpy.utils.unregister_class(OBJECT_OT_TransferIKtoFK)
    bpy.utils.unregister_class(OBJECT_OT_ClearAnimation)
    bpy.utils.unregister_class(OBJECT_OT_LimbSwitch)
    bpy.utils.unregister_class(OBJECT_OT_GetTransferFrameRange)
