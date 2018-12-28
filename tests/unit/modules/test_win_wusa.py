# -*- coding: utf-8 -*-

# Import Python Libs
from __future__ import absolute_import, unicode_literals, print_function

# Import Salt Testing Libs
from tests.support.helpers import destructiveTest
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, patch, MagicMock
from tests.support.unit import TestCase, skipIf

# Import Salt Libs
import salt.utils.platform
import salt.modules.win_wusa as win_wusa
from salt.exceptions import CommandExecutionError


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(not salt.utils.platform.is_windows(), 'System is not Windows')
class WinWusaTestCase(TestCase, LoaderModuleMockMixin):
    def setup_loader_modules(self):
        return {win_wusa: {}}

    def test_is_installed_false(self):
        mock_retcode = MagicMock(return_value=1)
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            self.assertFalse(win_wusa.is_installed('KB123456'))

    def test_is_installed_true(self):
        mock_retcode = MagicMock(return_value=0)
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            self.assertTrue(win_wusa.is_installed('KB123456'))

    def test_list(self):
        ret = {'pid': 1,
               'retcode': 0,
               'stderr': '',
               'stdout': '[{"HotFixID": "KB123456"}, '
                         '{"HotFixID": "KB123457"}]'}
        mock_all = MagicMock(return_value=ret)
        with patch.dict(win_wusa.__salt__, {'cmd.run_all': mock_all}):
            expected = ['KB123456', 'KB123457']
            returned = win_wusa.list()
            self.assertListEqual(expected, returned)

    def test_install(self):
        mock_retcode = MagicMock(return_value=0)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            self.assertTrue(win_wusa.install(path))
        mock_retcode.assert_called_once_with(
            ['wusa.exe', path, '/quiet', '/norestart'], ignore_retcode=True)

    def test_install_restart(self):
        mock_retcode = MagicMock(return_value=0)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            self.assertTrue(win_wusa.install(path, restart=True))
        mock_retcode.assert_called_once_with(
            ['wusa.exe', path, '/quiet', '/forcerestart'], ignore_retcode=True)

    def test_install_already_installed(self):
        mock_retcode = MagicMock(return_value=2359302)
        path = 'C:\\KB123456.msu'
        name = 'KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            with self.assertRaises(CommandExecutionError) as excinfo:
                win_wusa.install(path)
        mock_retcode.assert_called_once_with(
            ['wusa.exe', path, '/quiet', '/norestart'], ignore_retcode=True)
        self.assertEqual('{0} is already installed'.format(name),
                         excinfo.exception.strerror)

    def test_install_error_87(self):
        mock_retcode = MagicMock(return_value=87)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            with self.assertRaises(CommandExecutionError) as excinfo:
                win_wusa.install(path)
        mock_retcode.assert_called_once_with(
            ['wusa.exe', path, '/quiet', '/norestart'], ignore_retcode=True)
        self.assertEqual('Unknown error', excinfo.exception.strerror)

    def test_install_error_other(self):
        mock_retcode = MagicMock(return_value=1234)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            with self.assertRaises(CommandExecutionError) as excinfo:
                win_wusa.install(path)
        mock_retcode.assert_called_once_with(
            ['wusa.exe', path, '/quiet', '/norestart'], ignore_retcode=True)
        self.assertEqual('Unknown error: 1234', excinfo.exception.strerror)

    def test_uninstall_kb(self):
        mock_retcode = MagicMock(return_value=0)
        kb = 'KB123456'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}), \
                patch("os.path.exists", MagicMock(return_value=False)):
            self.assertTrue(win_wusa.uninstall(kb))
        mock_retcode.assert_called_once_with(
            ['wusa.exe', '/uninstall', '/quiet', '/kb:{0}'.format(kb[2:]), '/norestart'],
            ignore_retcode=True)

    def test_uninstall_path(self):
        mock_retcode = MagicMock(return_value=0)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}), \
                patch("os.path.exists", MagicMock(return_value=True)):
            self.assertTrue(win_wusa.uninstall(path))
        mock_retcode.assert_called_once_with(
            ['wusa.exe', '/uninstall', '/quiet', path, '/norestart'],
            ignore_retcode=True)

    def test_uninstall_path_restart(self):
        mock_retcode = MagicMock(return_value=0)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}), \
             patch("os.path.exists", MagicMock(return_value=True)):
            self.assertTrue(win_wusa.uninstall(path, restart=True))
        mock_retcode.assert_called_once_with(
            ['wusa.exe', '/uninstall', '/quiet', path, '/forcerestart'],
            ignore_retcode=True)

    def test_uninstall_already_uninstalled(self):
        mock_retcode = MagicMock(return_value=2359303)
        kb = 'KB123456'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}):
            with self.assertRaises(CommandExecutionError) as excinfo:
                win_wusa.uninstall(kb)
        mock_retcode.assert_called_once_with(
            ['wusa.exe', '/uninstall', '/quiet', '/kb:{0}'.format(kb[2:]), '/norestart'],
            ignore_retcode=True)
        self.assertEqual('{0} not installed'.format(kb),
                         excinfo.exception.strerror)

    def test_uninstall_path_error_other(self):
        mock_retcode = MagicMock(return_value=1234)
        path = 'C:\\KB123456.msu'
        with patch.dict(win_wusa.__salt__, {'cmd.retcode': mock_retcode}), \
                patch("os.path.exists", MagicMock(return_value=True)), \
                self.assertRaises(CommandExecutionError) as excinfo:
            win_wusa.uninstall(path)
        mock_retcode.assert_called_once_with(
            ['wusa.exe', '/uninstall', '/quiet', path, '/norestart'],
            ignore_retcode=True)
        self.assertEqual('Unknown error: 1234', excinfo.exception.strerror)
