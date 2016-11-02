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

class MenuButton(urwid.Button):
    spacer = (urwid.FIXED, 1, urwid.Text(u' '))

    def __init__(self, caption, shortcut=None, global_shortcut=None):
        super(MenuButton, self).__init__(u'')
        self.min_width = len(caption) + 2
        self.shortcut = shortcut
        cursor = 0
        if shortcut is not None:
            parts = caption.partition(shortcut)
            caption = []
            if parts[0] != u'':
                caption.append(parts[0])
            caption.append(('shortcut', parts[1]))
            if parts[2] != u'':
                caption.append(parts[2])
            cursor = len(parts[0])
        content = [self.spacer, urwid.SelectableIcon(caption, cursor_position=cursor)]
        if global_shortcut is not None:
            self.min_width += len(shortcut) + 2
            content.append((urwid.FIXED, len(shortcut), urwid.Text(shortcut)))
        content.append(self.spacer)
        self._w = urwid.AttrMap(urwid.Columns(content, dividechars=0), None, 'focus')


class PopupMenu(urwid.LineBox):
    signals = ['close']

    def __init__(self, items, title=None):
        self.items = urwid.SimpleFocusListWalker(items)
        self.menu = urwid.ListBox(self.items)
        super(PopupMenu, self).__init__(self.menu, title=title)

    def keypress(self, size, key):
        key = super(PopupMenu, self).keypress(size, key)
        if key == 'esc':
            self._close()
        for item in self.items:
            if isinstance(item, MenuButton) and key == item.shortcut.lower():
                item._emit('click')
                return
        return key

    def _close(self, sender=None):
        urwid.emit_signal(self, 'close')

    def get_min_size(self):
        menu_width = 0
        for item in self.items:
            if hasattr(item, 'min_width') and item.min_width > menu_width:
                menu_width = item.min_width
        return (menu_width + 2, len(self.items) + 2)
