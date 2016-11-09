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

import vboxapi

class _VBoxWrapper_Cache(object):
    def __init__(self):
        self.mgr = vboxapi.VirtualBoxManager()
        self.vbox = self.mgr.getVirtualBox()
        self.machine_groups = None
        self.machines = None


class VBoxWrapper(object):
    _cache = None

    def __init__(self):
        if VBoxWrapper._cache is None:
            VBoxWrapper._cache = _VBoxWrapper_Cache()

    @property
    def mgr(self):
        return VBoxWrapper._cache.mgr

    @property
    def vbox(self):
        return VBoxWrapper._cache.vbox

    @property
    def constants(self):
        return VBoxWrapper._cache.mgr.constants

    @property
    def host(self):
        return VBoxWrapper._cache.vbox.host

    @property
    def systemProperties(self):
        return VBoxWrapper._cache.vbox.systemProperties

    @property
    def machine_groups(self):
        if VBoxWrapper._cache.machine_groups is None:
            VBoxWrapper._cache.machine_groups = self.mgr.getArray(self.vbox, 'machineGroups')
        return VBoxWrapper._cache.machine_groups

    @property
    def machines(self):
        if VBoxWrapper._cache.machines is None:
            VBoxWrapper._cache.machines = self.mgr.getArray(self.vbox, 'machines')
        return VBoxWrapper._cache.machines

    def drop_cache(self):
        VBoxWrapper._cache.machine_groups = None
        VBoxWrapper._cache.machines = None

    def getSession(self):
        return VBoxWrapper._cache.mgr.getSessionObject(VBoxWrapper._cache.vbox)


def VBoxConstants():
    vbox = VBoxWrapper()
    return vbox.constants
