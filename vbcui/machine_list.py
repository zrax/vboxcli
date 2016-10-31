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

class MachineNodeWidget(urwid.TreeWidget):
    def __init__(self, node):
        super(MachineNodeWidget, self).__init__(node)
        self._w = urwid.AttrWrap(self._w, None)
        self._w.focus_attr = 'focus'

    def selectable(self):
        return True

    def keypress(self, size, key):
        # Make the Left and Right keys behave somewhat consistently with
        # each other, which is apparently not the default
        key = super(MachineNodeWidget, self).keypress(size, key)
        if key in ('left', 'h'):
            if not self.is_leaf:
                self.expanded = False
                self.update_expanded_icon()
        elif key == 'l':
            if not self.is_leaf:
                self.expanded = True
                self.update_expanded_icon()
        else:
            return key


class MachineWidget(MachineNodeWidget):
    def get_display_text(self):
        machine = self.get_node().get_key()
        return [vb_enum.MachineState_icon(machine.state), u' ' + machine.name]


class MachineGroupWidget(MachineNodeWidget):
    def get_display_text(self):
        key = self.get_node().get_key()
        if key == u'/':
            return u'Virtual Machines'
        return key[key.rfind(u'/')+1:]


class MachineNode(urwid.TreeNode):
    def __init__(self, machine, parent=None):
        if parent is None:
            depth = 0
        else:
            depth = parent.get_depth() + 1
        urwid.TreeNode.__init__(self, machine, key=machine, parent=parent, depth=depth)

    def load_widget(self):
        return MachineWidget(self)


class MachineGroupNode(urwid.ParentNode):
    _all_groups = None

    def __init__(self, path, parent=None):
        if path == u'/':
            depth = 0
        else:
            depth = path.count(u'/')
        super(MachineGroupNode, self).__init__(path, key=path, parent=parent, depth=depth)
        self._machines = None
        self._group_count = None

    @property
    def machines(self):
        if self._machines is None:
            self._machines = []
            vbox = VBoxWrapper()
            for mach in vbox.machines:
                mgroups = vbox.mgr.getArray(mach, 'groups')
                if self.get_value() in mgroups:
                    self._machines.append(mach)
        return self._machines

    def load_child_keys(self):
        path = self.get_value()
        subgroups = []
        vbox = VBoxWrapper()
        for group in vbox.machine_groups:
            if path == group:
                continue
            if group.startswith(path):
                groupname = group[len(path):]
                if u'/' in groupname:
                    continue
                subgroups.append(group)
        self._group_count = len(subgroups)
        return subgroups + self.machines

    def load_child_node(self, key):
        index = self.get_child_index(key)
        if index < self._group_count:
            return MachineGroupNode(key, parent=self)
        else:
            return MachineNode(key, parent=self)

    def load_widget(self):
        return MachineGroupWidget(self)


class MachineList(urwid.TreeListBox):
    signals = ['selection_changed']

    def __init__(self):
        self.walker = urwid.TreeWalker(MachineGroupNode(u'/'))
        super(MachineList, self).__init__(self.walker)

        urwid.connect_signal(self.walker, 'modified', self.walker_modified)

        # Some vi-style keys for easier navigation
        self._command_map['j'] = urwid.CURSOR_DOWN
        self._command_map['k'] = urwid.CURSOR_UP
        self._command_map['ctrl f'] = urwid.CURSOR_PAGE_DOWN
        self._command_map['ctrl b'] = urwid.CURSOR_PAGE_UP

    def walker_modified(self):
        if self.focus:
            sel_node = self.focus.get_node()
            # Force the current selection to get its display updated
            iw = self.focus.get_inner_widget()
            iw.set_text(self.focus.get_display_text())
        else:
            sel_node = None
        urwid.emit_signal(self, 'selection_changed', sel_node)

    def reload(self):
        # This should force the whole tree to be re-generated
        # TODO: Save the currently selected key and try to find it again
        # after the tree is re-loaded
        self.walker.set_focus(MachineGroupNode(u'/'))
