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

import bpy, os
from mathutils import Vector
from math import pi
from .fkik import updateView3D, isRigify, LimbSwitchPitchipoy, LimbSwitchRigify, isRigifyPitchipoy
from .utils import isLegName, isArmName

def bind_anim(metarig, rig, context):
    # This script is for using the metarig to redirect Mocap animations to the final rig
    # Works on Pitchipoy rigs only
    create_mrig(metarig, rig, context)
    add_cross_constraints(metarig, rig, context)


def create_mrig(metarig, rig, context):
    
    # Clean metarig from unwanted bones
    
    scn = context.scene
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    scn.objects.active = metarig
    metarig.select = True
    
    bpy.ops.object.duplicate()
    newmrig = bpy.data.objects[metarig.name + '.001']
    newmrig.name = 'mocanimator'
    newmrig.data.name = 'mocanimator'
    scn.MocanimSrcRig = newmrig.name
    bpy.ops.object.select_all(action = 'DESELECT')
    scn.objects.active = newmrig
    newmrig.select = True
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bones_to_keep = ['torso', 'pelvis', 'chest', 'neck', 'spine', 'shoulder', 'upper_arm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'heel', 'toe']
    
    bpy.ops.armature.select_all(action = 'DESELECT')
    
    for ebone in newmrig.data.edit_bones:
        name = ebone.name
        words = name.split('.')
        if not words[0] in bones_to_keep:
            ebone.select = True
        
    bpy.ops.armature.delete()
    add_extra_bones_mrig(newmrig, rig, context)


def add_extra_bones_mrig(metarig, rig, context):
    # add more bones to metarig for animation retargeting
    
    scn = context.scene
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    
    scn.objects.active = rig
    metarig.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    chest_pos = rig.data.edit_bones['chest'].head.copy()
    torso_pos = rig.data.edit_bones['torso'].head.copy()
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    
    scn.objects.active = metarig
    metarig.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    ebones = metarig.data.edit_bones
    spine = ebones['spine']
    spine1 = ebones['spine.001']
    spine2 = ebones['spine.002']
    spine3 = ebones['spine.003']
    spine5 = ebones['spine.005']
    
    
    # Add a Spine Hook bone
    bpy.ops.armature.bone_primitive_add(name="spine_hook")
    spine_hook = ebones['spine_hook']
    spine_hook.head = torso_pos
    spine_hook.tail = spine_hook.head + Vector((0.0,0.28,0.0))
    spine_hook.parent = spine
    
    # Add a Chest Hook bone
    bpy.ops.armature.bone_primitive_add(name="chest_hook")
    chest_hook = ebones['chest_hook']
    chest_hook.head = chest_pos
    chest_hook.tail = chest_hook.head + Vector((0.0,0.21,0.0))
    chest_hook.parent = spine1
    
    # Add a Root bone
    bpy.ops.armature.bone_primitive_add(name="root")
    root = ebones['root']
    root.head = Vector((0.0,0.0,0.0))
    root.tail = root.head + Vector((0.0,0.5,0.0))
    spine.parent = root
    
    # Add extra shoulder bones
    shoulderL = ebones['shoulder.L']
    shoulderL.select = True
    bpy.ops.armature.extrude()
    ebones['shoulder.L.001'].tail = ebones['upper_arm.L'].head
    ebones['upper_arm.L'].parent = ebones['shoulder.L.001']
    ebones['upper_arm.L'].use_connect = True
    shoulderL.select = False
    
    shoulderR = ebones['shoulder.R']
    shoulderR.select = True
    bpy.ops.armature.extrude()
    ebones['shoulder.R.001'].tail = ebones['upper_arm.R'].head
    ebones['upper_arm.R'].parent = ebones['shoulder.R.001']
    ebones['upper_arm.R'].use_connect = True
    shoulderR.select = False

    # Add extra foot bones
    footL = ebones['foot.L']
    footL.select = True
    bpy.ops.armature.extrude()
    ebones['foot.L.001'].name = 'foot_rev.L'
    ebones['foot_rev.L'].tail = ebones['foot.L'].head
    ebones['foot_rev.L'].tail[2] = ebones['foot.L'].tail[2]
    footL.select = False

    footR = ebones['foot.R']
    footR.select = True
    bpy.ops.armature.extrude()
    ebones['foot.R.001'].name = 'foot_rev.R'
    ebones['foot_rev.R'].tail = ebones['foot.R'].head
    ebones['foot_rev.R'].tail[2] = ebones['foot.R'].tail[2]
    footR.select = False


    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')


def fix_feet(metarig, context):

    scn = context.scene
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')

    scn.objects.active = metarig
    metarig.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')

    ebones = metarig.data.edit_bones

    # Add extra foot bones
    footL = ebones['foot.L']
    footL.select = True
    bpy.ops.armature.extrude()
    ebones['foot.L.001'].name = 'foot_rev.L'
    ebones['foot_rev.L'].tail = ebones['foot.L'].head
    ebones['foot_rev.L'].tail[2] = ebones['foot.L'].tail[2]
    footL.select = False

    footR = ebones['foot.R']
    footR.select = True
    bpy.ops.armature.extrude()
    ebones['foot.R.001'].name = 'foot_rev.R'
    ebones['foot_rev.R'].tail = ebones['foot.R'].head
    ebones['foot_rev.R'].tail[2] = ebones['foot.R'].tail[2]
    footR.select = False

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')


def add_cross_constraints(metarig, rig, context):
    # Add Cross Constraints between metarig and rig
    
    scn = context.scene
    
    arms_assoc = {'upper_arm_fk.L': 'upper_arm.L', 'forearm_fk.L': 'forearm.L', 'hand_fk.L': 'hand.L', 'upper_arm_fk.R': 'upper_arm.R', 'forearm_fk.R': 'forearm.R', 'hand_fk.R': 'hand.R',}
    legs_assoc = {'thigh_fk.L': 'shin.L', 'shin_fk.L': 'foot.L', 'foot_fk.L': 'toe.L', 'toe.L': 'toe.L', 'thigh_fk.R': 'shin.R', 'shin_fk.R': 'foot.R', 'foot_fk.R': 'toe.R', 'toe.R': 'toe.R'}
    spine_assoc = {'torso': 'spine_hook', 'hips': 'spine_hook', 'chest': 'chest_hook', 'neck': 'spine.004', 'head': 'spine.006', 'shoulder.L': 'shoulder.L', 'shoulder.R': 'shoulder.R'}
    
    delete_constraints(metarig, rig, context)
    
    if scn.MocanimConstrainRoot:
        constrain_root(metarig, rig, context)
    if scn.MocanimConstrainSpine:
        constrain_spine(metarig, rig, spine_assoc)
    if scn.MocanimConstrainArms:
        constrain_arms(metarig, rig, arms_assoc)
    if scn.MocanimConstrainLegs:
        constrain_legs(metarig, rig, legs_assoc)  

    constrain_ik_legs(metarig, rig, context)
    constrain_ik_arms(metarig, rig, context)


def deselect_pose_bones(rig):
    # Deselect all pose bones

    pbones = rig.pose.bones
    for pbone in pbones:
        pbone.bone.select = False


def constrain_arms(metarig, rig, arms_assoc):
    
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    
    for key in arms_assoc.keys():
        
        pbone = pbones[key]
               
        cns = pbone.constraints.new(type = 'COPY_ROTATION')
        cns.target = metarig
        cns.subtarget = arms_assoc[key]
        cns.name = cns.name + ' -mcn'
        cns.target_space = 'WORLD'
        cns.owner_space = 'POSE'


def constrain_legs(metarig, rig, legs_assoc):
    
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    
    for key in legs_assoc.keys():
        
        pbone = pbones[key]
        
        cns = pbone.constraints.new(type = 'DAMPED_TRACK')
        cns.target = metarig
        cns.subtarget = legs_assoc[key]
        if 'toe' in key:
            cns.head_tail = 1
        else:
            cns.head_tail = 0
        cns.track_axis = 'TRACK_Y'
        cns.name = cns.name + ' -mcn'


def constrain_spine(metarig, rig, spine_assoc):
    
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    scn = bpy.context.scene

    for key in spine_assoc.keys():
        
        pbone = pbones[key]
        
        if key == 'torso' and scn.MocanimConstrainTorso:
            cns = pbone.constraints.new(type = 'COPY_LOCATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.use_y = False
            cns.name = cns.name + ' -mcn'
            cns.target_space = 'WORLD'
            cns.owner_space = 'POSE'
            
            cns = pbone.constraints.new(type = 'DAMPED_TRACK')
            cns.target = metarig
            cns.subtarget = 'spine.003'
            cns.track_axis = 'TRACK_NEGATIVE_Y'
            cns.head_tail = 1
            cns.influence = 0.025
            cns.name = cns.name + ' -mcn'
            
        elif key == 'hips' and scn.MocanimConstrainHips:
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.owner_space = 'LOCAL'
            cns.target_space = 'LOCAL'
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = 'thigh.L'
            cns.influence = 0.33
            cns.owner_space = 'LOCAL'
            cns.target_space = 'LOCAL'
            cns.mute = not scn.MocanimFollowThigh
            cns.name = cns.name + ' -mcn'

            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = 'thigh.R'
            cns.influence = 0.33
            cns.owner_space = 'LOCAL'
            cns.target_space = 'LOCAL'
            cns.mute = not scn.MocanimFollowThigh
            cns.name = cns.name + ' -mcn'
            
        elif key == 'chest' and scn.MocanimConstrainChest:
            cns = pbone.constraints.new(type = 'COPY_LOCATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.name = cns.name + ' -mcn'

            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.name = cns.name + ' -mcn'
            cns.use_x = False
            cns.use_y = False
            cns.target_space = 'WORLD'
            cns.owner_space = 'POSE'
            
            cns = pbone.constraints.new(type = 'DAMPED_TRACK')
            cns.target = metarig
            cns.subtarget = 'spine.005' #mpbones[spine_assoc[key]].parent.name #spine.005?
            cns.track_axis = 'TRACK_Z'
            cns.head_tail = 0
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'DAMPED_TRACK')
            cns.target = metarig
            cns.subtarget = 'spine.005' #mpbones[spine_assoc[key]].parent.name #spine.005?
            cns.track_axis = 'TRACK_Z'
            cns.head_tail = 1
            cns.influence = 0.5
            cns.name = cns.name + ' -mcn'
            
        elif key == 'neck':
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.name = cns.name + ' -mcn'
            cns.target_space = 'WORLD'
            cns.owner_space = 'POSE'

            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc['head']
            cns.name = cns.name + ' -mcn'
            cns.use_y = False
            cns.target_space = 'WORLD'
            cns.owner_space = 'POSE'
            cns.influence = 0.25
            
        elif key == 'head':
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.name = cns.name + ' -mcn'
            cns.target_space = 'WORLD'
            cns.owner_space = 'POSE'
            
        elif 'shoulder' in key:
            cns = pbone.constraints.new(type = 'COPY_ROTATION')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.owner_space = 'LOCAL'
            cns.target_space = 'LOCAL'
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'DAMPED_TRACK')
            cns.target = metarig
            cns.subtarget = spine_assoc[key]
            cns.track_axis = 'TRACK_Y'
            cns.head_tail = 1.0
            cns.influence = 0.5
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'DAMPED_TRACK')
            cns.target = metarig
            words = key.split('.')
            cns.subtarget = 'hand.' + words[1]
            cns.track_axis = 'TRACK_Y'
            cns.head_tail = 0
            cns.influence = 0.3
            cns.name = cns.name + ' -mcn'
            
            cns = pbone.constraints.new(type = 'LIMIT_ROTATION')
            cns.min_x = -5*pi/180
            cns.max_x = pi
            cns.use_limit_x = True
            cns.owner_space = 'LOCAL'
            cns.use_limit_z = True
            if '.L' in key:
                cns.min_z = -15.0*pi/180
                cns.max_z = 0.0
            else:
                cns.min_z = 0.0
                cns.max_z = 15.0*pi/180
            if scn.MocanimUseLimits:
                cns.mute = False
            else:
                cns.mute = True
            cns.name = cns.name + ' -mcn'


