"""
Test dwave_appdirs.

Since some of the dwave_appdirs functionality is OS specific, this module can only get 100% coverage if it is run on
all three operating systems: Windows, Linux, and macOS. Thus, coverage tools will need to merge reports from different
runs.

"""
import os
import sys
import shutil
import unittest

import virtualenv
import dwave_appdirs as dirs

_PY2 = sys.version_info[0] == 2
if _PY2:
    def itervalues(d):
        return d.itervalues()
else:
    def itervalues(d):
        return iter(d.values())


class TestDwaveAppDirs(unittest.TestCase):
    """
    In mac os x, the parameters we care about are version (None | string), use_virtualenv (bool), and create (bool).
    The following are the 8 corresponding test cases, per folder type. Since the the test name is described in the
    function name, docstrings are omitted.
    """

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.app_name = "test_app"

        # we can't just use sys.platform because on linux it could be either linux2 or just linux
        # (https://docs.python.org/2/library/sys.html#sys.platform)
        # If we're masking linux, might as well mask darwin with mac os.
        if sys.platform.startswith('linux'):
            self.platform = 'linux'
        elif sys.platform == 'darwin':
            self.platform = 'mac_os'
        else:
            self.platform = 'win32'

        self.base_paths = self._expected_base_paths()

    def _expected_base_paths(self):
        mac_os_app_support = os.path.expanduser('~/Library/Application Support/')
        mac_os_site_app_support = '/Library/Application Support'
        base_names = dict(
            mac_os=dict(
                user_data=mac_os_app_support,
                user_config=mac_os_app_support,
                user_state=mac_os_app_support,
                user_cache=os.path.expanduser('~/Library/Caches'),
                user_log=os.path.expanduser('~/Library/Logs'),
                site_data=[mac_os_site_app_support],
                site_config=[mac_os_site_app_support]
            ),
            linux=dict(
                user_data=mac_os_app_support,
                user_config=mac_os_app_support,
                user_state=mac_os_app_support,
                user_cache=os.path.expanduser('~/Library/Caches'),
                user_log=os.path.expanduser('~/Library/Logs'),
                site_data=[mac_os_site_app_support],
                site_config=[mac_os_site_app_support]
            )
        )

        # add virtualenv expectations. When there is no actual virtualenv, we expect the use_virtualenv parameter
        # to do nothing.
        for paths in itervalues(base_names):
            paths['user_data_venv'] = paths['user_data']
            paths['user_config_venv'] = paths['user_config']
            paths['user_state_venv'] = paths['user_state']
            paths['user_cache_venv'] = paths['user_cache']
            paths['user_log_venv'] = paths['user_log']

        return base_names

    #####################################################
    # user_data_dir.
    #####################################################
    def test_user_data_no_version_no_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_data'], self.app_name)
        self.assertEqual(expected, dirs.user_data_dir(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_user_data_no_version_no_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_data'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_data_dir(self.app_name, version=None, use_virtualenv=False, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_data_no_version_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_data_venv'], self.app_name)
        self.assertEqual(expected, dirs.user_data_dir(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_user_data_no_version_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_data_venv'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_data_dir(self.app_name, version=None, use_virtualenv=True, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_data_version_no_venv_no_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_data'], '{}_{}'.format(self.app_name, version))
        self.assertEqual(expected,
                         dirs.user_data_dir(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_user_data_version_no_venv_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_data'], '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        result = dirs.user_data_dir(self.app_name, version=version, use_virtualenv=False, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_data_version_venv_no_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_data_venv'],
                                '{}_{}'.format(self.app_name, version))
        result = dirs.user_data_dir(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    def test_user_data_version_venv_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_data_venv'],
                                '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertFalse(os.path.exists(expected))
        result = dirs.user_data_dir(self.app_name, version=version, use_virtualenv=True, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    #####################################################
    # user_cache_dir.
    #####################################################
    def test_user_cache_no_version_no_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_cache'], self.app_name)
        self.assertEqual(expected, dirs.user_cache_dir(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_user_cache_no_version_no_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_cache'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_cache_dir(self.app_name, version=None, use_virtualenv=False, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_cache_no_version_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_cache_venv'], self.app_name)
        self.assertEqual(expected, dirs.user_cache_dir(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_user_cache_no_version_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_cache_venv'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_cache_dir(self.app_name, version=None, use_virtualenv=True, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_cache_version_no_venv_no_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_cache'], '{}_{}'.format(self.app_name, version))
        self.assertEqual(expected,
                         dirs.user_cache_dir(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_user_cache_version_no_venv_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_cache'], '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        result = dirs.user_cache_dir(self.app_name, version=version, use_virtualenv=False, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_cache_version_venv_no_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_cache_venv'],
                                '{}_{}'.format(self.app_name, version))
        result = dirs.user_cache_dir(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    def test_user_cache_version_venv_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_cache_venv'],
                                '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertFalse(os.path.exists(expected))
        result = dirs.user_cache_dir(self.app_name, version=version, use_virtualenv=True, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    #####################################################
    # user_config_dir
    #####################################################
    def test_user_config_no_version_no_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_config'], self.app_name)
        self.assertEqual(expected,
                         dirs.user_config_dir(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_user_config_no_version_no_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_config'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_config_dir(self.app_name, version=None, use_virtualenv=False, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_config_no_version_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_config_venv'], self.app_name)
        self.assertEqual(expected, dirs.user_config_dir(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_user_config_no_version_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_config_venv'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_config_dir(self.app_name, version=None, use_virtualenv=True, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_config_version_no_venv_no_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_config'], '{}_{}'.format(self.app_name, version))
        self.assertEqual(expected,
                         dirs.user_config_dir(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_user_config_version_no_venv_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_config'], '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        result = dirs.user_config_dir(self.app_name, version=version, use_virtualenv=False, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_config_version_venv_no_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_config_venv'],
                                '{}_{}'.format(self.app_name, version))
        result = dirs.user_config_dir(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    def test_user_config_version_venv_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_config_venv'],
                                '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertFalse(os.path.exists(expected))
        result = dirs.user_config_dir(self.app_name, version=version, use_virtualenv=True, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    #####################################################
    # user_state_dir
    #####################################################
    def test_user_state_no_version_no_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_state'], self.app_name)
        self.assertEqual(expected, dirs.user_state_dir(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_user_state_no_version_no_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_state'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_state_dir(self.app_name, version=None, use_virtualenv=False, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_state_no_version_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_state_venv'], self.app_name)
        self.assertEqual(expected, dirs.user_state_dir(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_user_state_no_version_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_state_venv'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_state_dir(self.app_name, version=None, use_virtualenv=True, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_state_version_no_venv_no_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_state'], '{}_{}'.format(self.app_name, version))
        self.assertEqual(expected,
                         dirs.user_state_dir(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_user_state_version_no_venv_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_state'], '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        result = dirs.user_state_dir(self.app_name, version=version, use_virtualenv=False, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_state_version_venv_no_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_state_venv'],
                                '{}_{}'.format(self.app_name, version))
        result = dirs.user_state_dir(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    def test_user_state_version_venv_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_state_venv'],
                                '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertFalse(os.path.exists(expected))
        result = dirs.user_state_dir(self.app_name, version=version, use_virtualenv=True, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    #####################################################
    # user_log_dir
    #####################################################
    def test_user_log_no_version_no_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_log'], self.app_name)
        self.assertEqual(expected, dirs.user_log_dir(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_user_log_no_version_no_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_log'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_log_dir(self.app_name, version=None, use_virtualenv=False, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_log_no_version_venv_no_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_log_venv'], self.app_name)
        self.assertEqual(expected, dirs.user_log_dir(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_user_log_no_version_venv_create(self):
        expected = os.path.join(self.base_paths[self.platform]['user_log_venv'], self.app_name)
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertEqual(expected, dirs.user_log_dir(self.app_name, version=None, use_virtualenv=True, create=True))
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_log_version_no_venv_no_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_log'], '{}_{}'.format(self.app_name, version))
        self.assertEqual(expected,
                         dirs.user_log_dir(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_user_log_version_no_venv_create(self):
        version = "1.0"
        expected = os.path.join(self.base_paths[self.platform]['user_log'], '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        result = dirs.user_log_dir(self.app_name, version=version, use_virtualenv=False, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    def test_user_log_version_venv_no_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_log_venv'],
                                '{}_{}'.format(self.app_name, version))
        result = dirs.user_log_dir(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    def test_user_log_version_venv_create(self):
        version = '1.0'
        expected = os.path.join(self.base_paths[self.platform]['user_log_venv'],
                                '{}_{}'.format(self.app_name, version))
        if os.path.exists(expected):
            os.rmdir(expected)
        self.assertFalse(os.path.exists(expected))
        result = dirs.user_log_dir(self.app_name, version=version, use_virtualenv=True, create=True)
        self.assertEqual(expected, result)
        self.assertTrue(os.path.exists(expected))
        os.rmdir(expected)

    #####################################################
    # site_data_dirs. Not testing create=True since we don't know if we have permissions.
    #####################################################
    def test_site_data_no_version_no_venv_no_create(self):
        expected = [os.path.join(d, self.app_name) for d in self.base_paths[self.platform]['site_data']]
        self.assertEqual(expected, dirs.site_data_dirs(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_site_data_no_version_venv_no_create(self):
        expected = [os.path.join(d, self.app_name) for d in self.base_paths[self.platform]['site_data']]
        self.assertEqual(expected, dirs.site_data_dirs(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_site_data_version_no_venv_no_create(self):
        version = "1.0"
        expected = [os.path.join(d, '{}_{}'.format(self.app_name, version)) for d in self.base_paths[self.platform]['site_data']]
        self.assertEqual(expected,
                         dirs.site_data_dirs(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_site_data_version_venv_no_create(self):
        version = '1.0'
        expected = [os.path.join(d, '{}_{}'.format(self.app_name, version)) for d in self.base_paths[self.platform]['site_data']]
        result = dirs.site_data_dirs(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)

    #####################################################
    # site_config_dirs. Not testing create=True since we don't know if we have permissions.
    #####################################################
    def test_site_config_no_version_no_venv_no_create(self):
        expected = [os.path.join(d, self.app_name) for d in self.base_paths[self.platform]['site_config']]
        self.assertEqual(expected,
                         dirs.site_config_dirs(self.app_name, version=None, use_virtualenv=False, create=False))

    def test_site_config_no_version_venv_no_create(self):
        expected = [os.path.join(d, self.app_name) for d in self.base_paths[self.platform]['site_config']]
        self.assertEqual(expected,
                         dirs.site_config_dirs(self.app_name, version=None, use_virtualenv=True, create=False))

    def test_site_config_version_no_venv_no_create(self):
        version = "1.0"
        expected = [os.path.join(d, '{}_{}'.format(self.app_name, version))
                    for d in self.base_paths[self.platform]['site_config']]
        self.assertEqual(expected,
                         dirs.site_config_dirs(self.app_name, version=version, use_virtualenv=False, create=False))

    def test_site_config_version_venv_no_create(self):
        version = '1.0'
        expected = [os.path.join(d, '{}_{}'.format(self.app_name, version))
                    for d in self.base_paths[self.platform]['site_config']]
        result = dirs.site_config_dirs(self.app_name, version=version, use_virtualenv=True, create=False)
        self.assertEqual(expected, result)


class TestDwaveAppDirsVirtualEnv(TestDwaveAppDirs):

    virtualenv_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_venv')

    def __init__(self, *args, **kwargs):
        TestDwaveAppDirs.__init__(self, *args, **kwargs)

    def _expected_base_paths(self):
        base_paths = TestDwaveAppDirs._expected_base_paths(self)

        # add virtualenv expectations.
        for paths in itervalues(base_paths):
            paths['user_data_venv'] = os.path.join(self.virtualenv_dir, 'data')
            paths['user_config_venv'] = os.path.join(self.virtualenv_dir, 'config')
            paths['user_state_venv'] = os.path.join(self.virtualenv_dir, 'state')
            paths['user_cache_venv'] = os.path.join(self.virtualenv_dir, 'cache')
            paths['user_log_venv'] = os.path.join(self.virtualenv_dir, 'log')

        return base_paths

    @classmethod
    def setUpClass(cls):
        virtualenv.create_environment(cls.virtualenv_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.virtualenv_dir)

    def setUp(self):
        activate_script = os.path.join(self.virtualenv_dir, 'bin', 'activate_this.py')
        execfile(activate_script, dict(__file__=activate_script))


if __name__ == '__main__':
    unittest.main()
