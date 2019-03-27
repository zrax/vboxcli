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
        super(MachineInfo, self).__init__(urwid.ListBox(self.info), _('Details'))
        self.show_machine(None)

    def add_header(self, label, space_before=True):
        if space_before:
            self.info.append(urwid.Divider())
        self.info.append(urwid.Text(('info header', label)))

    def add_info(self, label, value, head_width, left_pad=2):
        head = urwid.Padding(urwid.Text(('info key', '{}:'.format(label))),
                             left=left_pad)
        content = urwid.Text(('info', '{}'.format(value)))
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
            self.info.append(urwid.Text(_('No machine selected')))
            return

        if not machine.accessible:
            self.info.append(urwid.Text(('info error', _('Machine details inaccessible'))))
            return

        vbox = VBoxWrapper()
        self.info.append(urwid.Text([
            ('info key', _('Current State:  ')),
            vb_enum.MachineState_icon(machine.state),
            ('info', ' ' + vb_enum.MachineState_text(machine.state))]))

        self.add_info_group(_('General'), [
            (_('Name'), machine.name),
            (_('ID'), machine.id),
            (_('OS'), vb_text.get_os_type(machine))
        ])

        system_group = [
            (_('Base Memory'), '{} MiB'.format(machine.memorySize))
        ]
        if machine.CPUCount != 1:
            system_group.append((_('Processors'), machine.CPUCount))
        if machine.CPUExecutionCap != 100:
            system_group.append((_('Execution Cap'), '{}%'.format(machine.CPUExecutionCap)))
        system_group.append((_('Boot Order'), vb_text.get_boot_order(machine)))
        accel = vb_text.get_accel_summary(machine)
        if accel != '':
            system_group.append((_('Acceleration'), accel))
        self.add_info_group(_('System'), system_group)

        display_group = [
            (_('Video Memory'), '{} MiB'.format(machine.VRAMSize))
        ]
        if machine.monitorCount != 1:
            display_group.append((_('Screens'), machine.monitorCount))
        if machine.VRDEServer.enabled:
            display_group.append((_('RDP Server Port'),
                                  machine.VRDEServer.getVRDEProperty('TCP/Ports')))
        if machine.videoCaptureEnabled:
            display_group.append((_('Video Capture File'),
                                  os.path.basename(machine.videoCaptureFile)))
        self.add_info_group(_('Display'), display_group)

        storageControllers = vbox.mgr.getArray(machine, 'storageControllers')
        if len(storageControllers) > 0:
            self.add_header(_('Storage'))
        for scon in storageControllers:
            self.add_text(_('Controller: {}').format(scon.name))
            attachments = machine.getMediumAttachmentsOfController(scon.name)
            slot_names = [vb_text.get_storage_slot_name(scon.bus, att.port, att.device)
                          for att in attachments]
            self.add_info_group(None, [
                (slot_names[slot], vb_text.get_attachment_desc(attachments[slot]))
                    for slot in range(len(attachments))], left_pad=4)

        if machine.audioAdapter.enabled:
            audio = machine.audioAdapter
            self.add_info_group(_('Audio'), [
                (_('Host Driver'), vb_enum.AudioDriverType_text(audio.audioDriver)),
                (_('Controller'), vb_enum.AudioControllerType_text(audio.audioController))
            ])

        maxAdapters = vbox.systemProperties.getMaxNetworkAdapters(machine.chipsetType)
        adapter_group = []
        for ad in range(maxAdapters):
            adapter = machine.getNetworkAdapter(ad)
            if not adapter.enabled:
                continue
            desc = vb_text.get_network_adapter_desc(adapter)
            if desc != '':
                adapter_group.append((_('Adapter {}').format(adapter.slot + 1), desc))
        self.add_info_group(_('Network'), adapter_group)

        maxSerialPorts = vbox.systemProperties.serialPortCount
        serial_group = []
        for sp in range(maxSerialPorts):
            port = machine.getSerialPort(sp)
            if not port.enabled:
                continue
            port_text = '{}: {}'.format(vb_text.serial_port_name(port),
                                         vb_enum.PortMode_text(port.hostMode))
            if port.hostMode in {vbox.constants.PortMode_HostPipe,
                                 vbox.constants.PortMode_HostDevice,
                                 vbox.constants.PortMode_RawFile,
                                 vbox.constants.PortMode_TCP}:
                port_text += ' ({})'.format(port.path)
            serial_group.append((_('Port {}').format(port.slot + 1), port_text))
        self.add_info_group(_('Serial Ports'), serial_group)

        maxParallelPorts = vbox.systemProperties.parallelPortCount
        parallel_group = []
        for pp in range(maxParallelPorts):
            port = machine.getParallelPort(pp)
            if not port.enabled:
                continue
            port_text = '{} ({})'.format(vb_text.parallel_port_name(port), port.path)
            parallel_group.append((_('Port {}').format(port.slot + 1), port_text))
        self.add_info_group(_('Parallel Ports'), parallel_group)

        usb_filters = machine.USBDeviceFilters
        if usb_filters is not None and machine.USBProxyAvailable:
            usb_group = []
            controllers = vbox.mgr.getArray(machine, 'USBControllers')
            clist = []
            for c in controllers:
                clist.append(c.name)
            if len(clist) > 0:
                usb_group.append((_('USB Controller'), ', '.join(clist)))
            else:
                usb_group.append((_('USB Controller'), _('Disabled')))
            filt_active = 0
            filters = vbox.mgr.getArray(usb_filters, 'deviceFilters')
            for df in filters:
                if df.active:
                    filt_active += 1
            usb_group.append((_('Device Filters'), _('{} ({} active)').format(len(filters), filt_active)))
            self.add_info_group(_('USB'), usb_group)

        sharedFolders = vbox.mgr.getArray(machine, 'sharedFolders')
        sf_group = []
        for sf in sharedFolders:
            details = []
            if not sf.writable:
                details.append(_('Read-Only'))
            if sf.autoMount:
                details.append(_('Auto-Mount'))
            if len(details) > 0:
                sf_group.append((sf.name, '{} ({})'.format(sf.hostPath, ', '.join(details))))
            else:
                sf_group.append((sf.name, sf.hostPath))
        self.add_info_group(_('Shared Folders'), sf_group)

        if len(machine.description) > 0:
            self.add_header(_('Description'))
            self.add_text(('info', machine.description))
