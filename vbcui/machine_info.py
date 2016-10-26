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

import os
import urwid

from vbifc import VBoxWrapper, vb_enum, vb_text

class MachineInfo(urwid.LineBox):
    def __init__(self):
        self.info = urwid.SimpleFocusListWalker([])
        super(MachineInfo, self).__init__(urwid.ListBox(self.info), u'Details')
        self.show_machine(None)

    def add_header(self, label, space_before=True):
        if space_before:
            self.info.append(urwid.Divider())
        self.info.append(urwid.Text(('info header', label)))

    def add_info(self, label, value, head_width, left_pad=2):
        head = urwid.Padding(urwid.Text(('info key', u'{}:'.format(label))),
                             left=left_pad)
        content = urwid.Text(('info', u'{}'.format(value)))
        columns = urwid.Columns([(head_width + 2 + left_pad, head), content], 1)
        self.info.append(columns)

    def show_machine(self, machine):
        del self.info[:]
        if machine is None:
            self.info.append(urwid.Text(u'No machine selected'))
            return

        if not machine.accessible:
            self.info.append(urwid.Text(('info error', u'Machine details inaccessible')))
            return

        vbox = VBoxWrapper()
        self.info.append(urwid.Text([
            ('info key', u'Current State:  '),
            vb_enum.MachineState_icon(machine.state),
            ('info', u' ' + vb_enum.MachineState_text(machine.state))]))

        self.add_header(u'General')
        head_width = len(u'Name')
        self.add_info(u'Name', machine.name, head_width)
        self.add_info(u'ID', machine.id, head_width)
        self.add_info(u'OS', vb_text.get_os_type(machine), head_width)

        self.add_header(u'System')
        if machine.CPUExecutionCap != 100:
            head_width = len(u'Execution Cap')
        else:
            head_width = len(u'Acceleration')
        self.add_info(u'Base Memory', u'{} MiB'.format(machine.memorySize), head_width)
        if machine.CPUCount != 1:
            self.add_info(u'Processors', machine.CPUCount, head_width)
        if machine.CPUExecutionCap != 100:
            self.add_info(u'Execution Cap', u'{}%'.format(machine.CPUExecutionCap), head_width)
        self.add_info(u'Boot Order', vb_text.get_boot_order(machine), head_width)
        accel = vb_text.get_accel_summary(machine)
        if accel != u'':
            self.add_info(u'Acceleration', accel, head_width)

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
            self.add_info(u'Video Capture File', os.path.basename(machine.videoCaptureFile), head_width)
        else:
            self.add_info(u'Video Capture', u'Disabled', head_width)

        self.add_header(u'Storage')
        storageControllers = vbox.mgr.getArray(machine, 'storageControllers')
        for scon in storageControllers:
            self.info.append(urwid.Padding(urwid.Text(u'Controller: {}'.format(scon.name)), left=2))
            attachments = machine.getMediumAttachmentsOfController(scon.name)
            slot_names = [vb_text.get_storage_slot_name(scon.bus, att.port, att.device)
                          for att in attachments]
            head_width = len(max(slot_names, key=len))
            for slot in range(len(attachments)):
                self.add_info(slot_names[slot], vb_text.get_attachment_desc(attachments[slot]),
                              head_width, left_pad=4)
