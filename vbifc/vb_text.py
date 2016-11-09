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
import vb_enum

def format_size(size):
    if size < 1024:
        return u'{} B'.format(size)
    elif size < 1024**2:
        return u'{:.2f} KiB'.format(size / 1024.0)
    elif size < 1024**3:
        return u'{:.2f} MiB'.format(size / float(1024**2))
    elif size < 1024**4:
        return u'{:.2f} GiB'.format(size / float(1024**3))
    elif size < 1024**5:
        return u'{:.2f} TiB'.format(size / float(1024**4))
    else:
        return u'{:.2f} PiB'.format(size / float(1024**5))

def get_os_type(machine):
    vbox = VBoxWrapper()
    os_type = vbox.vbox.getGuestOSType(machine.OSTypeId)
    if os_type is None:
        return u'Unknown'
    return os_type.description

def get_boot_order(machine):
    vbox = VBoxWrapper()
    maxBootOrder = vbox.systemProperties.maxBootPosition
    text = []
    for i in range(maxBootOrder):
        devname = vb_enum.DeviceType_text(machine.getBootOrder(i + 1))
        if devname != u'':
            text.append(devname)
    return u', '.join(text)

def get_accel_summary(machine):
    vbox = VBoxWrapper()
    vbconst = VBoxConstants()
    desc = []
    if vbox.host.getProcessorFeature(vbconst.ProcessorFeature_HWVirtEx):
        if machine.getHWVirtExProperty(vbconst.HWVirtExPropertyType_Enabled):
            desc.append(u'VT-x/AMD-V')
            if machine.getHWVirtExProperty(vbconst.HWVirtExPropertyType_NestedPaging):
                desc.append(u'Nested Paging')
    if machine.getCPUProperty(vbconst.CPUPropertyType_PAE):
        desc.append(u'PAE/NX')
    pvirt = vb_enum.ParavirtProvider_text(machine.getEffectiveParavirtProvider())
    if pvirt != u'':
        desc.append(u'{} Paravirtualization'.format(pvirt))
    return u', '.join(desc)

def get_storage_slot_name(bus, port, device):
    vbconst = VBoxConstants()
    text = vb_enum.StorageBus_text(bus)
    if bus == vbconst.StorageBus_IDE:
        if port == 0:
            text += u' Primary'
        elif port == 1:
            text += u' Secondary'
        else:
            text += u' <invalid>'
        if device == 0:
            text += u' Master'
        elif device == 1:
            text += u' Slave'
        else:
            text += u' <invalid>'
    elif bus == vbconst.StorageBus_Floppy:
        text += u' Device {}'.format(device)
    else:
        text += u' Port {}'.format(port)
    return text

def get_attachment_desc(attachment):
    vbconst = VBoxConstants()
    if attachment.type == vbconst.DeviceType_DVD:
        text = u'[Optical Drive] '
    else:
        text = u''

    # TODO:  The Qt client enumerates all media and looks at the root
    # medium for details -- here we just look at the directly referenced
    # medium (which may be snapshotted, etc)
    medium = attachment.medium
    if medium is None:
        return text + u'Empty'

    if medium.hostDrive:
        if medium.description == u'':
            text += u"Host Drive '{}'".format(medium.location)
        else:
            text += u'Host Drive {} ({})'.format(medium.description, medium.name)
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
            details.append(u'Encrypted')

    mstate = medium.state
    if mstate == vbconst.MediumState_NotCreated:
        details.append(u'Checking...')
    elif mstate == vbconst.MediumState_Inaccessible:
        details.append(u'Inaccessible')
    elif devType == vbconst.DeviceType_HardDisk:
        details.append(format_size(medium.logicalSize))
    else:
        details.append(format_size(medium.size))
    return u'{} ({})'.format(text, u', '.join(details))

def get_network_adapter_desc(adapter):
    if not adapter.enabled:
        return u''

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
            details.append(u'{}={}'.format(names[i], props[i]))
    elif at_type == vbconst.NetworkAttachmentType_NATNetwork:
        details.append(adapter.NATNetwork)

    return u'{} ({})'.format(text, u', '.join(details))

def serial_port_name(port):
    if port.IRQ == 4 and port.IOBase == 0x3f8:
        return u'COM1'
    if port.IRQ == 3 and port.IOBase == 0x2f8:
        return u'COM2'
    if port.IRQ == 4 and port.IOBase == 0x3e8:
        return u'COM3'
    if port.IRQ == 3 and port.IOBase == 0x2e8:
        return u'COM4'
    return u'Custom (I {}; A 0x{:X})'.format(port.IRQ, port.IOBase)

def parallel_port_name(port):
    if port.IRQ == 7 and port.IOBase == 0x378:
        return u'LPT1'
    if port.IRQ == 5 and port.IOBase == 0x278:
        return u'LPT2'
    if port.IRQ == 2 and port.IOBase == 0x3bc:
        return u'LPT1'
    return u'Custom (I {}; A 0x{:X})'.format(port.IRQ, port.IOBase)
