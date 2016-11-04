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

def isArmName(name):
    identifiers=['hand', 'arm', 'shoulder']

    for id in identifiers:
        if id in name:
            return True

    return False

def isLegName(name):
    identifiers=['thigh', 'foot']

    for id in identifiers:
        if id in name:
            return True

    return False

def isRigify(rig):
    try:
        rig.pose.bones['MCH-spine.flex']
        return True
    except KeyError:
        return False

def isRigifyPitchipoy(rig):
    try:
        rig.pose.bones['ORG-pelvis.L']
        return True
    except KeyError:
        return False
    