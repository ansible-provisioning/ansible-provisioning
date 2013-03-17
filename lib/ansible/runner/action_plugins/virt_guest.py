# (c) 2012, Dag Wieers <dag@wieers.com>
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

import os
from ansible import utils
from ansible.runner.return_data import ReturnData

class ActionModule(object):

    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        ''' handler for file transfer operations '''

        # load up options
        options = utils.parse_kv(module_args)
        src = options.get('src', None)

        # template the source data locally & transfer
        try:
            xmldata = utils.template_from_file(self.runner.basedir, src, inject)
        except Exception, e:
            result = dict(failed=True, msg='%s (%s)' % (e, src))
            return ReturnData(conn=conn, comm_ok=False, result=result)
        tmp_src = self.runner._transfer_str(conn, tmp, 'source', xmldata)

        # fix file permissions when the copy is done as a different user
        if self.runner.sudo and self.runner.sudo_user != 'root':
            self.runner._low_level_exec_command(conn, "chmod a+r %s" % tmp_src, tmp)

        module_args = "%s src=%s" % (module_args, tmp_src)
        return self.runner._execute_module(conn, tmp, 'virt_guest', module_args, inject=inject)
