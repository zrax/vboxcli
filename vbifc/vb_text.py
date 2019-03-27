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

from . import VBoxWrapper, VBoxConstants
from . import vb_enum

def format_size(size):
    if size < 1024:
        return '{} B'.format(size)
    elif size < 1024**2:
        return '{:.2f} KiB'.format(size / 1024.0)
    elif size < 1024**3:
        return '{:.2f} MiB'.format(size / float(1024**2))
    elif size < 1024**4:
        return '{:.2f} GiB'.format(size / float(1024**3))
    elif size < 1024**5:
        return '{:.2f} TiB'.format(size / float(1024**4))
    else:
        return '{:.2f} PiB'.format(size / float(1024**5))

def get_os_type(machine):
    vbox = VBoxWrapper()
    os_type = vbox.vbox.getGuestOSType(machine.OSTypeId)
    if os_type is None:
        return _('Unknown')
    return os_type.description

def get_boot_order(machine):
    vbox = VBoxWrapper()
    maxBootOrder = vbox.systemProperties.maxBootPosition
    text = []
    for i in range(maxBootOrder):
        devname = vb_enum.DeviceType_text(machine.getBootOrder(i + 1))
        if devname != '':
            text.append(devname)
    return ', '.join(text)

def get_accel_summary(machine):
    vbox = VBoxWrapper()
    vbconst = VBoxConstants()
    desc = []
    if vbox.host.getProcessorFeature(vbconst.ProcessorFeature_HWVirtEx):
        if machine.getHWVirtExProperty(vbconst.HWVirtExPropertyType_Enabled):
            desc.append(_('VT-x/AMD-V'))
            if machine.getHWVirtExProperty(vbconst.HWVirtExPropertyType_NestedPaging):
                desc.append(_('Nested Paging'))
    if machine.getCPUProperty(vbconst.CPUPropertyType_PAE):
        desc.append(_('PAE/NX'))
    pvirt = vb_enum.ParavirtProvider_text(machine.getEffectiveParavirtProvider())
    if pvirt != '':
        desc.append(_('{} Paravirtualization').format(pvirt))
    return ', '.join(desc)

def get_storage_slot_name(bus, port, device):
    vbconst = VBoxConstants()
    text = [vb_enum.StorageBus_text(bus)]
    if bus == vbconst.StorageBus_IDE:
        if port == 0:
            text.append(_('Primary'))
        elif port == 1:
            text.append(_('Secondary'))
        else:
            text.append(_('<invalid>'))
        if device == 0:
            text.append(_('Master'))
        elif device == 1:
            text.append(_('Slave'))
        else:
            text.append(_('<invalid>'))
    elif bus == vbconst.StorageBus_Floppy:
        text.append(_('Device {}').format(device))
    else:
        text.append(_('Port {}').format(port))
    return ' '.join(text)

def get_attachment_desc(attachment):
    vbconst = VBoxConstants()
    if attachment.type == vbconst.DeviceType_DVD:
        text = _('[Optical Drive]') + ' '
    else:
        text = ''

    # TODO:  The Qt client enumerates all media and looks at the root
    # medium for details -- here we just look at the directly referenced
    # medium (which may be snapshotted, etc)
    medium = attachment.medium
    if medium is None:
        return text + _('Empty')

    if medium.hostDrive:
        if medium.description == '':
            text += _("Host Drive '{}'").format(medium.location)
        else:
            text += _('Host Drive {} ({})').format(medium.description, medium.name)
        return text

    text += medium.name
    details = []
    devType = medium.deviceType
    if devType == vbconst.DeviceType_HardDisk:
        details.append(vb_enum.MediumType_text(medium.type))
        try:
            medium.getEncryptionSettings()
            encrypted = True
        except:
            encrypted = False
        if encrypted:
            details.append(_('Encrypted'))

    mstate = medium.state
    if mstate == vbconst.MediumState_NotCreated:
        details.append(_('Checking...'))
    elif mstate == vbconst.MediumState_Inaccessible:
        details.append(_('Inaccessible'))
    elif devType == vbconst.DeviceType_HardDisk:
        details.append(format_size(medium.logicalSize))
    else:
        details.append(format_size(medium.size))
    return '{} ({})'.format(text, ', '.join(details))

def get_network_adapter_desc(adapter):
    if not adapter.enabled:
        return ''

    vbconst = VBoxConstants()
    text = vb_enum.NetworkAdapterType_text(adapter.adapterType)
    at_type = adapter.attachmentType
    details = [vb_enum.NetworkAttachmentType_text(at_type)]
    if at_type == vbconst.NetworkAttachmentType_Bridged:
        details.append(adapter.bridgedInterface)
    elif at_type == vbconst.NetworkAttachmentType_Internal:
        details.append(adapter.internalNetwork)
    elif at_type == vbconst.NetworkAttachmentType_Internal:
        details.append(adapter.hostOnlyInterface)
    elif at_type == vbconst.NetworkAttachmentType_Generic:
        details.append(adapter.genericDriver)
        names, props = adapter.getProperties(None)
        for i in range(len(names)):
            details.append('{}={}'.format(names[i], props[i]))
    elif at_type == vbconst.NetworkAttachmentType_NATNetwork:
        details.append(adapter.NATNetwork)

    return '{} ({})'.format(text, ', '.join(details))

def serial_port_name(port):
    if port.IRQ == 4 and port.IOBase == 0x3f8:
        return _('COM1')
    if port.IRQ == 3 and port.IOBase == 0x2f8:
        return _('COM2')
    if port.IRQ == 4 and port.IOBase == 0x3e8:
        return _('COM3')
    if port.IRQ == 3 and port.IOBase == 0x2e8:
        return _('COM4')
    return _('Custom (I {}; A 0x{:X})').format(port.IRQ, port.IOBase)

def parallel_port_name(port):
    if port.IRQ == 7 and port.IOBase == 0x378:
        return _('LPT1')
    if port.IRQ == 5 and port.IOBase == 0x278:
        return _('LPT2')
    if port.IRQ == 2 and port.IOBase == 0x3bc:
        return _('LPT1')
    return _('Custom (I {}; A 0x{:X})').format(port.IRQ, port.IOBase)
