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
            vbconst.AudioControllerType_AC97: _('ICH AC97'),
            vbconst.AudioControllerType_SB16: _('SoundBlaster 16'),
            vbconst.AudioControllerType_HDA: _('Intel HD Audio')
        }
    if id in _ac_text_cache:
        return _ac_text_cache[id]
    else:
        return _('(Unknown)')

_ad_text_cache = None
def AudioDriverType_text(id):
    global _ad_text_cache
    if _ad_text_cache is None:
        vbconst = VBoxConstants()
        _ad_text_cache = {
            vbconst.AudioDriverType_Null: _('Dummy'),
            vbconst.AudioDriverType_WinMM: _('Windows Multimedia'),
            vbconst.AudioDriverType_OSS: _('OSS'),
            vbconst.AudioDriverType_ALSA: _('ALSA'),
            vbconst.AudioDriverType_DirectSound: _('DirectSound'),
            vbconst.AudioDriverType_CoreAudio: _('CoreAudio'),
            vbconst.AudioDriverType_Pulse: _('PulseAudio'),
            vbconst.AudioDriverType_SolAudio: _('Solaris Audio')
        }
    if id in _ad_text_cache:
        return _ad_text_cache[id]
    else:
        return _('(Unknown)')

_dt_text_cache = None
def DeviceType_text(id):
    global _dt_text_cache
    if _dt_text_cache is None:
        vbconst = VBoxConstants()
        _dt_text_cache = {
            vbconst.DeviceType_Null: '',
            vbconst.DeviceType_Floppy: _('Floppy'),
            vbconst.DeviceType_DVD: _('Optical'),
            vbconst.DeviceType_HardDisk: _('Hard Disk'),
            vbconst.DeviceType_Network: _('Network'),
            vbconst.DeviceType_USB: _('USB'),
            vbconst.DeviceType_SharedFolder: _('Shared Folder'),
            vbconst.DeviceType_Graphics3D: _('3D Graphics')
        }
    if id in _dt_text_cache:
        return _dt_text_cache[id]
    else:
        return _('(Unknown)')

_ms_text_cache = None
def MachineState_text(id):
    global _ms_text_cache
    if _ms_text_cache is None:
        vbconst = VBoxConstants()
        _ms_text_cache = {
            vbconst.MachineState_Null: _('<Invalid>'),
            vbconst.MachineState_PoweredOff: _('Powered Off'),
            vbconst.MachineState_Saved: _('Saved'),
            vbconst.MachineState_Teleported: _('Teleported'),
            vbconst.MachineState_Aborted: _('Aborted'),
            vbconst.MachineState_Running: _('Running'),
            vbconst.MachineState_Paused: _('Paused'),
            vbconst.MachineState_Stuck: _('Guru Meditation'),
            vbconst.MachineState_Teleporting: _('Teleporting'),
            vbconst.MachineState_LiveSnapshotting: _('Creating Snapshot (Online)'),
            vbconst.MachineState_Starting: _('Starting'),
            vbconst.MachineState_Stopping: _('Stopping'),
            vbconst.MachineState_Saving: _('Saving'),
            vbconst.MachineState_Restoring: _('Restoring'),
            vbconst.MachineState_TeleportingPausedVM: _('Teleporting (Paused)'),
            vbconst.MachineState_TeleportingIn: _('Teleporting In'),
            vbconst.MachineState_FaultTolerantSyncing: _('Syncing'),
            vbconst.MachineState_DeletingSnapshotOnline: _('Deleting Snapshot (Online)'),
            vbconst.MachineState_DeletingSnapshotPaused: _('Deleting Snapshot (Paused)'),
            vbconst.MachineState_OnlineSnapshotting: _('Creating Snapshot (Online)'),
            vbconst.MachineState_RestoringSnapshot: _('Restoring Snapshot'),
            vbconst.MachineState_DeletingSnapshot: _('Deleting Snapshot'),
            vbconst.MachineState_SettingUp: _('Configuring'),
            vbconst.MachineState_Snapshotting: _('Creating Snapshot')
        }
    if id in _ms_text_cache:
        return _ms_text_cache[id]
    else:
        return _('(Unknown)')

_ms_icon_cache = None
def MachineState_icon(id):
    global _ms_icon_cache
    if _ms_icon_cache is None:
        vbconst = VBoxConstants()
        _ms_icon_cache = {
            # There may be better unicode symbols available, but these are
            # ones I found to work even in older/limited terminal fonts.
            vbconst.MachineState_Null: ('state error', '?'),
            vbconst.MachineState_PoweredOff: ('state off', '\u25a0'),
            vbconst.MachineState_Saved: ('state off', '\u25c9'),
            vbconst.MachineState_Teleported: ('state off', 'T'),
            vbconst.MachineState_Aborted: ('state error', '!'),
            vbconst.MachineState_Running: ('state run', '\u25b6'),
            vbconst.MachineState_Paused: ('state pause', '\u2225'),
            vbconst.MachineState_Stuck: ('state error', '!'),
            vbconst.MachineState_Teleporting: ('state on', 'T'),
            vbconst.MachineState_LiveSnapshotting: ('state on', 'S'),
            vbconst.MachineState_Starting: ('state on', '\u25a0'),
            vbconst.MachineState_Stopping: ('state pause', '\u25a0'),
            vbconst.MachineState_Saving: ('state pause', '\u25d4'),
            vbconst.MachineState_Restoring: ('state pause', '\u25d4'),
            vbconst.MachineState_TeleportingPausedVM: ('state pause', 'T'),
            vbconst.MachineState_TeleportingIn: ('state off', 'T'),
            vbconst.MachineState_FaultTolerantSyncing: ('state run', '\u25e9'),
            vbconst.MachineState_DeletingSnapshotOnline: ('state run', 'D'),
            vbconst.MachineState_DeletingSnapshotPaused: ('state pause', 'D'),
            vbconst.MachineState_OnlineSnapshotting: ('state pause', 'S'),
            vbconst.MachineState_RestoringSnapshot: ('state off', 'R'),
            vbconst.MachineState_DeletingSnapshot: ('state off', 'D'),
            vbconst.MachineState_SettingUp: ('state off', '\u25a0'),
            vbconst.MachineState_Snapshotting: ('state off', 'S')
        }
    if id in _ms_icon_cache:
        return _ms_icon_cache[id]
    else:
        return ('state error', '?')

