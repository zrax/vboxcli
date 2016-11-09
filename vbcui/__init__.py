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

palette = [
    # Name,         foreground,         background,     mono
    ('default',     'light gray',       'black',        ''),
    ('focus',       'black',            'light gray',   'standout'),
    ('shortcut',    'white,bold',       'black',        'bold'),
    ('statusbar',   'white,bold',       'dark blue',    'standout'),
    ('progress',    'dark blue',        'brown',        ''),
    ('info header', 'light gray,bold',  'black',        'bold'),
    ('info key',    'light gray',       'black',        ''),
    ('info',        'dark cyan',        'black',        'underline'),
    ('info error',  'dark red,bold',    'black',        'bold'),
    ('state run',   'dark green',       'black',        'bold'),
    ('state error', 'dark red,bold',    'black',        'bold'),
    ('state pause', 'brown',            'black',        'bold'),
    ('state off',   'dark gray',        'black',        'bold'),
    ('popup',       'black',            'light gray',   'standout'),
    ('popup focus', 'light gray',       'black',        ''),
    ('popup shortcut', 'black,underline',    'light gray',   'bold'),
    ('menu',        'light gray',       'dark blue',    'standout'),
    ('menu focus',  'dark blue',        'light gray',   ''),
    ('menu shortcut', 'white,bold',     'dark blue',    'bold')
]

popup_palette_map = {
    None: 'popup',
    'focus': 'popup focus',
    'shortcut': 'popup shortcut'
}

menu_palette_map = {
    None: 'menu',
    'focus': 'menu focus',
    'shortcut': 'menu shortcut'
}

class VBCUIEventLoop(urwid.MainLoop):
    instance = None

    def __init__(self, widget):
        VBCUIEventLoop.instance = self
        super(VBCUIEventLoop, self).__init__(widget, palette=palette, pop_ups=True)
