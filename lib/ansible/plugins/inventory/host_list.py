# Copyright 2017 RedHat, inc
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
r'''
DOCUMENTATION:
    inventory: host_list
    version_added: "2.4"
    short_description: Parses a 'host list' string
    description:
        - Parses a host list string as a comma separated values of hosts
        - This plugin only applies to inventory strings that are not paths and contain a comma.
EXAMPLES: |
    # define 2 hosts in command line
    ansible -i '10.10.2.6, 10.10.2.4' -m ping all

    # DNS resolvable names
    ansible -i 'host1.example.com, host2' -m user -a 'name=me state=abset' all

    # just use localhost
    ansible-playbook -i 'localhost,' play.yml -c local
'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_bytes, to_text, to_native
from ansible.parsing.utils.addresses import parse_address
from ansible.plugins.inventory import BaseInventoryPlugin


class InventoryModule(BaseInventoryPlugin):

    NAME = 'host_list'

    def verify_file(self, host_list):

        valid = False
        b_path = to_bytes(host_list)
        if not os.path.exists(b_path) and ',' in host_list:
                valid = True
        return valid

    def parse(self, inventory, loader, host_list, cache=True):
        ''' parses the inventory file '''

        super(InventoryModule, self).parse(inventory, loader, host_list)

        try:
            for h in host_list.split(','):
                if h:
                    try:
                        (host, port) = parse_address(h, allow_ranges=False)
                    except AnsibleError as e:
                        self.display.vvv("Unable to parse address from hostname, leaving unchanged: %s" % to_native(e))
                        host = h
                        port = None

                    if host not in self.inventory.hosts:
                        self.inventory.add_host(host, group='ungrouped', port=port)
        except Exception as e:
            raise AnsibleParserError("Invalid data from string, could not parse: %s" % str(e))