def constrain_root(metarig, rig, context):
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    scn = context.scene
    
    pbone = pbones['root']
    
    cns = pbone.constraints.new(type = 'COPY_LOCATION')
    cns.target = metarig
    cns.subtarget = 'root'
    cns.head_tail = 0
    cns.use_z = False
    cns.name = cns.name + ' -mcn'
    
    cns = pbone.constraints.new(type = 'COPY_ROTATION')
    cns.target = metarig
    cns.subtarget = 'root'
    cns.use_x = False
    cns.use_y = False
    cns.owner_space = 'LOCAL'
    cns.target_space = 'LOCAL'
    cns.name = cns.name + ' -mcn'


def constrain_others(metarig, rig, context):
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    scn = context.scene


    pass


def constrain_ik_legs(metarig, rig, context):
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    scn = context.scene

    if 'foot_rev.L' not in mpbones.keys():
        fix_feet(metarig, context)

    for suffix in [".L", ".R"]:
        pbone = pbones['thigh_ik' + suffix]
        cns = pbone.constraints.new(type = 'COPY_LOCATION')
        cns.target = metarig
        cns.subtarget = 'thigh' + suffix
        cns.name = cns.name + ' -mcn'
        cns = pbone.constraints.new(type = 'DAMPED_TRACK')
        cns.target = metarig
        cns.subtarget = 'shin' + suffix
        cns.name = cns.name + ' -mcn'
        cns = pbone.constraints.new(type = 'COPY_ROTATION')
        cns.target = metarig
        cns.subtarget = 'thigh' + suffix
        cns.name = cns.name + ' -mcn'
        cns.use_x = False
        cns.use_z = False
        cns.target_space = 'WORLD'
        cns.owner_space = 'POSE'
        cns = pbone.constraints.new(type = 'LIMIT_ROTATION')
        cns.use_limit_z = True
        if suffix == ".L":
            cns.min_z = -10.0*pi/180
            cns.max_z = 0.0
        else:
            cns.min_z = 0.0
            cns.max_z = 10.0*pi/180
        cns.owner_space = 'LOCAL'
        cns.mute = True
        cns.name = cns.name + ' -mcn'

        pbone = pbones['foot_ik' + suffix]
        cns = pbone.constraints.new(type = 'COPY_LOCATION')
        cns.target = metarig
        cns.subtarget = 'foot_rev' + suffix
        cns.name = cns.name + ' -mcn'
        cns = pbone.constraints.new(type = 'COPY_ROTATION')
        cns.target = metarig
        cns.subtarget = 'foot_rev' + suffix
        cns.use_x = False
        cns.use_y =False
        cns.name = cns.name + ' -mcn'
        cns.target_space = 'WORLD'
        cns.owner_space = 'POSE'
        cns = pbone.constraints.new(type = 'LIMIT_LOCATION')
        cns.use_min_z = True
        cns.min_z = 0.0
        cns.use_transform_limit = True
        if scn.MocanimUseLimits:
            cns.mute = False
        else:
            cns.mute = True
        cns.name = cns.name + ' -mcn'

        pbone = pbones['foot_heel_ik' + suffix]
        cns = pbone.constraints.new(type = 'COPY_ROTATION')
        cns.target = metarig
        cns.subtarget = 'foot_rev' + suffix
        cns.name = cns.name + ' -mcn'
        cns.target_space = 'WORLD'
        cns.owner_space = 'POSE'

        pbone = pbones['MCH-thigh_ik' + suffix]
        cns = pbone.constraints['IK']
        cns.pole_target = metarig
        cns.pole_subtarget = 'shin' + suffix
        cns.pole_angle = -pi/2


