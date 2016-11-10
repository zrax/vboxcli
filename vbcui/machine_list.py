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

class MachineNodeKey(object):
    def __init__(self, machine):
        self.machine = machine

    def get_display_text(self):
        return [vb_enum.MachineState_icon(self.machine.state), u' ' + self.machine.name]


class MachineGroupNodeKey(object):
    def __init__(self, path, default_expanded=True):
        self.path = path
        self.default_expanded = default_expanded

    def get_display_text(self):
        if self.path == u'/':
            return _(u'Virtual Machines')
        return self.path[self.path.rfind(u'/')+1:]


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
        if key in {'left', 'h'}:
            if not self.is_leaf:
                self.expanded = False
                self.update_expanded_icon()
        elif key == 'l':
            if not self.is_leaf:
                self.expanded = True
                self.update_expanded_icon()
        else:
            return key

    def get_display_text(self):
        return self.get_node().get_key().get_display_text()

    def reload_text(self):
        iw = self.get_inner_widget()
        iw.set_text(self.get_display_text())


class MachineGroupWidget(MachineNodeWidget):
    def __init__(self, node):
        super(MachineGroupWidget, self).__init__(node)
        self.expanded = node.get_key().default_expanded
        self.update_expanded_icon()


class MachineNode(urwid.TreeNode):
    def __init__(self, node, parent=None):
        if parent is None:
            depth = 0
        else:
            depth = parent.get_depth() + 1
        urwid.TreeNode.__init__(self, node, key=node, parent=parent, depth=depth)

    @property
    def machine(self):
        return self.get_value().machine

    @property
    def selection_id(self):
        return self.machine.id

    def load_widget(self):
        return MachineNodeWidget(self)


class MachineGroupNode(urwid.ParentNode):
    def __init__(self, node, parent=None):
        if isinstance(node, unicode):
            # Mostly a shortcut for the initial node creation
            node = MachineGroupNodeKey(node)

        if node.path == u'/':
            depth = 0
        else:
            depth = node.path.count(u'/')
        super(MachineGroupNode, self).__init__(node, key=node, parent=parent, depth=depth)
        self._machines = None
        self._group_count = None

    @property
    def path(self):
        return self.get_value().path

    @property
    def selection_id(self):
        return self.path

    @property
    def machines(self):
        if self._machines is None:
            self._machines = []
            vbox = VBoxWrapper()
            for mach in vbox.machines:
                mgroups = vbox.mgr.getArray(mach, 'groups')
                if self.path in mgroups:
                    self._machines.append(mach)
        return self._machines

    def load_child_keys(self):
        subgroups = []
        vbox = VBoxWrapper()
        for group in vbox.machine_groups:
            if self.path == group:
                continue
            if group.startswith(self.path):
                groupname = group[len(self.path):]
                if u'/' in groupname:
                    continue
                subgroups.append(group)
        self._group_count = len(subgroups)

        # Try to sort these to match the VirtualBox GUI's sorting
        # TODO: Allow this to be modified and saved as well
        order = vbox.vbox.getExtraData(u'GUI/GroupDefinitions' + self.path)
        children = []
        machines = self.machines[:]
        if order is not None:
            order = order.split(u',')
            for ob in order:
                if ob.startswith(u'go=') or ob.startswith(u'gc='):
                    group = self.path + ob[3:]
                    children.append(MachineGroupNodeKey(group, ob.startswith(u'go=')))
                    try:
                        subgroups.remove(group)
                    except ValueError:
                        pass
                elif ob.startswith(u'm='):
                    for mach in machines:
                        if mach.id == ob[2:]:
                            children.append(MachineNodeKey(mach))
                            try:
                                machines.remove(mach)
                            except ValueError:
                                pass

        # Ensure any unsorted groups and machines get added as well
        for group in subgroups:
            children.append(MachineGroupNodeKey(group))
        for mach in machines:
            children.append(MachineNodeKey(mach))
        return children

    def load_child_node(self, key):
        if isinstance(key, MachineGroupNodeKey):
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
            # Force the current selection to get its text/icon updated
            self.focus.reload_text()
        else:
            sel_node = None
        urwid.emit_signal(self, 'selection_changed', sel_node)

    def reload(self):
        selection = None
        if self.focus:
            sel_node = self.focus.get_node()
            selection = sel_node.selection_id

        # This should force the whole tree to be re-generated
        VBoxWrapper().drop_cache()
        self.walker.set_focus(MachineGroupNode(u'/'))

        node = self.walker.focus
        while node is not None:
            if node.selection_id == selection:
                self.walker.set_focus(node)
                break
            widget, node = self.walker.get_next(node)
