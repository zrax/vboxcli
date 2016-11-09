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

from vbifc import VBoxWrapper, VBoxConstants
from machine_list import MachineList, MachineNode
from machine_info import MachineInfo
from menus import MenuButton, PopupMenu, MenuBar
from popups import MessagePopup, ConfirmPopup
from . import VBCUIEventLoop, popup_palette_map

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
        self.columns = urwid.Columns([
            (urwid.WEIGHT, 1, self.mach_list),
            (urwid.WEIGHT, 2, self.mach_info)
        ])
        top_menu = [
            (u'&File', [
                MenuButton(u'&Preferences'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'&Import Appliance'),
                MenuButton(u'&Export Appliance'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'&Virtual Media Manager'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'E&xit', u'q', action=self.quit)
            ]),
            (u'&Machine', [
                MenuButton(u'&New'),
                MenuButton(u'&Add'),
                MenuButton(u'&Settings'),
                MenuButton(u'Cl&one'),
                MenuButton(u'Remo&ve'),
                MenuButton(u'Gro&up'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'S&tart...', u's', action=self.show_start),
                MenuButton(u'&Pause'),
                MenuButton(u'&Reset'),
                MenuButton(u'Sto&p...'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'D&iscard Saved State'),
                MenuButton(u'Show &Log'),
                MenuButton(u'Re&fresh')
            ]),
            (u'&Devices', [
                MenuButton(u'&Attach Optical Disk Image'),
                MenuButton(u'&Remove Disk from Virtual Drive'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'Manage &USB Devices'),
                urwid.Divider(u'\u2500'),
                MenuButton(u'Insert &Guest Additions CD Image')
            ]),
            (u'&Help', [
                MenuButton(u'&About')
            ])
        ]
        #self.menu_bar = MenuBar(top_menu)
        self.hint_bar = urwid.Text(u'?: Help  q: Quit  s: Start/Stop  e: Edit VM Settings')
        self.status_bar = StatusBar()
        self.top_frame = urwid.Frame(self.columns, urwid.AttrWrap(self.hint_bar, 'statusbar'), self.status_bar)
        super(TopUI, self).__init__(self.top_frame)

        #urwid.connect_signal(self.menu_bar, 'popup_closed', self.reset_focus)
        urwid.connect_signal(self.mach_list, 'selection_changed', self.set_selection)

    def keypress(self, size, key):
        key = super(TopUI, self).keypress(size, key)
        if self.original_widget is not self.top_frame:
            # Don't handle key events unless we're actually showing the main
            # UI as the top-level widget
            return key

        if key in ('q', 'Q'):
            self.quit()
        elif key == 'P':
            self.pause_resume()
        elif key == 'R':
            self.mach_list.reload()
        elif key == 'r':
            self.update_selected()
        elif key == 's':
            self.show_start()
        else:
            return key

    def quit(self, sender=None):
        raise urwid.ExitMainLoop()

    def reset_focus(self):
        self.top_frame.focus_position = 'body'

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
        vbconst = VBoxConstants()
        session = vbox.getSession()
        try:
            progress = machine.launchVMProcess(session, vmtype, u'')
            self.status_bar.set_text(u'Starting {}'.format(machine.name))
            self.progress_bar(progress)
        except Exception as ex:
            self.show_message(vbox.exceptMessage(ex), title=u'VirtualBox Exception')
        if session.state == vbconst.SessionState_Locked:
            session.unlockMachine()
        self.update_selected()
        self.status_bar.set_text(u'')

    def _on_start_machine(self, sender, params):
        self.close_popup(sender)
        machine, vmtype = params
        self.start_machine(machine, vmtype)

    def get_running_session(self, machine):
        # Must unlock the session if one is returned
        vbox = VBoxWrapper()
        vbconst = VBoxConstants()
        session = vbox.getSession()
        machine.lockMachine(session, vbconst.LockType_Shared)
        if session.state != vbconst.SessionState_Locked:
            self.show_message(u'Could not lock session', title=u'Error')
            return None
        else:
            return session

    def save_state(self, machine):
        session = self.get_running_session(machine)
        try:
            progress = session.machine.saveState()
            self.status_bar.set_text(u'Saving {}'.format(machine.name))
            self.progress_bar(progress)
        except Exception as ex:
            vbox = VBoxWrapper()
            self.show_message(vbox.exceptMessage(ex), title=u'VirtualBox Exception')
        self.update_selected()
        self.status_bar.set_text(u'')

    def _on_save_state(self, sender, machine):
        self.close_popup(sender)
        self.save_state(machine)

    def console_cmd(self, machine, command):
        vbconst = VBoxConstants()
        session = self.get_running_session(machine)
        console = session.console
        try:
            if command == 'pause':
                console.pause()
            elif command == 'resume':
                console.resume()
            elif command == 'acpi_button':
                console.powerButton()
            elif command == 'power_down':
                console.powerDown()
            else:
                self.show_message(u'Unsupported command: {}'.format(command),
                                  title=u'Internal Error')
        except Exception as ex:
            vbox = VBoxWrapper()
            self.show_message(vbox.exceptMessage(ex), title=u'VirtualBox Exception')

        if session.state == vbconst.SessionState_Locked:
            session.unlockMachine()
        self.update_selected()

    def _on_console_cmd(self, sender, params):
        self.close_popup(sender)
        machine, command = params
        self.console_cmd(machine, command)

    def show_start(self, sender=None):
        if self.mach_list.focus is None:
            return
        sel_node = self.mach_list.focus.get_node()
        if not isinstance(sel_node, MachineNode):
            return

        vbconst = VBoxConstants()
        machine = sel_node.machine
        if machine.state in {vbconst.MachineState_PoweredOff,
                             vbconst.MachineState_Aborted,
                             vbconst.MachineState_Saved}:
            menu_items = [
                MenuButton(u'Start &GUI', action=self._on_start_machine,
                           user_data=(machine, u'gui')),
                MenuButton(u'Start S&DL GUI', action=self._on_start_machine,
                           user_data=(machine, u'sdl')),
                MenuButton(u'Start &Headless', action=self._on_start_machine,
                           user_data=(machine, u'headless'))
            ]
            title = u'Start Machine'
        elif machine.state in {vbconst.MachineState_Running,
                               vbconst.MachineState_Paused}:
            menu_items = [
                MenuButton(u'Sa&ve State', action=self._on_save_state,
                           user_data=machine),
                MenuButton(u'ACPI Sh&utdown', action=self._on_console_cmd,
                           user_data=(machine, 'acpi_button')),
                MenuButton(u'Po&wer Off', action=self._on_console_cmd,
                           user_data=(machine, 'power_down'))
            ]
            title = u'Stop Machine'
        else:
            return

        popup = PopupMenu(menu_items, title=title)
        urwid.connect_signal(popup, 'close', self.close_popup)
        cols, rows = popup.get_min_size()
        self.show_popup(popup, align=urwid.CENTER, width=cols,
                        valign=urwid.MIDDLE, height=rows)

    def pause_resume(self, sender=None):
        if self.mach_list.focus is None:
            return
        sel_node = self.mach_list.focus.get_node()
        if not isinstance(sel_node, MachineNode):
            return

        vbconst = VBoxConstants()
        machine = sel_node.machine
        if machine.state == vbconst.MachineState_Running:
            self.console_cmd(machine, 'pause')
        elif machine.state == vbconst.MachineState_Paused:
            self.console_cmd(machine, 'resume')

    def show_message(self, message, title=None):
        popup = MessagePopup(message, title)
        urwid.connect_signal(popup, 'close', self.close_popup)
        self.show_popup(popup, align=urwid.CENTER, width=(urwid.RELATIVE, 80),
                        valign=urwid.MIDDLE, height=urwid.PACK)