def constrain_ik_arms(metarig, rig, context):
    mpbones = metarig.pose.bones
    pbones = rig.pose.bones
    scn = context.scene

    for suffix in [".L", ".R"]:
        pbone = pbones['upper_arm_ik' + suffix]
        cns = pbone.constraints.new(type = 'COPY_ROTATION')
        cns.target = metarig
        cns.subtarget = 'upper_arm' + suffix
        cns.owner_space = 'LOCAL'
        cns.target_space = 'LOCAL'
        cns.name = cns.name + ' -mcn'
        cns = pbone.constraints.new(type = 'LIMIT_ROTATION')
        cns.use_limit_z = True
        if suffix == ".L":
            cns.min_z = -10.0*pi/180
            cns.max_z = 0.0
        else:
            cns.min_z = 0.0
            cns.max_z = 10.0*pi/180
        cns.owner_space = 'LOCAL'
        if scn.MocanimUseLimits:
            cns.mute = False
        else:
            cns.mute = True
        cns.name = cns.name + ' -mcn'

        pbone = pbones['hand_ik' + suffix]
        cns = pbone.constraints.new(type = 'COPY_TRANSFORMS')
        cns.target = metarig
        cns.subtarget = 'hand' + suffix
        cns.name = cns.name + ' -mcn'

        pbone = pbones['MCH-upper_arm_ik' + suffix]
        cns = pbone.constraints['IK']
        cns.pole_target = metarig
        cns.pole_subtarget = 'forearm' + suffix
        cns.pole_angle = -pi/2


