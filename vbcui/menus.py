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

from . import menu_palette_map

class MenuButton(urwid.Button):
    spacer = (urwid.FIXED, 1, urwid.Text(' '))

    def __init__(self, caption, global_shortcut=None, action=None, user_data=None):
        super(MenuButton, self).__init__('')
        self.min_width = len(caption) + 2
        self.shortcut = None
        self.global_shortcut = global_shortcut
        self.user_data = user_data

        cursor = 0
        if '&' in caption:
            parts = caption.partition('&')
            self.shortcut = parts[2][0]
            caption = []
            if parts[0] != '':
                caption.append(parts[0])
            caption.append(('shortcut', self.shortcut))
            if len(parts[2]) > 1:
                caption.append(parts[2][1:])
            cursor = len(parts[0])
        content = [self.spacer, urwid.SelectableIcon(caption, cursor_position=cursor)]
        if global_shortcut is not None:
            self.min_width += len(global_shortcut) + 2
            content.append((urwid.FIXED, len(global_shortcut), urwid.Text(global_shortcut)))
        content.append(self.spacer)
        self._w = urwid.AttrMap(urwid.Columns(content, dividechars=0), None, 'focus')

        if action is not None:
            if self.user_data is not None:
                urwid.connect_signal(self, 'click', action, self.user_data)
            else:
                urwid.connect_signal(self, 'click', action)


class PopupMenu(urwid.LineBox):
    signals = ['close']

    def __init__(self, items, title=''):
        self.items = urwid.SimpleFocusListWalker(items)
        self.menu = urwid.ListBox(self.items)
        super(PopupMenu, self).__init__(self.menu, title=title)

    def keypress(self, size, key):
        key = super(PopupMenu, self).keypress(size, key)
        if key == 'esc':
            self._close()
        for item in self.items:
            if isinstance(item, MenuButton) and item.shortcut is not None \
                    and key == item.shortcut.lower():
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


class MenuBar(urwid.AttrMap):
    signals = ['popup_closed']

    class MenuPopup(urwid.PopUpLauncher):
        signals = ['closed']

        def __init__(self, button):
            super(MenuBar.MenuPopup, self).__init__(button)
            self.items = button.user_data
            urwid.connect_signal(button, 'click', lambda sender: self.open_pop_up())

        def create_pop_up(self):
            menu = PopupMenu(self.items)
            urwid.connect_signal(menu, 'close', self.close_pop_up)
            return urwid.AttrMap(menu, menu_palette_map)

        def get_pop_up_parameters(self):
            # Can't rely on a PopupMenu existing yet
            menu_width = 8
            for item in self.items:
                if hasattr(item, 'min_width') and item.min_width > menu_width:
                    menu_width = item.min_width

            return {
                'left': 0,
                'top': 1,
                'overlay_width': menu_width + 2,
                'overlay_height': len(self.items) + 2
            }

        def close_pop_up(self):
            super(MenuBar.MenuPopup, self).close_pop_up()
            urwid.emit_signal(self, 'closed')

    def __init__(self, menu_items):
        self.content = []
        for item in menu_items:
            label, popup_items = item
            menu_button = MenuButton(label, user_data=popup_items)
            popup = self.MenuPopup(menu_button)
            urwid.connect_signal(popup, 'closed', self.popup_closed)
            self.content.append((urwid.FIXED, menu_button.min_width, popup))
        columns = urwid.Columns(self.content, dividechars=0)
        super(MenuBar, self).__init__(columns, menu_palette_map)

    def popup_closed(self):
        urwid.emit_signal(self, 'popup_closed')
