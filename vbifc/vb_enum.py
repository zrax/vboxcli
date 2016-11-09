# This file is part of vboxcli
# Copyright (C) 2016  Michael Hansen
#
# vboxcli is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# vboxcli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with vboxcli; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from . import VBoxConstants

_ac_text_cache = None
def AudioControllerType_text(id):
    global _ac_text_cache
    if _ac_text_cache is None:
        vbconst = VBoxConstants()
        _ac_text_cache = {
            vbconst.AudioControllerType_AC97: u'ICH AC97',
            vbconst.AudioControllerType_SB16: u'SoundBlaster 16',
            vbconst.AudioControllerType_HDA: u'Intel HD Audio'
        }
    if id in _ac_text_cache:
        return _ac_text_cache[id]
    else:
        return u'(Unknown)'

_ad_text_cache = None
def AudioDriverType_text(id):
    global _ad_text_cache
    if _ad_text_cache is None:
        vbconst = VBoxConstants()
        _ad_text_cache = {
            vbconst.AudioDriverType_Null: u'Dummy',
            vbconst.AudioDriverType_WinMM: u'Windows Multimedia',
            vbconst.AudioDriverType_OSS: u'OSS',
            vbconst.AudioDriverType_ALSA: u'ALSA',
            vbconst.AudioDriverType_DirectSound: u'DirectSound',
            vbconst.AudioDriverType_CoreAudio: u'CoreAudio',
            vbconst.AudioDriverType_Pulse: u'PulseAudio',
            vbconst.AudioDriverType_SolAudio: u'Solaris Audio'
        }
    if id in _ad_text_cache:
        return _ad_text_cache[id]
    else:
        return u'(Unknown)'

_dt_text_cache = None
def DeviceType_text(id):
    global _dt_text_cache
    if _dt_text_cache is None:
        vbconst = VBoxConstants()
        _dt_text_cache = {
            vbconst.DeviceType_Null: u'',
            vbconst.DeviceType_Floppy: u'Floppy',
            vbconst.DeviceType_DVD: u'Optical',
            vbconst.DeviceType_HardDisk: u'Hard Disk',
            vbconst.DeviceType_Network: u'Network',
            vbconst.DeviceType_USB: u'USB',
            vbconst.DeviceType_SharedFolder: u'Shared Folder',
            vbconst.DeviceType_Graphics3D: u'3D Graphics'
        }
    if id in _dt_text_cache:
        return _dt_text_cache[id]
    else:
        return u'(Unknown)'

_ms_text_cache = None
def MachineState_text(id):
    global _ms_text_cache
    if _ms_text_cache is None:
        vbconst = VBoxConstants()
        _ms_text_cache = {
            vbconst.MachineState_Null: u'<Invalid>',
            vbconst.MachineState_PoweredOff: u'Powered Off',
            vbconst.MachineState_Saved: u'Saved',
            vbconst.MachineState_Teleported: u'Teleported',
            vbconst.MachineState_Aborted: u'Aborted',
            vbconst.MachineState_Running: u'Running',
            vbconst.MachineState_Paused: u'Paused',
            vbconst.MachineState_Stuck: u'Guru Meditation',
            vbconst.MachineState_Teleporting: u'Teleporting',
            vbconst.MachineState_LiveSnapshotting: u'Creating Snapshot (Online)',
            vbconst.MachineState_Starting: u'Starting',
            vbconst.MachineState_Stopping: u'Stopping',
            vbconst.MachineState_Saving: u'Saving',
            vbconst.MachineState_Restoring: u'Restoring',
            vbconst.MachineState_TeleportingPausedVM: u'Teleporting (Paused)',
            vbconst.MachineState_TeleportingIn: u'Teleporting In',
            vbconst.MachineState_FaultTolerantSyncing: u'Syncing',
            vbconst.MachineState_DeletingSnapshotOnline: u'Deleting Snapshot (Online)',
            vbconst.MachineState_DeletingSnapshotPaused: u'Deleting Snapshot (Paused)',
            vbconst.MachineState_OnlineSnapshotting: u'Creating Snapshot (Online)',
            vbconst.MachineState_RestoringSnapshot: u'Restoring Snapshot',
            vbconst.MachineState_DeletingSnapshot: u'Deleting Snapshot',
            vbconst.MachineState_SettingUp: u'Configuring',
            vbconst.MachineState_Snapshotting: u'Creating Snapshot'
        }
    if id in _ms_text_cache:
        return _ms_text_cache[id]
    else:
        return u'(Unknown)'

_ms_icon_cache = None
def MachineState_icon(id):
    global _ms_icon_cache
    if _ms_icon_cache is None:
        vbconst = VBoxConstants()
        _ms_icon_cache = {
            # There may be better unicode symbols available, but these are
            # ones I found to work even in older/limited terminal fonts.
            vbconst.MachineState_Null: ('state error', u'?'),
            vbconst.MachineState_PoweredOff: ('state off', u'\u25a0'),
            vbconst.MachineState_Saved: ('state off', u'\u25c9'),
            vbconst.MachineState_Teleported: ('state off', u'T'),
            vbconst.MachineState_Aborted: ('state error', u'!'),
            vbconst.MachineState_Running: ('state run', u'\u25b6'),
            vbconst.MachineState_Paused: ('state pause', u'\u2225'),
            vbconst.MachineState_Stuck: ('state error', u'!'),
            vbconst.MachineState_Teleporting: ('state on', u'T'),
            vbconst.MachineState_LiveSnapshotting: ('state on', u'S'),
            vbconst.MachineState_Starting: ('state on', u'\u25a0'),
            vbconst.MachineState_Stopping: ('state pause', u'\u25a0'),
            vbconst.MachineState_Saving: ('state pause', u'\u25d4'),
            vbconst.MachineState_Restoring: ('state pause', u'\u25d4'),
            vbconst.MachineState_TeleportingPausedVM: ('state pause', u'T'),
            vbconst.MachineState_TeleportingIn: ('state off', u'T'),
            vbconst.MachineState_FaultTolerantSyncing: ('state run', u'\u25e9'),
            vbconst.MachineState_DeletingSnapshotOnline: ('state run', u'D'),
            vbconst.MachineState_DeletingSnapshotPaused: ('state pause', u'D'),
            vbconst.MachineState_OnlineSnapshotting: ('state pause', u'S'),
            vbconst.MachineState_RestoringSnapshot: ('state off', u'R'),
            vbconst.MachineState_DeletingSnapshot: ('state off', u'D'),
            vbconst.MachineState_SettingUp: ('state off', u'\u25a0'),
            vbconst.MachineState_Snapshotting: ('state off', u'S')
        }
    if id in _ms_icon_cache:
        return _ms_icon_cache[id]
    else:
        return ('state error', u'?')

