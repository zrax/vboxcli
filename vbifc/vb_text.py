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

from . import VBoxWrapper
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
    desc = []
    if vbox.host.getProcessorFeature(vbox.constants.ProcessorFeature_HWVirtEx):
        if machine.getHWVirtExProperty(vbox.constants.HWVirtExPropertyType_Enabled):
            desc.append(u'VT-x/AMD-V')
            if machine.getHWVirtExProperty(vbox.constants.HWVirtExPropertyType_NestedPaging):
                desc.append(u'Nested Paging')
    if machine.getCPUProperty(vbox.constants.CPUPropertyType_PAE):
        desc.append(u'PAE/NX')
    pvirt = vb_enum.ParavirtProvider_text(machine.getEffectiveParavirtProvider())
    if pvirt != u'':
        desc.append(u'{} Paravirtualization'.format(pvirt))
    return u', '.join(desc)

def get_storage_slot_name(bus, port, device):
    vbox = VBoxWrapper()
    text = vb_enum.StorageBus_text(bus)
    if bus == vbox.constants.StorageBus_IDE:
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
    elif bus == vbox.constants.StorageBus_Floppy:
        text += u' Device {}'.format(device)
    else:
        text += u' Port {}'.format(port)
    return text

def get_attachment_desc(attachment):
    vbox = VBoxWrapper()
    if attachment.type == vbox.constants.DeviceType_DVD:
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
    if medium.deviceType == vbox.constants.DeviceType_HardDisk:
        details.append(vb_enum.MediumType_text(medium.type))
        try:
            medium.getEncryptionSettings()
            encrypted = True
        except:
            encrypted = False
        if encrypted:
            details.append(u'Encrypted')

    if medium.state == vbox.constants.MediumState_NotCreated:
        details.append(u'Checking...')
    elif medium.state == vbox.constants.MediumState_Inaccessible:
        details.append(u'Inaccessible')
    elif medium.deviceType == vbox.constants.DeviceType_HardDisk:
        details.append(format_size(medium.logicalSize))
    else:
        details.append(format_size(medium.size))
    return u'{} ({})'.format(text, u', '.join(details))
