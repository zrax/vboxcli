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

import machine_list
import machine_info

class TopUI(urwid.Frame):
    def __init__(self):
        self.mach_list = machine_list.MachineList()
        self.mach_info = machine_info.MachineInfo()
        columns = urwid.Columns([
            ('weight', 1, self.mach_list),
            ('weight', 2, self.mach_info)
        ])
        super(TopUI, self).__init__(columns, None, None)

        urwid.connect_signal(self.mach_list, 'selection_changed', self.set_selection)

    def keypress(self, size, key):
        key = super(TopUI, self).keypress(size, key)
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        else:
            return key

    def set_selection(self):
        w = self.mach_list.focus
        if isinstance(w, machine_list.MachineWidget):
            self.mach_info.show_machine(w.get_node().get_key())
        else:
            self.mach_info.show_machine(None)