_mt_text_cache = None
def MediumType_text(id):
    global _mt_text_cache
    if _mt_text_cache is None:
        vbconst = VBoxConstants()
        _mt_text_cache = {
            vbconst.MediumType_Normal: u'Normal',
            vbconst.MediumType_Immutable: u'Immutable',
            vbconst.MediumType_Writethrough: u'Writethrough',
            vbconst.MediumType_Shareable: u'Shareable',
            vbconst.MediumType_Readonly: u'Read-Only',
            vbconst.MediumType_MultiAttach: u'Multi-Attach'
        }
    if id in _mt_text_cache:
        return _mt_text_cache[id]
    else:
        return u'(Unknown)'

_nadt_text_cache = None
def NetworkAdapterType_text(id):
    global _nadt_text_cache
    if _nadt_text_cache is None:
        vbconst = VBoxConstants()
        _nadt_text_cache = {
            vbconst.NetworkAdapterType_Null: u'<Invalid>',
            vbconst.NetworkAdapterType_Am79C970A: u'AMD PCNet-PCI II',
            vbconst.NetworkAdapterType_Am79C973: u'AMD PCNet-FAST III',
            vbconst.NetworkAdapterType_I82540EM: u'Intel PRO/1000 MT Desktop',
            vbconst.NetworkAdapterType_I82543GC: u'Intel PRO/1000 T Server',
            vbconst.NetworkAdapterType_I82545EM: u'Intel PRO/1000 MT Server',
            vbconst.NetworkAdapterType_Virtio: u'Paravirtualized'
        }
    if id in _nadt_text_cache:
        return _nadt_text_cache[id]
    else:
        return u'(Unknown)'

_natt_text_cache = None
def NetworkAttachmentType_text(id):
    global _natt_text_cache
    if _natt_text_cache is None:
        vbconst = VBoxConstants()
        _natt_text_cache = {
            vbconst.NetworkAttachmentType_Null: u'',
            vbconst.NetworkAttachmentType_NAT: u'NAT',
            vbconst.NetworkAttachmentType_Bridged: u'Bridged',
            vbconst.NetworkAttachmentType_Internal: u'Internal',
            vbconst.NetworkAttachmentType_HostOnly: u'Host-Only',
            vbconst.NetworkAttachmentType_Generic: u'Generic',
            vbconst.NetworkAttachmentType_NATNetwork: u'NAT Network'
        }
    if id in _natt_text_cache:
        return _natt_text_cache[id]
    else:
        return u'(Unknown)'

_pvp_text_cache = None
def ParavirtProvider_text(id):
    global _pvp_text_cache
    if _pvp_text_cache is None:
        vbconst = VBoxConstants()
        _pvp_text_cache = {
            vbconst.ParavirtProvider_None: u'',
            vbconst.ParavirtProvider_Default: u'Default',
            vbconst.ParavirtProvider_Legacy: u'Legacy',
            vbconst.ParavirtProvider_Minimal: u'Minimal',
            vbconst.ParavirtProvider_HyperV: u'Hyper-V',
            vbconst.ParavirtProvider_KVM: u'KVM'
        }
    if id in _pvp_text_cache:
        return _pvp_text_cache[id]
    else:
        return u'(Unknown)'

_pm_text_cache = None
def PortMode_text(id):
    global _pm_text_cache
    if _pm_text_cache is None:
        vbconst = VBoxConstants()
        _pm_text_cache = {
            vbconst.PortMode_Disconnected: u'Disconnected',
            vbconst.PortMode_HostPipe: u'Host Pipe',
            vbconst.PortMode_HostDevice: u'Host Device',
            vbconst.PortMode_RawFile: u'Raw File',
            vbconst.PortMode_TCP: u'TCP Socket'
        }
    if id in _pm_text_cache:
        return _pm_text_cache[id]
    else:
        return u'(Unknown)'

_sb_text_cache = None
def StorageBus_text(id):
    global _sb_text_cache
    if _sb_text_cache is None:
        vbconst = VBoxConstants()
        _sb_text_cache = {
            vbconst.StorageBus_Null: u'<invalid>',
            vbconst.StorageBus_IDE: u'IDE',
            vbconst.StorageBus_SATA: u'SATA',
            vbconst.StorageBus_SCSI: u'SCSI',
            vbconst.StorageBus_Floppy: u'Floppy',
            vbconst.StorageBus_SAS: u'SAS',
            vbconst.StorageBus_USB: u'USB',
            vbconst.StorageBus_PCIe: u'PCIe'
        }
    if id in _sb_text_cache:
        return _sb_text_cache[id]
    else:
        return u'(Unknown)'