def delete_constraints(metarig, rig, context):
        
        scn = context.scene      
        pbones = rig.pose.bones
        
        for pbone in pbones:
            for cns in pbone.constraints:
                if 'IK' in cns.name:
                    cns.pole_target = None
                    cns.pole_subtarget = ''
                    cns.pole_angle = 0
                elif '-mcn' in cns.name:
                    pbone.constraints.remove(cns)


def enable_constraints(metarig, rig, context):
        scn = context.scene
        pbones = rig.pose.bones

        for pbone in pbones:
            for cns in pbone.constraints:
                if 'IK' in cns.name:
                    cns.pole_target = metarig
                    suffix = pbone.name[-2:]
                    if isArmName(pbone.name):
                        name = 'forearm'+suffix
                    elif isLegName(pbone.name):
                        name = 'shin'+suffix
                    cns.pole_subtarget = name
                    cns.pole_angle = -pi/2
                if '-mcn' in cns.name:
                    cns.mute = False


def disable_constraints(metarig, rig, context):
        scn = context.scene
        pbones = rig.pose.bones

        for pbone in pbones:
            for cns in pbone.constraints:
                if 'IK' in cns.name:
                    cns.pole_target = None
                    cns.pole_subtarget = ''
                    cns.pole_angle = 0
                elif '-mcn' in cns.name:
                    cns.mute = True


