# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Daniel Mizyrycki (mzdaniel@glidelink.net)`


    tests.integration.cli.ssh.test_grains
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test salt-ssh grains id work for localhost. (gh #16129)

    $ salt-ssh localhost grains.get id
    localhost:
        localhost
'''
# Import Python libs
from __future__ import absolute_import


def test_grains_id(session_salt_ssh):
    '''
    Test salt-ssh grains id work for localhost. (gh #16129)

    $ salt-ssh localhost grains.get id
    localhost:
        localhost
    '''
    expected = 'localhost'
    cmd = session_salt_ssh.run_sync('grains.get', 'id')
    assert expected == cmd
