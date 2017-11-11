#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2005-2010 ActiveState Software Inc.
# Copyright (c) 2013 Eddy Petrișor

"""Utilities for determining application-specific dirs.

Inspired by
<http://github.com/ActiveState/appdirs>
"""
# Dev Notes:
# - MSDN on where to store app data files:
#   http://support.microsoft.com/default.aspx?scid=kb;en-us;310294#XSLTH3194121123120121120120
# - Mac OS X: http://developer.apple.com/documentation/MacOSX/Conceptual/BPFileSystem/index.html
# - XDG spec for Un*x: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

__version__ = "0.1.0"
__version_info__ = tuple(int(segment) for segment in __version__.split("."))

import sys
import os

system = {"windows": False, 'macosx': False, 'linux': False}

if sys.platform == 'win32':
    system['windows'] = True
elif sys.platform == 'darwin':
    system['macosx'] = True
else:
    # this is a broad generalization. We may be able to get away with sys.platform.statswith('linux') and error
    # out on everything else. But this requires some testing.
    system['linux'] = True


def _get_folder(folder_type, app_name, app_author, version, roaming, use_virtualenv, create):
    if use_virtualenv and _in_virtualenv_folder():
        paths = [sys.prefix]

    elif system['windows']:
        if folder_type in ['user_data', 'user_config', 'user_state']:
            paths = [os.path.normpath(_get_win_folder(site=False, roaming=roaming, app_author=app_author))]
        elif folder_type == 'user_cache':
            # we'll follow the MSDN recommendation on local data, but since they're mum on caches,
            # we'll put them in LOCAL_APPDATA/author_name/Caches.
            path = os.path.normpath(_get_win_folder(site=False, roaming=False, app_author=app_author))
            paths = [os.path.join(path, 'Caches')]
        elif folder_type == 'user_logs':
            # Similar issue as with user caches. MSDN is no help.
            path = os.path.normpath(_get_win_folder(site=False, roaming=False, app_author=app_author))
            paths = [os.path.join(path, 'Logs')]
        else:  # folder_type in ['site_data', 'site_config']:
            paths = [os.path.normpath(_get_win_folder(site=True, roaming=roaming, app_author=app_author))]

    elif system['macosx']:
        if folder_type in ['user_data', 'user_config', 'user_state']:
            paths = [os.path.expanduser('~/Library/Application Support')]
        elif folder_type == 'user_cache':
            paths = [os.path.expanduser('~/Library/Caches')]
        elif folder_type == 'user_log':
            paths = [os.path.expanduser('~/Library/Logs')]
        else:  # folder_type in ['site_data', 'site_config']:
            paths = [os.path.expanduser('/Library/Application Support')]

    elif system['linux']:
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
        if version:
            final_path = os.path.join(final_path, version)

        if create and not os.path.exists():
            os.makedirs(final_path)

        final_paths.append(final_path)

    return final_paths


def user_data_dir(app_name, app_author=None, version=None, roaming=False, use_virtualenv=True, create=True):
    # type: (str, str, str, bool) -> str
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
    Return the full path to the user data dir for this application, using the host OS's convention.

    Note that we DO NOT create this directory if it doesn't exist.

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
        str: the full path to the user data dir for this application.
    """
    return _get_folder('user_config', app_name, app_author, version, roaming, use_virtualenv, create)[0]


def user_cache_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    r"""Return full path to the user-specific cache dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "opinion" (boolean) can be False to disable the appending of
            "Cache" to the base app data dir for Windows. See
            discussion below.

    Typical user cache directories are:
        Mac OS X:   ~/Library/Caches/<AppName>
        Unix:       ~/.cache/<AppName> (XDG default)
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Cache
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Cache

    On Windows the only suggestion in the MSDN docs is that local settings go in
    the `CSIDL_LOCAL_APPDATA` directory. This is identical to the non-roaming
    app data dir (the default returned by `user_data_dir` above). Apps typically
    put cache data somewhere *under* the given dir here. Some examples:
        ...\Mozilla\Firefox\Profiles\<ProfileName>\Cache
        ...\Acme\SuperApp\Cache\1.0
    OPINION: This function appends "Cache" to the `CSIDL_LOCAL_APPDATA` value.
    This can be disabled with the `opinion=False` option.
    """
    return _get_folder('user_cache', app_name, app_author, version, False, use_virtualenv, create)[0]


def user_state_dir(app_name=None, app_author=None, version=None, roaming=False, use_virtualenv=True, create=True):
    r"""Return full path to the user-specific state dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "roaming" (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user state directories are:
        Mac OS X:  same as user_data_dir
        Unix:      ~/.local/state/<AppName>   # or in $XDG_STATE_HOME, if defined
        Win *:     same as user_data_dir

    For Unix, we follow this Debian proposal <https://wiki.debian.org/XDGBaseDirectorySpecification#state>
    to extend the XDG spec and support $XDG_STATE_HOME.

    That means, by default "~/.local/state/<AppName>".
    """
    return _get_folder('user_state', app_name, app_author, version, roaming, use_virtualenv, create)[0]


def user_log_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    r"""Return full path to the user-specific log dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "opinion" (boolean) can be False to disable the appending of
            "Logs" to the base app data dir for Windows, and "log" to the
            base cache dir for Unix. See discussion below.

    Typical user log directories are:
        Mac OS X:   ~/Library/Logs/<AppName>
        Unix:       ~/.cache/<AppName>/log  # or under $XDG_CACHE_HOME if defined
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Logs
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Logs

    On Windows the only suggestion in the MSDN docs is that local settings
    go in the `CSIDL_LOCAL_APPDATA` directory. (Note: I'm interested in
    examples of what some windows apps use for a logs dir.)

    OPINION: This function appends "Logs" to the `CSIDL_LOCAL_APPDATA`
    value for Windows and appends "log" to the user cache dir for Unix.
    This can be disabled with the `opinion=False` option.
    """
    return _get_folder('user_log', app_name, app_author, version, False, use_virtualenv, create)


def site_data_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=False):
    """Return full path to the user-shared data dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "multipath" is an optional parameter only applicable to *nix
            which indicates that the entire list of data dirs should be
            returned. By default, the first item from XDG_DATA_DIRS is
            returned, or '/usr/local/share/<AppName>',
            if XDG_DATA_DIRS is not set

    Typical site data directories are:
        Mac OS X:   /Library/Application Support/<AppName>
        Unix:       /usr/local/share/<AppName> or /usr/share/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>   # Hidden, but writeable on Win 7.

    For Unix, this is using the $XDG_DATA_DIRS[0] default.

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    return _get_folder('site_data', app_name, app_author, version, False, use_virtualenv, create)


def site_config_dir(app_name=None, app_author=None, version=None, use_virtualenv=True, create=True):
    r"""Return full path to the user-shared data dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "multipath" is an optional parameter only applicable to *nix
            which indicates that the entire list of config dirs should be
            returned. By default, the first item from XDG_CONFIG_DIRS is
            returned, or '/etc/xdg/<AppName>', if XDG_CONFIG_DIRS is not set

    Typical site config directories are:
        Mac OS X:   same as site_data_dir
        Unix:       /etc/xdg/<AppName> or $XDG_CONFIG_DIRS[i]/<AppName> for each value in
                    $XDG_CONFIG_DIRS
        Win *:      same as site_data_dir
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)

    For Unix, this is using the $XDG_CONFIG_DIRS[0] default, if multipath=False

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    return _get_folder('site_config', app_name, app_author, version, False, use_virtualenv, create)


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