def SetSwitchFKIKPitchipoy(rig, scn, val):
        
        for suffix in [".L", ".R"]:
            rig.pose.bones["MCH-upper_arm_parent"+suffix]["IK/FK"] = val
            updateView3D()

            rig.pose.bones["MCH-thigh_parent"+suffix]["IK/FK"] = val
            updateView3D()

#-------------------------------------------------------------------

class OBJECT_OT_CreateMetarig(bpy.types.Operator):
    """Create a Mocanim metarig from current metarig before export"""
    bl_idname = "mocanim.create_metarig"
    bl_label = "Create Metarig"
    
    def execute(self,context):
        scn = context.scene

        mrig = bpy.data.objects[scn.MocanimSrcRig]
        rig = bpy.data.objects[scn.MocanimTrgRig]
        
        create_mrig(mrig, rig, context)
        
        return {'FINISHED'}
    
class OBJECT_OT_CreateConstraints(bpy.types.Operator):
    """Binds the BVH and the target rig via a set of Constraints"""
    bl_idname = "mocanim.create_constraints"
    bl_label = "Create Constraints"

    def execute(self,context):
        scn = context.scene
        mrig = bpy.data.objects[scn.MocanimSrcRig]
        rig = bpy.data.objects[scn.MocanimTrgRig]
        
        add_cross_constraints(mrig, rig, context)
        rig.data.layers = [False, False, False, True, False, False, False, False, True, False, False, True, False, False, True, False, False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False ]
        #SetSwitchFKIKPitchipoy(rig, scn, 1.0)

        if isRigify(rig):
            LimbSwitchRigify(rig, scn)
        elif isRigifyPitchipoy(rig):
            LimbSwitchPitchipoy(rig,scn)

        return {'FINISHED'}
    
