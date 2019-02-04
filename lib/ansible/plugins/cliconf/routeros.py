#
# (c) 2017 Red Hat Inc.
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
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
cliconf: routeros
short_description: Use routeros cliconf to run command on MikroTik RouterOS platform
description:
  - This routeros plugin provides low level abstraction apis for
    sending and receiving CLI commands from MikroTik RouterOS network devices.
version_added: "2.7"
"""

import re
import json

from itertools import chain

from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode
from ansible.module_utils.network.common.config import NetworkConfig, dumps


class Cliconf(CliconfBase):

    def get_diff(self, candidate=None, running=None, diff_match='line', diff_ignore_lines=None, path=None, diff_replace='line'):
        """
        Generate diff between candidate and running configuration. If the
        remote host supports onbox diff capabilities ie. supports_onbox_diff in that case
        candidate and running configurations are not required to be passed as argument.
        In case if onbox diff capability is not supported candidate argument is mandatory
        and running argument is optional.
        :param candidate: The configuration which is expected to be present on remote host.
        :param running: The base configuration which is used to generate diff.
        :param diff_match: Instructs how to match the candidate configuration with current device configuration
                      Valid values are 'line', 'strict', 'exact', 'none'.
                      'line' - commands are matched line by line
                      'strict' - command lines are matched with respect to position
                      'exact' - command lines must be an equal match
                      'none' - will not compare the candidate configuration with the running configuration
        :param diff_ignore_lines: Use this argument to specify one or more lines that should be
                                  ignored during the diff.  This is used for lines in the configuration
                                  that are automatically updated by the system.  This argument takes
                                  a list of regular expressions or exact line matches.
        :param path: The ordered set of parents that uniquely identify the section or hierarchy
                     the commands should be checked against.  If the parents argument
                     is omitted, the commands are checked against the set of top
                    level or global commands.
        :param diff_replace: Instructs on the way to perform the configuration on the device.
                        If the replace argument is set to I(line) then the modified lines are
                        pushed to the device in configuration mode.  If the replace argument is
                        set to I(block) then the entire command block is pushed to the device in
                        configuration mode if any line is not correct.
        :return: Configuration diff in  json format.
               {
                   'config_diff': '',
                   'banner_diff': {}
               }

        """
        diff = {}

        # prepare candidate configuration
        candidate_obj = NetworkConfig(indent=1)
        # want_src, want_banners = self._extract_banners(candidate)
        # candidate_obj.load(want_src)

        # if running and diff_match != 'none':
        # running configuration
        # have_src, have_banners = self._extract_banners(running)
        # running_obj = NetworkConfig(indent=1, contents=have_src, ignore_lines=diff_ignore_lines)
        # configdiffobjs = candidate_obj.difference(running_obj, path=path, match=diff_match, replace=diff_replace)

        # else:
        configdiffobjs = candidate_obj.items
        # have_banners = {}

        diff['config_diff'] = dumps(configdiffobjs, 'commands') if configdiffobjs else ''
        # banners = self._diff_banners(want_banners, have_banners)
        # diff['banner_diff'] = banners if banners else {}
        return diff

    def get_device_info(self):
        device_info = {}
        device_info['network_os'] = 'RouterOS'

        resource = self.get('/system resource print')
        data = to_text(resource, errors='surrogate_or_strict').strip()
        match = re.search(r'version: (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        routerboard = self.get('/system routerboard print')
        data = to_text(routerboard, errors='surrogate_or_strict').strip()
        match = re.search(r'model: (.+)$', data, re.M)
        if match:
            device_info['network_os_model'] = match.group(1)

        identity = self.get('/system identity print')
        data = to_text(identity, errors='surrogate_or_strict').strip()
        match = re.search(r'name: (.+)$', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    def get_config(self, source='running', format='text', flags=None):
        return self.get(b'/export compact')

    def edit_config(self, command):
        return

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        return json.dumps(result)
