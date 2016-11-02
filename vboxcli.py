#!/usr/bin/env python2
# vboxcli - curses GUI for VirtualBox
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

import sys
import urwid

from vbcui import top_ui, palette
from vbifc import VBoxWrapper

def main(argv):
    # Ensure this gets set up before we start doing curses stuff that might
    # mess with the initial output
    vbox = VBoxWrapper()

    ui = urwid.AttrMap(top_ui.TopUI(), 'default')
    loop = urwid.MainLoop(ui, palette)
    loop.run()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