class OBJECT_OT_DeleteConstraints(bpy.types.Operator):
    """Deletes Constraints binding the BVH and the target rig"""
    bl_idname = "mocanim.delete_constraints"
    bl_label = "Delete Constraints"
    
    def execute(self,context):
        scn = context.scene
        mrig = bpy.data.objects[scn.MocanimSrcRig]
        rig = bpy.data.objects[scn.MocanimTrgRig]

        delete_constraints(mrig,rig,context)
        
        return {'FINISHED'}

class OBJECT_OT_EnableConstraints(bpy.types.Operator):
    """Enable all Constraints binding the BVH and the target rig"""
    bl_idname = "mocanim.enable_constraints"
    bl_label = "Enable Constraints"

    def execute(self,context):
        scn = context.scene
        mrig = bpy.data.objects[scn.MocanimSrcRig]
        rig = bpy.data.objects[scn.MocanimTrgRig]

        enable_constraints(mrig,rig,context)
        return {'FINISHED'}

class OBJECT_OT_DisableConstraints(bpy.types.Operator):
    """Disable all Constraints binding the BVH and the target rig"""
    bl_idname = "mocanim.disable_constraints"
    bl_label = "Disable Constraints"

    def execute(self,context):
        scn = context.scene
        mrig = bpy.data.objects[scn.MocanimSrcRig]
        rig = bpy.data.objects[scn.MocanimTrgRig]

        disable_constraints(mrig,rig,context)
        return {'FINISHED'}

class OBJECT_OT_SelectSource(bpy.types.Operator):
    """Select the Performer Armature"""
    bl_idname = "mocanim.select_source"
    bl_label = "Select Performer"
    
    def execute(self,context):
        
        scn = context.scene
        rig = context.object
        
        if (rig != None) and (rig.type == 'ARMATURE'):
             scn.MocanimSrcRig = rig.name
        
        return {'FINISHED'}

class OBJECT_OT_SelectTarget(bpy.types.Operator):
    """Select the Character Armature"""
    bl_idname = "mocanim.select_target"
    bl_label = "Select Character"
    
    def execute(self,context):
        
        scn = context.scene
        rig = context.object
        
        if (rig != None) and (rig.type == 'ARMATURE'):
             scn.MocanimTrgRig = rig.name
        
        return {'FINISHED'}

class OBJECT_OT_ExportBVH(bpy.types.Operator):
    """ Export Mocanim Metarig to BVH """
    bl_idname = "mocanim.export_metarig"
    bl_label = "Export Mocanimator"

    def execute(self,context):
        scn = context.scene
        mocanimator = scn.objects[scn.MocanimSrcRig]
        bpy.ops.object.mode_set(mode = 'OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

        mocanimator.select = True

        bpy.ops.transform.rotate(value=-pi/2, axis=(1,0,0))

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        if scn.MocanimExportPath == '//./':
            path = bpy.data.filepath.split('/')
            fname = path[-1]
            name = fname.split('.')
            name = '.'.join(name[0:-1])
            name = name + '.bvh'
            path.pop()
            path.append(name)
            pathandname = '/'.join(path)
        else:
            pathandname = bpy.path.abspath(scn.MocanimExportPath)

        bpy.ops.export_anim.bvh(filepath=pathandname)


        bpy.ops.object.delete(use_global=False)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_CreateMetarig)
    bpy.utils.register_class(OBJECT_OT_CreateConstraints)
    bpy.utils.register_class(OBJECT_OT_DeleteConstraints)
    bpy.utils.register_class(OBJECT_OT_EnableConstraints)
    bpy.utils.register_class(OBJECT_OT_DisableConstraints)
    bpy.utils.register_class(OBJECT_OT_SelectSource)
    bpy.utils.register_class(OBJECT_OT_SelectTarget)
    bpy.utils.register_class(OBJECT_OT_ExportBVH)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CreateMetarig)
    bpy.utils.unregister_class(OBJECT_OT_CreateConstraints)
    bpy.utils.unregister_class(OBJECT_OT_DeleteConstraints)
    bpy.utils.unregister_class(OBJECT_OT_EnableConstraints)
    bpy.utils.unregister_class(OBJECT_OT_DisableConstraints)
    bpy.utils.unregister_class(OBJECT_OT_SelectSource)
    bpy.utils.unregister_class(OBJECT_OT_SelectTarget)
    bpy.utils.unregister_class(OBJECT_OT_ExportBVH)