_mt_text_cache = None
def MediumType_text(id):
    global _mt_text_cache
    if _mt_text_cache is None:
        vbconst = VBoxConstants()
        _mt_text_cache = {
            vbconst.MediumType_Normal: _('Normal'),
            vbconst.MediumType_Immutable: _('Immutable'),
            vbconst.MediumType_Writethrough: _('Writethrough'),
            vbconst.MediumType_Shareable: _('Shareable'),
            vbconst.MediumType_Readonly: _('Read-Only'),
            vbconst.MediumType_MultiAttach: _('Multi-Attach')
        }
    if id in _mt_text_cache:
        return _mt_text_cache[id]
    else:
        return _('(Unknown)')

_nadt_text_cache = None
def NetworkAdapterType_text(id):
    global _nadt_text_cache
    if _nadt_text_cache is None:
        vbconst = VBoxConstants()
        _nadt_text_cache = {
            vbconst.NetworkAdapterType_Null: _('<Invalid>'),
            vbconst.NetworkAdapterType_Am79C970A: _('AMD PCNet-PCI II'),
            vbconst.NetworkAdapterType_Am79C973: _('AMD PCNet-FAST III'),
            vbconst.NetworkAdapterType_I82540EM: _('Intel PRO/1000 MT Desktop'),
            vbconst.NetworkAdapterType_I82543GC: _('Intel PRO/1000 T Server'),
            vbconst.NetworkAdapterType_I82545EM: _('Intel PRO/1000 MT Server'),
            vbconst.NetworkAdapterType_Virtio: _('Paravirtualized')
        }
    if id in _nadt_text_cache:
        return _nadt_text_cache[id]
    else:
        return _('(Unknown)')

_natt_text_cache = None
def NetworkAttachmentType_text(id):
    global _natt_text_cache
    if _natt_text_cache is None:
        vbconst = VBoxConstants()
        _natt_text_cache = {
            vbconst.NetworkAttachmentType_Null: '',
            vbconst.NetworkAttachmentType_NAT: _('NAT'),
            vbconst.NetworkAttachmentType_Bridged: _('Bridged'),
            vbconst.NetworkAttachmentType_Internal: _('Internal'),
            vbconst.NetworkAttachmentType_HostOnly: _('Host-Only'),
            vbconst.NetworkAttachmentType_Generic: _('Generic'),
            vbconst.NetworkAttachmentType_NATNetwork: _('NAT Network')
        }
    if id in _natt_text_cache:
        return _natt_text_cache[id]
    else:
        return _('(Unknown)')

_pvp_text_cache = None
def ParavirtProvider_text(id):
    global _pvp_text_cache
    if _pvp_text_cache is None:
        vbconst = VBoxConstants()
        _pvp_text_cache = {
            vbconst.ParavirtProvider_None: '',
            vbconst.ParavirtProvider_Default: _('Default'),
            vbconst.ParavirtProvider_Legacy: _('Legacy'),
            vbconst.ParavirtProvider_Minimal: _('Minimal'),
            vbconst.ParavirtProvider_HyperV: _('Hyper-V'),
            vbconst.ParavirtProvider_KVM: _('KVM')
        }
    if id in _pvp_text_cache:
        return _pvp_text_cache[id]
    else:
        return _('(Unknown)')

_pm_text_cache = None
def PortMode_text(id):
    global _pm_text_cache
    if _pm_text_cache is None:
        vbconst = VBoxConstants()
        _pm_text_cache = {
            vbconst.PortMode_Disconnected: _('Disconnected'),
            vbconst.PortMode_HostPipe: _('Host Pipe'),
            vbconst.PortMode_HostDevice: _('Host Device'),
            vbconst.PortMode_RawFile: _('Raw File'),
            vbconst.PortMode_TCP: _('TCP Socket')
        }
    if id in _pm_text_cache:
        return _pm_text_cache[id]
    else:
        return _('(Unknown)')

_sb_text_cache = None
def StorageBus_text(id):
    global _sb_text_cache
    if _sb_text_cache is None:
        vbconst = VBoxConstants()
        _sb_text_cache = {
            vbconst.StorageBus_Null: _('<invalid>'),
            vbconst.StorageBus_IDE: _('IDE'),
            vbconst.StorageBus_SATA: _('SATA'),
            vbconst.StorageBus_SCSI: _('SCSI'),
            vbconst.StorageBus_Floppy: _('Floppy'),
            vbconst.StorageBus_SAS: _('SAS'),
            vbconst.StorageBus_USB: _('USB'),
            vbconst.StorageBus_PCIe: _('PCIe')
        }
    if id in _sb_text_cache:
        return _sb_text_cache[id]
    else:
        return _('(Unknown)')
