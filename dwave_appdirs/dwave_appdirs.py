#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides an API for determining application specific directories for data, config, logs, etc.

Module contents:
    user_data_dir()
    user_config_dir()
    user_cache_dir()
    user_state_dir()
    user_log_dir()
    site_data_dirs()
    site_config_dirs()

This code is inspired by and builds on top of code from <http://github.com/ActiveState/appdirs>

"""
# Dev Notes:
# - MSDN on where to store app data files:
#   http://support.microsoft.com/default.aspx?scid=kb;en-us;310294#XSLTH3194121123120121120120
# - Mac OS X: http://developer.apple.com/documentation/MacOSX/Conceptual/BPFileSystem/index.html
# - XDG spec for Un*x: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
import sys
import os

WINDOWS = MACOSX = LINUX = False
if sys.platform == 'win32':
    WINDOWS = True
elif sys.platform == 'darwin':
    MACOSX = True
else:
    # this is a broad generalization. We may be able to get away with sys.platform.statswith('linux') and error
    # out on everything else. But this requires some testing.
    LINUX = True


def user_data_dir(app_name, app_author=None, version=None, roaming=False, use_virtualenv=True, create=True):
    """
    Return the full path to the user data dir for this application, using a virtualenv location as a base, if it is
    exists, and falling back to the host OS's convention if it doesn't.

    If using a virtualenv, the path returned is /path/to/virtualenv/data/app_name

    Typical user data directories are:
        Mac OS X:               ~/Library/Application Support/<app_name>
        Unix:                   ~/.local/share/<app_name>    # or $XDG_DATA_HOME/<app_name>, if defined.
        Win XP (not roaming):   C:\Documents and Settings\<username>\Application Data\<app_author>\<app_name>
        Win XP (roaming):       C:\Documents and Settings\<username>\Local Settings\Application Data\<app_author>\<app_name>
        Win 7  (not roaming):   C:\Users\<username>\AppData\Local\<app_author>\<app_name>
        Win 7  (roaming):       C:\Users\<username>\AppData\Roaming\<app_author>\<app_name>

    For Unix, we follow the XDG spec and support $XDG_DATA_HOME.
    That means, by default "~/.local/share/<AppName>".


    Args:
        str app_name: Name of the application. Will be appended to the base user data path.
        str app_author: Only used in Windows when not in a virtualenv, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool roaming: roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be synchronized on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx> for a discussion of issues.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the user data dir for this application.
    """
    return _get_folder('user_data', app_name, app_author, version, roaming, use_virtualenv, create)[0]


def user_config_dir(app_name, app_author=None, version=None, roaming=False, use_virtualenv=True, create=True):
    """
    Return the full path to the user data dir for this application, using a virtualenv location as a base, if it is
    exists, and falling back to the host OS's convention if it doesn't.

    If using a virtualenv, the path returned is /path/to/virtualenv/config/app_name

    Typical user config directories are:
        Mac OS X:               same as user_data_dir
        Unix:                   ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
        Win *:                  same as user_data_dir

    For Unix, we follow the XDG spec and support $XDG_CONFIG_HOME.
    That means, by default "~/.config/<AppName>".

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool roaming: roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be synchronized on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx> for a discussion of issues.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the user config dir for this application.
    """
    return _get_folder('user_config', app_name, app_author, version, roaming, use_virtualenv, create)[0]


def user_cache_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    """
    Return the full path to the user data dir for this application, using a virtualenv location as a base, if it is
    exists, and falling back to the host OS's convention if it doesn't.

    If using a virtualenv, the path returned is /path/to/virtualenv/cache/app_name

    Typical user cache directories are:
        Mac OS X:   ~/Library/Caches/<AppName>
        Unix:       ~/.cache/<AppName> (XDG default)
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Cache
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Cache

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the user cache dir for this application.

    """
    return _get_folder('user_cache', app_name, app_author, version, False, use_virtualenv, create)[0]


def user_state_dir(app_name=None, app_author=None, version=None, roaming=False, use_virtualenv=True, create=True):
    """
    Return the full path to the user data dir for this application, using a virtualenv location as a base, if it is
    exists, and falling back to the host OS's convention if it doesn't.

    If using a virtualenv, the path returned is /path/to/virtualenv/state/app_name

    Typical user state directories are:
        Mac OS X:  same as user_data_dir
        Unix:      ~/.local/state/<AppName>   # or in $XDG_STATE_HOME, if defined
        Win *:     same as user_data_dir

    For Unix, we follow this Debian proposal <https://wiki.debian.org/XDGBaseDirectorySpecification#state>
    to extend the XDG spec and support $XDG_STATE_HOME.

    That means, by default "~/.local/state/<AppName>".

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool roaming: roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be synchronized on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx> for a discussion of issues.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the user state dir for this application.
    """
    return _get_folder('user_state', app_name, app_author, version, roaming, use_virtualenv, create)[0]


def user_log_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    """
    Return the full path to the user log dir for this application, using a virtualenv location as a base, if it is
    exists, and falling back to the host OS's convention if it doesn't.

    If using a virtualenv, the path returned is /path/to/virtualenv/log/app_name

    Typical user log directories are:
        Mac OS X:   ~/Library/Logs/<AppName>
        Unix:       ~/.cache/<AppName>/log  # or under $XDG_CACHE_HOME if defined
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Logs
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Logs

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the user log dir for this application.
    """
    return _get_folder('user_log', app_name, app_author, version, False, use_virtualenv, create)[0]


def site_data_dirs(app_name=None, app_author=None, version=None, use_virtualenv=True, create=False):
    """
    Return the full path to the OS wide data dir for this application.

    Typical site data directories are:
        Mac OS X:   /Library/Application Support/<AppName>
        Unix:       /usr/local/share/<AppName> or /usr/share/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>   # Hidden, but writeable on Win 7.

    For Unix, this is using the $XDG_DATA_DIRS[0] default.
    ..warning:: Do not use this on Windows Vista. See the Vista-Fail note above for why.

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the site data dir for this application.
    """
    return _get_folder('site_data', app_name, app_author, version, False, use_virtualenv, create)


def site_config_dirs(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    """
    Return the full path to the OS wide config dir for this application.

    Typical site data directories are:
        Mac OS X:   /Library/Application Support/<AppName>
        Unix:       /usr/local/share/<AppName> or /usr/share/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>   # Hidden, but writeable on Win 7.

    For Unix, this is using the $XDG_DATA_DIRS[0] default.
    ..warning:: Do not use this on Windows Vista. See the Vista-Fail note above for why.

    Args:
        str app_name: Name of the application. Will be appended to the base user config path.
        str app_author: Only used in Windows, name of the application author.
        str version: If given, the application version identifier will be appended to the app_name.
        bool use_virtualenv: If True and we're running inside of a virtualenv, return a path relative to that
            environment.
        bool create: If True, the folder is created if it does not exist before the path is returned.

    Returns:
        str: the full path to the site config dir for this application.
    """
    return _get_folder('site_config', app_name, app_author, version, False, use_virtualenv, create)


def _get_folder(folder_type, app_name, app_author, version, roaming, use_virtualenv, create):
    """
    Get the directory corresponding to the appropriate folder type and operating system.
    The folder is returned, with the app_name, and in the case of windows app_author appended to it.
    If version is not None, it is appended to app_name to allow for multiple versions to run in the same place.

    Since some operating systems have more than one appropriate folder of a given time (e.g. site_data on linux),
    A list is returned. It is up to calling functions to handle the contents of this list.

    Args:
        str folder_type: Folder type, must be one of
            'user_data' | 'user_config' | 'user_state' | 'user_cache' | 'user_log' | 'site_data' | 'site_config'
        str app_name: Name of the app, the returned dir has os.path.basename == app_name
        str app_author: Name of app author, only used in Windows.
        str version: App version, appended to app_name
        bool roaming: Whether or not the Windows user is roaming.
        bool use_virtualenv: If True and a virtualenv is activated, use the virtualenv path instead of the OS
            convention.
        bool create: If True, create the directory if it doesn't exist. In the case of lists of directories, all folders
            are created.

    Returns:
        list: A list of paths.

    """
    if not folder_type.startswith('site') and use_virtualenv and _in_virtualenv_folder():
        sub_folder = folder_type.split('_')[1]  # data | config | state | log | cache
        paths = [os.path.join(sys.prefix, sub_folder)]

    elif WINDOWS:
        if folder_type in ['user_data', 'user_config', 'user_state']:
            paths = [os.path.normpath(_get_win_folder(site=False, roaming=roaming, app_author=app_author))]
        elif folder_type == 'user_cache':
            # we'll follow the MSDN recommendation on local data, but since they're mum on caches,
            # we'll put them in LOCAL_APPDATA/author_name/app_name/Caches.
            path = os.path.normpath(_get_win_folder(site=False, roaming=False, app_author=app_author))
            paths = [os.path.join(path, 'Caches')]
        elif folder_type == 'user_logs':
            # Similar issue as with user caches. MSDN is no help.
            path = os.path.normpath(_get_win_folder(site=False, roaming=False, app_author=app_author))
            paths = [os.path.join(path, 'Logs')]
        else:  # folder_type in ['site_data', 'site_config']:
            paths = [os.path.normpath(_get_win_folder(site=True, roaming=roaming, app_author=app_author))]

    elif MACOSX:
        if folder_type in ['user_data', 'user_config', 'user_state']:
            paths = [os.path.expanduser('~/Library/Application Support')]
        elif folder_type == 'user_cache':
            paths = [os.path.expanduser('~/Library/Caches')]
        elif folder_type == 'user_log':
            paths = [os.path.expanduser('~/Library/Logs')]
        else:  # folder_type in ['site_data', 'site_config']:
            paths = [os.path.expanduser('/Library/Application Support')]

    elif LINUX:
        if folder_type == 'user_data':
            paths = [os.getenv('XDG_DATA_HOME', os.path.expanduser("~/.local/share"))]
        elif folder_type == 'user_config':
            paths = [os.getenv('XDG_CONFIG_HOME', os.path.expanduser("~/.config"))]
        elif folder_type == 'user_state':
            paths = [os.getenv('XDG_STATE_HOME', os.path.expanduser("~/.local/state"))]
        elif folder_type == 'user_cache':
            paths = [os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))]
        elif folder_type == 'site_data':
            path = os.getenv('XDG_DATA_DIRS', os.pathsep.join(['/usr/local/share', '/usr/share']))
            paths = [os.path.expanduser(x.rstrip(os.sep)) for x in path.split(os.pathsep)]
        else:  # site_config
            path = os.getenv('XDG_CONFIG_DIRS', '/etc/xdg')
            paths = [os.path.expanduser(x.rstrip(os.sep)) for x in path.split(os.pathsep)]
    else:
        raise RuntimeError('Unsupported operating system: {}'.format(sys.platform))

    final_paths = []
    for path in paths:
        final_path = os.path.join(path, app_name)
        if version is not None:
            final_path = os.path.join(final_path, version)

        if create and not os.path.exists(final_path):
            os.makedirs(final_path)

        final_paths.append(final_path)

    return final_paths


def _in_virtualenv_folder():
    """
    Determine if we're in a virtual env.

    If sys.real_prefix exists, we're are in a virtualenv, and sys.prefix is the virtualenv path, while
    sys.real_prefix is the 'system' python.
    if sys.real_prefix does not exist, it could be because we're in python 3 and the user is using
    the built in venv module instead of virtualenv. In this case a sys.base_prefix attribute always exists, and is
    is different from sys.prefix.

    In either case, the path we want in case we are in a virtualenv is sys.prefix.

    Returns:
        bool: True if we are running in a virtual environment, and False otherwise.
    """
    return hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix


def _get_win_folder(site, roaming, app_author):
    import ctypes

    if app_author is None:
        raise RuntimeError('app_author must be provided on Windows')

    csidl_consts = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
    }

    if site:
        csidl_const = csidl_consts['CSIDL_COMMON_APPDATA']
    elif roaming:
        csidl_const = csidl_consts['CSIDL_APPDATA']
    else:
        csidl_const = csidl_consts['CSIDL_LOCAL_APPDATA']

    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    # Oren: This bug is not publicly available!
    has_high_char = False
    for c in buf:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf2 = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return os.path.join(buf.value, app_author)
