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

from machine_list import MachineList, MachineNode
from machine_info import MachineInfo
from menus import MenuButton, PopupMenu
from popups import MessagePopup, ConfirmPopup
from . import popup_palette_map, menu_palette_map

class TopUI(urwid.WidgetPlaceholder):
    def __init__(self):
        self.mach_list = MachineList()
        self.mach_info = MachineInfo()
        columns = urwid.Columns([
            (urwid.WEIGHT, 1, self.mach_list),
            (urwid.WEIGHT, 2, self.mach_info)
        ])
        self.top_frame = urwid.Frame(columns, None, None)
        super(TopUI, self).__init__(self.top_frame)

        urwid.connect_signal(self.mach_list, 'selection_changed', self.set_selection)

    def keypress(self, size, key):
        key = super(TopUI, self).keypress(size, key)
        if self.original_widget is not self.top_frame:
            # Don't handle key events unless we're actually showing the main
            # UI as the top-level widget
            return key

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key == 'R':
            self.mach_list.reload()
        elif key == 'r':
            if self.mach_list.focus is not None:
                self.mach_list.focus.reload_text()
                self.set_selection(self.mach_list.focus.get_node())
        elif key == 's':
            if self.mach_list.focus is not None:
                sel_node = self.mach_list.focus.get_node()
                if isinstance(sel_node, MachineNode):
                    self.show_start(sel_node.machine)
        else:
            return key

    def set_selection(self, sel_node):
        if isinstance(sel_node, MachineNode):
            self.mach_info.show_machine(sel_node.machine)
        else:
            self.mach_info.show_machine(None)

    def show_popup(self, widget, **kwargs):
        popup_map = urwid.AttrMap(widget, popup_palette_map)
        self.original_widget = urwid.Overlay(popup_map, self.original_widget, **kwargs)

    def close_popup(self, sender=None):
        if self.original_widget is self.top_frame:
            return
        self.original_widget = self.original_widget[0]

    def start_machine(self, sender, params):
        self.close_popup()
        machine, vmtype = params
        self.show_message(u'start({}, {})'.format(machine.id, vmtype), title=u'Selection')

    def show_start(self, machine):
        menu_items = [
            MenuButton(u'Start GUI', u'G'),
            MenuButton(u'Start SDL GUI', u'D'),
            MenuButton(u'Start Headless', u'H')
        ]
        urwid.connect_signal(menu_items[0], 'click', self.start_machine, (machine, u'gui'))
        urwid.connect_signal(menu_items[1], 'click', self.start_machine, (machine, u'sdl'))
        urwid.connect_signal(menu_items[2], 'click', self.start_machine, (machine, u'headless'))
        popup = PopupMenu(menu_items, title=u'Start Machine')
        urwid.connect_signal(popup, 'close', self.close_popup)
        cols, rows = popup.get_min_size()
        self.show_popup(popup, align=urwid.CENTER, width=cols,
                        valign=urwid.MIDDLE, height=rows)

    def show_message(self, message, title=None):
        popup = MessagePopup(message, title)
        urwid.connect_signal(popup, 'close', self.close_popup)
        self.show_popup(popup, align=urwid.CENTER, width=(urwid.RELATIVE, 80),
                        valign=urwid.MIDDLE, height=urwid.PACK)
