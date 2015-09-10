import shlex

import six

from .. import errors
from ..utils import utils, check_resource


class ExecApiMixin(object):
    @check_resource
    def exec_create(self, container, cmd, stdout=True, stderr=True, tty=False,
                    privileged=False, user=''):
        if utils.compare_version('1.15', self._version) < 0:
            raise errors.InvalidVersion('Exec is not supported in API < 1.15')
        if privileged and utils.compare_version('1.19', self._version) < 0:
            raise errors.InvalidVersion(
                'Privileged exec is not supported in API < 1.19'
            )
        if user and utils.compare_version('1.19', self._version) < 0:
            raise errors.InvalidVersion(
                'User-specific exec is not supported in API < 1.19'
            )
        if isinstance(cmd, six.string_types):
            cmd = shlex.split(str(cmd))

        data = {
            'Container': container,
            'User': user,
            'Privileged': privileged,
            'Tty': tty,
            'AttachStdin': False,
            'AttachStdout': stdout,
            'AttachStderr': stderr,
            'Cmd': cmd
        }

        url = self._url('/containers/{0}/exec', container)
        res = self._post_json(url, data=data)
        return self._result(res, True)

    def exec_inspect(self, exec_id):
        if utils.compare_version('1.16', self._version) < 0:
            raise errors.InvalidVersion(
                'exec_inspect is not supported in API < 1.16'
            )
        if isinstance(exec_id, dict):
            exec_id = exec_id.get('Id')
        res = self._get(self._url("/exec/{0}/json", exec_id))
        return self._result(res, True)

    def exec_resize(self, exec_id, height=None, width=None):
        if utils.compare_version('1.15', self._version) < 0:
            raise errors.InvalidVersion('Exec is not supported in API < 1.15')
        if isinstance(exec_id, dict):
            exec_id = exec_id.get('Id')

        params = {'h': height, 'w': width}
        url = self._url("/exec/{0}/resize", exec_id)
        res = self._post(url, params=params)
        self._raise_for_status(res)

    def exec_start(self, exec_id, detach=False, tty=False, stream=False):
        if utils.compare_version('1.15', self._version) < 0:
            raise errors.InvalidVersion('Exec is not supported in API < 1.15')
        if isinstance(exec_id, dict):
            exec_id = exec_id.get('Id')

        data = {
            'Tty': tty,
            'Detach': detach
        }

        res = self._post_json(
            self._url('/exec/{0}/start', exec_id), data=data, stream=stream
        )
        return self._get_result_tty(stream, res, tty)
