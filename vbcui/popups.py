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

class PopupButton(urwid.Button):
    button_left = urwid.Text("[")
    button_right = urwid.Text("]")

    def __init__(self, caption, shortcut=None):
        super(PopupButton, self).__init__(u'')
        self.min_width = len(caption) + 4
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
        content = [(urwid.FIXED, 1, self.button_left),
                   urwid.SelectableIcon(caption, cursor_position=cursor),
                   (urwid.FIXED, 1, self.button_right)]
        self._w = urwid.AttrMap(urwid.Columns(content, dividechars=1), None, 'focus')


class MessagePopup(urwid.LineBox):
    spacer = (urwid.WEIGHT, 1, urwid.Text(u''))

    signals = ['close']

    def __init__(self, message, title=None):
        ok_button = PopupButton(_(u'OK'))
        urwid.connect_signal(ok_button, 'click', self._close)
        content = urwid.Pile([
            urwid.Text(message),
            urwid.Divider(),
            urwid.Columns([
                self.spacer,
                (urwid.FIXED, ok_button.min_width, ok_button),
                self.spacer
            ], dividechars=0)
        ])
        super(MessagePopup, self).__init__(content, title=title)

    def keypress(self, size, key):
        key = super(MessagePopup, self).keypress(size, key)
        if key == 'esc':
            self._close()
        else:
            return key

    def _close(self, sender=None):
        urwid.emit_signal(self, 'close')


class ConfirmPopup(urwid.LineBox):
    spacer = (urwid.WEIGHT, 1, urwid.Text(u''))

    signals = ['accepted', 'rejected']

    def __init__(self, message, title=None):
        ok_button = PopupButton(_(u'OK'))
        urwid.connect_signal(ok_button, 'click', self._accept)
        cancel_button = PopupButton(_(u'Cancel'))
        urwid.connect_signal(cancel_button, 'click', self._reject)
        content = urwid.Pile([
            urwid.Text(message),
            urwid.Divider(),
            urwid.Columns([
                self.spacer,
                (urwid.FIXED, ok_button.min_width, ok_button),
                self.spacer,
                (urwid.FIXED, cancel_button.min_width, cancel_button),
                self.spacer
            ], dividechars=0)
        ])
        super(ConfirmPopup, self).__init__(content, title=title)

    def keypress(self, size, key):
        key = super(ConfirmPopup, self).keypress(size, key)
        if key == 'esc':
            self._reject()
        else:
            return key

    def _accept(self, sender=None):
        urwid.emit_signal(self, 'accepted')

    def _reject(self, sender=None):
        urwid.emit_signal(self, 'rejected')


class HelpPopup(urwid.LineBox):
    signals = ['close']

    def __init__(self, text, title=None):
        close_button = PopupButton(_(u'Close'))
        urwid.connect_signal(close_button, 'click', self._close)
        lines = text.split(u'\n')
        content = urwid.SimpleFocusListWalker([urwid.Text(ln) for ln in lines])
        super(HelpPopup, self).__init__(urwid.ListBox(content), title=title)

    def keypress(self, size, key):
        key = super(HelpPopup, self).keypress(size, key)
        if key in {'esc', 'enter'}:
            self._close()
        else:
            return key

    def _close(self, sender=None):
        urwid.emit_signal(self, 'close')
