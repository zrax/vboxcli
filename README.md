# VBoxCLI - A Curses UI for VirtualBox

## Requirements

* [Python 2.7](http://www.python.org) (the VirtualBox SDK doesn't support
  Python 3 yet)
* The [VirtualBox SDK](https://www.virtualbox.org/wiki/Downloads) Python
  bindings.  Note that this usually comes with VirtualBox itself, but may be
  provided as a separate package on some Linux distributions.
* [Urwid](http://urwid.org) 1.3 or later

## Usage

Just run `./vboxcli.py` in the root of the vboxcli directory.  For now, most
operations are controlled by keyboard shortcuts.  Press `?` on the main screen
for a summary of the available keyboard commands.

## Rationale

[phpVirtualBox](https://sourceforge.net/projects/phpvirtualbox/) is a great
project for managing VirtualBox machines on a server.  However, it has some
drawbacks, depending on your use:
* It only works via the vboxweb-service.
  * This means it can only access VMs for the web service user, not for other
    accounts on the system.  It also means the service must be configured
    and running in order to use phpVirtualBox.
* It requires a web server running PHP.
* Recently, it has seen less activity -- for example, there is no release
  for VirtualBox 5.1 yet, and the existing version needs some hacks to work
  with 5.1.

I wanted something that still allowed me to manage VMs on a headless server,
but without needing to rely on the web service or PHP.  Using a curses-like
UI allows one to manage VMs directly like the Qt front end, while also not
requiring an X server or the heavy Qt libraries to be installed.

Note that it's still possible to use vboxcli on an X server, as it can launch
VMs in a GUI window if desired.

## Contributing

Defect reports and patches are always welcome!  Visit the project pages on
github for details:
https://github.com/zrax/vboxcli

vboxcli is released under the terms of the GPLv2+ license.  See the COPYING
file for details.
