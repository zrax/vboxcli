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

from vbifc import VBoxWrapper
from machine_list import MachineList, MachineNode
from machine_info import MachineInfo
from menus import MenuButton, PopupMenu
from popups import MessagePopup, ConfirmPopup
from . import VBCUIEventLoop, popup_palette_map, menu_palette_map

class StatusBar(urwid.ProgressBar):
    text_align = urwid.LEFT

    def __init__(self):
        self.status_text = u''
        super(StatusBar, self).__init__('statusbar', 'progress', 0, 100)

    def set_text(self, text):
        self.status_text = text
        self.set_completion(0)

    def get_text(self):
        if self.current == 0:
            return self.status_text
        else:
            return u'{} ({} %)'.format(self.status_text, self.current)


class TopUI(urwid.WidgetPlaceholder):
    def __init__(self):
        self.mach_list = MachineList()
        self.mach_info = MachineInfo()
        columns = urwid.Columns([
            (urwid.WEIGHT, 1, self.mach_list),
            (urwid.WEIGHT, 2, self.mach_info)
        ])
        self.status_bar = StatusBar()
        self.top_frame = urwid.Frame(columns, None, self.status_bar)
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
            self.update_selected()
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

    def update_selected(self):
        if self.mach_list.focus is not None:
            self.mach_list.focus.reload_text()
            self.set_selection(self.mach_list.focus.get_node())

    def show_popup(self, widget, **kwargs):
        popup_map = urwid.AttrMap(widget, popup_palette_map)
        self.original_widget = urwid.Overlay(popup_map, self.original_widget, **kwargs)

    def close_popup(self, sender=None):
        if self.original_widget is self.top_frame:
            return
        self.original_widget = self.original_widget[0]

    def progress_bar(self, progress):
        vbox = VBoxWrapper()
        try:
            while not progress.completed:
                progress.waitForCompletion(100)
                vbox.mgr.waitForEvents(0)
                self.status_bar.set_completion(progress.percent)
                VBCUIEventLoop.instance.draw_screen()
            if int(progress.resultCode) == 0:
                return True
            err = progress.errorInfo
            self.show_message(
                u"Error in module '{}': {}".format(err.component, err.text),
                title=u'Error starting VM')
        except KeyboardInterrupt:
            if progress.cancelable:
                progress.cancel()
            self.show_message(u'Operation aborted', title=u'Error starting VM')
        return False

    def start_machine(self, machine, vmtype):
        vbox = VBoxWrapper()
        session = vbox.getSession()
        progress = machine.launchVMProcess(session, vmtype, u'')
        self.status_bar.set_text(u'Starting {}'.format(machine.name))
        if self.progress_bar(progress) and int(progress.resultCode) == 0:
            session.unlockMachine()
        self.update_selected()
        self.status_bar.set_text(u'')

    def _on_start_machine(self, sender, params):
        self.close_popup()
        machine, vmtype = params
        self.start_machine(machine, vmtype)

    def show_start(self, machine):
        menu_items = [
            MenuButton(u'Start GUI', u'G'),
            MenuButton(u'Start SDL GUI', u'D'),
            MenuButton(u'Start Headless', u'H')
        ]
        urwid.connect_signal(menu_items[0], 'click', self._on_start_machine, (machine, u'gui'))
        urwid.connect_signal(menu_items[1], 'click', self._on_start_machine, (machine, u'sdl'))
        urwid.connect_signal(menu_items[2], 'click', self._on_start_machine, (machine, u'headless'))
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
