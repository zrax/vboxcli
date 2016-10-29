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

    def add_info_group(self, header, lines, left_pad=2):
        if len(lines) == 0:
            return
        if header is not None:
            self.add_header(header)
        head_width = 0
        for ln in lines:
            ln_width = len(ln[0])
            if ln_width > head_width:
                head_width = ln_width
        for ln in lines:
            self.add_info(ln[0], ln[1], head_width, left_pad)

    def add_text(self, value, left_pad=2):
        self.info.append(urwid.Padding(urwid.Text(value), left=left_pad))

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

        self.add_info_group(u'General', [
            (u'Name', machine.name),
            (u'ID', machine.id),
            (u'OS', vb_text.get_os_type(machine))
        ])

        system_group = [
            (u'Base Memory', u'{} MiB'.format(machine.memorySize))
        ]
        if machine.CPUCount != 1:
            system_group.append((u'Processors', machine.CPUCount))
        if machine.CPUExecutionCap != 100:
            system_group.append((u'Execution Cap', u'{}%'.format(machine.CPUExecutionCap)))
        system_group.append((u'Boot Order', vb_text.get_boot_order(machine)))
        accel = vb_text.get_accel_summary(machine)
        if accel != u'':
            system_group.append((u'Acceleration', accel))
        self.add_info_group(u'System', system_group)

        display_group = [
            (u'Video Memory', u'{} MiB'.format(machine.VRAMSize))
        ]
        if machine.monitorCount != 1:
            display_group.append((u'Screens', machine.monitorCount))
        if machine.VRDEServer.enabled:
            display_group.append((u'RDP Server Port', machine.VRDEServer.getVRDEProperty(u'TCP/Ports')))
        if machine.videoCaptureEnabled:
            display_group.append((u'Video Capture File', os.path.basename(machine.videoCaptureFile)))
        self.add_info_group(u'Display', display_group)

        storageControllers = vbox.mgr.getArray(machine, 'storageControllers')
        if len(storageControllers) > 0:
            self.add_header(u'Storage')
        for scon in storageControllers:
            self.add_text(u'Controller: {}'.format(scon.name))
            attachments = machine.getMediumAttachmentsOfController(scon.name)
            slot_names = [vb_text.get_storage_slot_name(scon.bus, att.port, att.device)
                          for att in attachments]
            self.add_info_group(None, [
                (slot_names[slot], vb_text.get_attachment_desc(attachments[slot]))
                    for slot in range(len(attachments))], left_pad=4)

        if machine.audioAdapter.enabled:
            audio = machine.audioAdapter
            self.add_info_group(u'Audio', [
                (u'Host Driver', vb_enum.AudioDriverType_text(audio.audioDriver)),
                (u'Controller', vb_enum.AudioControllerType_text(audio.audioController))
            ])

        maxAdapters = vbox.systemProperties.getMaxNetworkAdapters(machine.chipsetType)
        adapter_group = []
        for ad in range(maxAdapters):
            adapter = machine.getNetworkAdapter(ad)
            if not adapter.enabled:
                continue
            desc = vb_text.get_network_adapter_desc(adapter)
            if desc != u'':
                adapter_group.append((u'Adapter {}'.format(adapter.slot + 1), desc))
        self.add_info_group(u'Network', adapter_group)

        maxSerialPorts = vbox.systemProperties.serialPortCount
        serial_group = []
        for sp in range(maxSerialPorts):
            port = machine.getSerialPort(sp)
            if not port.enabled:
                continue
            port_text = u'{}: {}'.format(vb_text.serial_port_name(port),
                                         vb_enum.PortMode_text(port.hostMode))
            if port.hostMode in (vbox.constants.PortMode_HostPipe,
                                 vbox.constants.PortMode_HostDevice,
                                 vbox.constants.PortMode_RawFile,
                                 vbox.constants.PortMode_TCP):
                port_text += u' ({})'.format(port.path)
            serial_group.append((u'Port {}'.format(port.slot + 1), port_text))
        self.add_info_group(u'Serial Ports', serial_group)

        maxParallelPorts = vbox.systemProperties.parallelPortCount
        parallel_group = []
        for pp in range(maxParallelPorts):
            port = machine.getParallelPort(pp)
            if not port.enabled:
                continue
            port_text = u'{} ({})'.format(vb_text.parallel_port_name(port), port.path)
            parallel_group.append((u'Port {}'.format(port.slot + 1), port_text))
        self.add_info_group(u'Parallel Ports', parallel_group)

        usb_filters = machine.USBDeviceFilters
        if usb_filters is not None and machine.USBProxyAvailable:
            usb_group = []
            controllers = vbox.mgr.getArray(machine, 'USBControllers')
            clist = []
            for c in controllers:
                clist.append(c.name)
            if len(clist) > 0:
                usb_group.append((u'USB Controller', u', '.join(clist)))
            else:
                usb_group.append((u'USB Controller', u'Disabled'))
            filt_active = 0
            filters = vbox.mgr.getArray(usb_filters, 'deviceFilters')
            for df in filters:
                if df.active:
                    filt_active += 1
            usb_group.append((u'Device Filters', u'{} ({} active)'.format(len(filters), filt_active)))
            self.add_info_group(u'USB', usb_group)

        sharedFolders = vbox.mgr.getArray(machine, 'sharedFolders')
        sf_group = []
        for sf in sharedFolders:
            details = []
            if not sf.writable:
                details.append(u'Read-Only')
            if sf.autoMount:
                details.append(u'Auto-Mount')
            if len(details) > 0:
                sf_group.append((sf.name, u'{} ({})'.format(sf.hostPath, u', '.join(details))))
            else:
                sf_group.append((sf.name, sf.hostPath))
        self.add_info_group(u'Shared Folders', sf_group)

        if len(machine.description) > 0:
            self.add_header(u'Description')
            self.add_text(('info', machine.description))
