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
from .machine_list import MachineList, MachineNode
from .machine_info import MachineInfo
from .menus import MenuButton, PopupMenu, MenuBar
from .popups import MessagePopup, ConfirmPopup, HelpPopup
from . import VBCUIEventLoop, popup_palette_map, VBOXCLI_VERSION


def get_help_text():
    # Needs to be a function so gettext is initialized by the time we need
    # the text content.  Please keep this content limited to 72 columns
    return _('''\
VirtualBox Command Line Interface (vboxcli) v{version}
Created by Michael Hansen

Keyboard Commands:
    q:  Quit vboxcli                  ?:  Show this help screen
    r:  Refresh current VM            R:  Refresh all VMs and VM tree
    s:  Start/Stop Selected VM        e:  Edit settings for selected VM
    P:  Pause/Resume Selected VM      ^t: Reset selected VM
    ^l: Show logs for selected VM     ^d: Discard saved state

    M:  Show Virtual Media Manager    ^p: Show global preferences
    ^a: Import appliance as VM        ^e: Export VM as appliance
    n:  Create new VM                 ^r: Remove selected VM
    a:  Add existing VM to list       ^o: Clone selected VM

    O:  Attach optical disk           X:  Remove optical disk
    U:  Manage USB devices            G:  Insert Guest Additions CD''').format(version=VBOXCLI_VERSION)


class StatusBar(urwid.ProgressBar):
    text_align = urwid.LEFT

    def __init__(self):
        self.status_text = ''
        super(StatusBar, self).__init__('statusbar', 'progress', 0, 100)

    def set_text(self, text):
        self.status_text = text
        self.set_completion(0)

    def get_text(self):
        if self.current == 0:
            return self.status_text
        else:
            return '{} ({} %)'.format(self.status_text, self.current)


class TopUI(urwid.WidgetPlaceholder):
    def __init__(self):
        self.mach_list = MachineList()
        self.mach_info = MachineInfo()
        self.columns = urwid.Columns([
            (urwid.WEIGHT, 1, self.mach_list),
            (urwid.WEIGHT, 2, self.mach_info)
        ])
        top_menu = [
            (_('&File'), [
                MenuButton(_('&Preferences')),
                urwid.Divider('\u2500'),
                MenuButton(_('&Import Appliance')),
                MenuButton(_('&Export Appliance')),
                urwid.Divider('\u2500'),
                MenuButton(_('&Virtual Media Manager')),
                urwid.Divider('\u2500'),
                MenuButton(_('E&xit'), 'q', action=self.quit)
            ]),
            (_('&Machine'), [
                MenuButton(_('&New')),
                MenuButton(_('&Add')),
                MenuButton(_('&Settings')),
                MenuButton(_('Cl&one')),
                MenuButton(_('Remo&ve')),
                MenuButton(_('Gro&up')),
                urwid.Divider('\u2500'),
                MenuButton(_('S&tart...'), 's', action=self.show_start),
                MenuButton(_('&Pause')),
                MenuButton(_('&Reset')),
                MenuButton(_('Sto&p...')),
                urwid.Divider('\u2500'),
                MenuButton(_('D&iscard Saved State')),
                MenuButton(_('Show &Log')),
                MenuButton(_('Re&fresh'))
            ]),
            (_('&Devices'), [
                MenuButton(_('&Attach Optical Disk Image')),
                MenuButton(_('&Remove Disk from Virtual Drive')),
                urwid.Divider('\u2500'),
                MenuButton(_('Manage &USB Devices')),
                urwid.Divider('\u2500'),
                MenuButton(_('Insert &Guest Additions CD Image'))
            ]),
            (_('&Help'), [
                MenuButton(_('&About'))
            ])
        ]
        #self.menu_bar = MenuBar(top_menu)
        self.hint_bar = urwid.Text(_('?: Help  q: Quit  s: Start/Stop  e: Edit VM Settings'))
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

        if key in {'q', 'Q'}:
            self.quit()
        elif key == '?':
            self.show_help()
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
                _("Error in module '{}': {}").format(err.component, err.text),
                title=_('Error starting VM'))
        except KeyboardInterrupt:
            if progress.cancelable:
                progress.cancel()
            self.show_message(_('Operation aborted'), title=_('Error starting VM'))
        return False

    def start_machine(self, machine, vmtype):
        vbox = VBoxWrapper()
        vbconst = VBoxConstants()
        session = vbox.getSession()
        try:
            progress = machine.launchVMProcess(session, vmtype, '')
            self.status_bar.set_text(_('Starting {}').format(machine.name))
            self.progress_bar(progress)
        except Exception as ex:
            self.show_message(vbox.exceptMessage(ex), title=_('VirtualBox Exception'))
        if session.state == vbconst.SessionState_Locked:
            session.unlockMachine()
        self.update_selected()
        self.status_bar.set_text('')

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
            self.show_message(_('Could not lock session'), title=_('Error'))
            return None
        else:
            return session

    def save_state(self, machine):
        session = self.get_running_session(machine)
        try:
            progress = session.machine.saveState()
            self.status_bar.set_text(_('Saving {}').format(machine.name))
            self.progress_bar(progress)
        except Exception as ex:
            vbox = VBoxWrapper()
            self.show_message(vbox.exceptMessage(ex), title=_('VirtualBox Exception'))
        self.update_selected()
        self.status_bar.set_text('')

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
                self.show_message(_('Unsupported command: {}').format(command),
                                  title=_('Internal Error'))
        except Exception as ex:
            vbox = VBoxWrapper()
            self.show_message(vbox.exceptMessage(ex), title=_('VirtualBox Exception'))

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
                MenuButton(_('Start &GUI'), action=self._on_start_machine,
                           user_data=(machine, 'gui')),
                MenuButton(_('Start S&DL GUI'), action=self._on_start_machine,
                           user_data=(machine, 'sdl')),
                MenuButton(_('Start &Headless'), action=self._on_start_machine,
                           user_data=(machine, 'headless'))
            ]
            title = _('Start Machine')
        elif machine.state in {vbconst.MachineState_Running,
                               vbconst.MachineState_Paused}:
            menu_items = [
                MenuButton(_('Sa&ve State'), action=self._on_save_state,
                           user_data=machine),
                MenuButton(_('ACPI Sh&utdown'), action=self._on_console_cmd,
                           user_data=(machine, 'acpi_button')),
                MenuButton(_('Po&wer Off'), action=self._on_console_cmd,
                           user_data=(machine, 'power_down'))
            ]
            title = _('Stop Machine')
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

    def show_message(self, message, title=''):
        popup = MessagePopup(message, title)
        urwid.connect_signal(popup, 'close', self.close_popup)
        self.show_popup(popup, align=urwid.CENTER, width=(urwid.RELATIVE, 80),
                        valign=urwid.MIDDLE, height=urwid.PACK)

    def show_help(self, sender=None):
        popup = HelpPopup(get_help_text(), title=_('Help/About'))
        urwid.connect_signal(popup, 'close', self.close_popup)
        self.show_popup(popup, align=urwid.CENTER, width=76,
                        valign=urwid.MIDDLE, height=popup.suggested_height)
