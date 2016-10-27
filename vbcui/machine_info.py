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

        storageControllers = vbox.mgr.getArray(machine, 'storageControllers')
        if len(storageControllers) > 0:
            self.add_header(u'Storage')
        for scon in storageControllers:
            self.add_text(u'Controller: {}'.format(scon.name))
            attachments = machine.getMediumAttachmentsOfController(scon.name)
            slot_names = [vb_text.get_storage_slot_name(scon.bus, att.port, att.device)
                          for att in attachments]
            head_width = len(max(slot_names, key=len))
            for slot in range(len(attachments)):
                self.add_info(slot_names[slot], vb_text.get_attachment_desc(attachments[slot]),
                              head_width, left_pad=4)

        if machine.audioAdapter.enabled:
            self.add_header(u'Audio')
            head_width = len(u'Host Driver')
            audio = machine.audioAdapter
            self.add_info(u'Host Driver', vb_enum.AudioDriverType_text(audio.audioDriver), head_width)
            self.add_info(u'Controller', vb_enum.AudioControllerType_text(audio.audioController), head_width)

        maxAdapters = vbox.systemProperties.getMaxNetworkAdapters(machine.chipsetType)
        adapter_info = []
        for ad in range(maxAdapters):
            adapter = machine.getNetworkAdapter(ad)
            if not adapter.enabled:
                continue
            desc = vb_text.get_network_adapter_desc(adapter)
            if desc != u'':
                adapter_info.append((adapter.slot, desc))
        if len(adapter_info) > 0:
            self.add_header(u'Network')
            head_width = len(u'Adapter 1')
            if len(adapter_info) > 9:
                head_width += 1
            for adi in adapter_info:
                slot, desc = adi
                self.add_info(u'Adapter {}'.format(slot + 1), desc, head_width)

        maxSerialPorts = vbox.systemProperties.serialPortCount
        serial_info = []
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
            serial_info.append((port.slot, port_text))
        if len(serial_info) > 0:
            self.add_header(u'Serial Ports')
            head_width = len(u'Port 1')
            for si in serial_info:
                slot, port = si
                slot.add_info(u'Port {}'.format(slot + 1), port, head_width)

        maxParallelPorts = vbox.systemProperties.parallelPortCount
        parallel_info = []
        for pp in range(maxParallelPorts):
            port = machine.getParallelPort(pp)
            if not port.enabled:
                continue
            port_text = u'{} ({})'.format(vb_text.parallel_port_name(port), port.path)
            parallel_info.append((port.slot, port_text))
        if len(parallel_info) > 0:
            self.add_header(u'Parallel Ports')
            head_width = len(u'Port 1')
            for pi in parallel_info:
                slot, port = pi
                slot.add_info(u'Port {}'.format(slot + 1), port, head_width)

        usb_filters = machine.USBDeviceFilters
        if usb_filters is not None and machine.USBProxyAvailable:
            self.add_header(u'USB')
            controllers = vbox.mgr.getArray(machine, 'USBControllers')
            clist = []
            for c in controllers:
                clist.append(c.name)
            head_width = len(u'USB Controller')
            if len(clist) > 0:
                self.add_info(u'USB Controller', u', '.join(clist), head_width)
            else:
                self.add_info(u'USB Controller', u'Disabled', head_width)
            filt_active = 0
            filters = vbox.mgr.getArray(usb_filters, 'deviceFilters')
            for df in filters:
                if df.active:
                    filt_active += 1
            self.add_info(u'Device Filters', u'{} ({} active)'.format(len(filters), filt_active), head_width)

        sharedFolders = vbox.mgr.getArray(machine, 'sharedFolders')
        if len(sharedFolders) > 0:
            self.add_header(u'Shared Folders')
            head_width = 0
            for sf in sharedFolders:
                if len(sf.name) > head_width:
                    head_width = len(sf.name)
            for sf in sharedFolders:
                details = []
                if not sf.writable:
                    details.append(u'Read-Only')
                if sf.autoMount:
                    details.append(u'Auto-Mount')
                if len(details) > 0:
                    self.add_info(sf.name, u'{} ({})'.format(sf.hostPath, u', '.join(details)), head_width)
                else:
                    self.add_info(sf.name, sf.hostPath, head_width)

        if len(machine.description) > 0:
            self.add_header(u'Description')
            self.add_text(('info', machine.description))
