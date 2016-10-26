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

import urwid

from vbifc import VBoxWrapper, vb_enum

class MachineInfo(urwid.LineBox):
    def __init__(self):
        self.info = urwid.SimpleFocusListWalker([])
        super(MachineInfo, self).__init__(urwid.ListBox(self.info), u'Details')
        self.show_machine(None)

    @staticmethod
    def get_os_type(machine):
        vbox = VBoxWrapper()
        os_type = vbox.vbox.getGuestOSType(machine.OSTypeId)
        if os_type is None:
            return u'Unknown'
        return os_type.description

    @staticmethod
    def get_boot_order(machine):
        vbox = VBoxWrapper()
        maxBootOrder = vbox.vbox.systemProperties.maxBootPosition
        text = []
        for i in range(maxBootOrder):
            devname = vb_enum.DeviceType_text(machine.getBootOrder(i + 1))
            if devname != u'':
                text.append(devname)
        return u', '.join(text)

    @staticmethod
    def get_accel_summary(machine):
        # TODO: The Qt UI may also list a (resolved) paravirt backend here
        vbox = VBoxWrapper()
        desc = []
        if machine.getHWVirtExProperty(vbox.constants.HWVirtExPropertyType_Enabled):
            desc.append(u'VT-x/AMD-V')
        if machine.getHWVirtExProperty(vbox.constants.HWVirtExPropertyType_NestedPaging):
            desc.append(u'Nested Paging')
        if machine.getCPUProperty(vbox.constants.CPUPropertyType_PAE):
            desc.append(u'PAE/NX')
        return u', '.join(desc)

    def add_header(self, label, space_before=True):
        if space_before:
            self.info.append(urwid.Divider())
        self.info.append(urwid.Text(('info header', label)))

    def add_info(self, label, value, head_width):
        head = urwid.Padding(urwid.Text(('info key', u'{}:'.format(label))), left=2)
        content = urwid.Text(('info', u'{}'.format(value)))
        columns = urwid.Columns([(head_width + 4, head), content], 1)
        self.info.append(columns)

    def show_machine(self, machine):
        del self.info[:]
        if machine is None:
            self.info.append(urwid.Text(u'No machine selected'))
            return

        self.info.append(urwid.Text([
            ('info key', u'Current State:  '),
            vb_enum.MachineState_icon(machine.state),
            ('info', u' ' + vb_enum.MachineState_text(machine.state))]))

        self.add_header(u'General')
        head_width = len(u'Name')
        self.add_info(u'Name', machine.name, head_width)
        self.add_info(u'ID', machine.id, head_width)
        self.add_info(u'OS', self.get_os_type(machine), head_width)

        self.add_header(u'System')
        head_width = len(u'Acceleration')
        self.add_info(u'Base Memory', u'{} MiB'.format(machine.memorySize), head_width)
        if machine.CPUCount != 1:
            self.add_info(u'Processors', machine.CPUCount, head_width)
        self.add_info(u'Boot Order', self.get_boot_order(machine), head_width)
        self.add_info(u'Acceleration', self.get_accel_summary(machine), head_width)

        self.add_header(u'Display')
        if machine.videoCaptureEnabled:
            head_width = len(u'Video Capture File')
        elif machine.VRDEServer.enabled:
            head_width = len(u'RDP Server Port')
        else:
            head_width = len(u'Video Capture')
        self.add_info(u'Video Memory', u'{} MiB'.format(machine.VRAMSize), head_width)
        if machine.monitorCount != 1:
            self.add_info(u'Screens', machine.monitorCount, head_width)
        if machine.VRDEServer.enabled:
            self.add_info(u'RDP Server Port', machine.VRDEServer.getVRDEProperty(u'TCP/Ports'), head_width)
        else:
            self.add_info(u'RDP Server', u'Disabled', head_width)
        if machine.videoCaptureEnabled:
            self.add_info(u'Video Capture File', machine.videoCaptureFile, head_width)
        else:
            self.add_info(u'Video Capture', u'Disabled', head_width)
