#!/usr/bin/env python
"""Python Control Systems Library

The Python Control Systems Library, python-control,
is a python module that implements basic operations
for analysis and design of feedback control systems.

Features:
Linear input/output systems in state space and frequency domain
Block diagram algebra: serial, parallel and feedback interconnections
Time response: initial, step, impulse
Frequency response: Bode and Nyquist plots
Control analysis: stability, reachability, observability, stability margins
Control design: eigenvalue placement, linear quadratic regulator
Estimator design: linear quadratic estimator (Kalman filter)

Fork of http://sourceforge.net/projects/python-control/
Source code for fork at: https://github.com/jgoppert/python-control

This fork is focused on improving unit testing and
supporting pypi packaging and should be merged back
with upstream soon.

"""

from __future__ import division, print_function

DOCLINES = __doc__.split("\n")

import os
import sys
import subprocess


if sys.version_info[:2] < (2, 6) or (3, 0) <= sys.version_info[0:2] < (3, 2):
    raise RuntimeError("Python version 2.6, 2.7 or >= 3.2 required.")

if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins


CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: C
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

MAJOR = 0
MINOR = 6
MICRO = 1
ISRELEASED = True
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

# This is a bit hackish: we are setting a global variable so that the main
# control __init__ can detect if it is being loaded by the setup routine, to
# avoid attempting to load components that aren't built yet.  While ugly, it's
# a lot more robust than what was previously being used.
builtins.__CONTROL_SETUP__ = True


def get_version_info():
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of control.version messes up
    # the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('control/version.py'):
        # must be a source distribution, use existing version file
        try:
            from control.version import git_revision as GIT_REVISION
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "control/version.py and the build directory "
                              "before building.")
    else:
        GIT_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev-' + GIT_REVISION[:7]

    return FULLVERSION, GIT_REVISION


def write_version_py(filename='control/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM CONTROL SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    FULLVERSION, GIT_REVISION = get_version_info()

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version': FULLVERSION,
                       'git_revision': GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    config.add_subpackage('control')
    config.get_version('control/version.py')  # sets config.version
    return config


def check_submodules():
    """ verify that the submodules are checked out and clean
        use `git submodule update --init`; on failure
    """
    if not os.path.exists('.git'):
        return
    with open('.gitmodules') as f:
        for l in f:
            if 'path' in l:
                p = l.split('=')[-1].strip()
                if not os.path.exists(p):
                    raise ValueError('Submodule %s missing' % p)

    proc = subprocess.Popen(['git', 'submodule', 'status'],
                            stdout=subprocess.PIPE)
    status, _ = proc.communicate()
    status = status.decode("ascii", "replace")
    for line in status.splitlines():
        if line.startswith('-') or line.startswith('+'):
            raise ValueError('Submodule not clean: %s' % line)

from distutils.command.sdist import sdist


class sdist_checked(sdist):
    """ check submodules on sdist to prevent incomplete tarballs """
    def run(self):
        # control had no submodules currently
        # check_submodules()
        sdist.run(self)


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # Rewrite the version file everytime
    write_version_py()

    metadata = dict(
        name='control',
        maintainer="James Goppert",
        maintainer_email="james.goppert@gmail.com",
        description=DOCLINES[0],
        long_description="\n".join(DOCLINES[2:]),
        url='https://github.com/jgoppert/python-control',
        author='Richard Murray',
        author_email='murray@cds.caltech.edu',
        download_url='https://github.com/jgoppert/python-control',
        license='BSD',
        classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
        platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
        cmdclass={"sdist": sdist_checked},
        requires=['numpy', 'scipy'],
    )

    # Run build
    if len(sys.argv) >= 2 and \
            ('--help' in sys.argv[1:] or
             sys.argv[1] in ('--help-commands', 'egg_info', '--version',
             'clean')):
        # Use setuptools for these commands (they don't work well or at all
        # with distutils).  For normal builds use distutils.
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup

        FULLVERSION, GIT_REVISION = get_version_info()
        metadata['version'] = FULLVERSION
    elif len(sys.argv) >= 2 and sys.argv[1] == 'bdist_wheel':
        # bdist_wheel needs setuptools
        import setuptools
        setuptools  # reference once for pyflakes
        from numpy.distutils.core import setup
        metadata['configuration'] = configuration
    else:
        from numpy.distutils.core import setup
        metadata['configuration'] = configuration

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)
    return


if __name__ == '__main__':
    setup_package()
