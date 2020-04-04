import glob
import os
import sys
from subprocess import check_output, CalledProcessError
from setuptools import setup
from setuptools.command.build_py import build_py


# todo make sure this works
class CustomBuildExtCommand(build_py):
    """Customized setuptools install command - prints a friendly greeting."""

    def buildInkscapeExt(self):
        os.system("%s %s %s" % (sys.executable,
                                os.path.join("scripts", "boxes2inkscape"),
                                "inkex"))

    def updatePOT(self):
        os.system("%s %s %s" % (
            sys.executable,
            os.path.join("scripts", "boxes2pot"),
            "po/boxes.py.pot"))
        os.system("%s %s" % (
            "xgettext -L Python -j -o po/boxes.py.pot",
            "boxes/*.py scripts/boxesserver scripts/boxes"))

    def generate_mo_files(self):
        pos = glob.glob("po/*.po")

        for po in pos:
            lang = po.split(os.sep)[1][:-3].replace("-", "_")
            try:
                os.makedirs(os.path.join("locale", lang, "LC_MESSAGES"))
            except FileExistsError:
                pass
            os.system("msgfmt %s -o locale/%s/LC_MESSAGES/boxes.py.mo" % (po, lang))
            self.distribution.data_files.append(
                (os.path.join("share", "locale", lang, "LC_MESSAGES"),
                 [os.path.join("locale", lang, "LC_MESSAGES", "boxes.py.mo")]))

    def run(self):
        if self.distribution.data_files is None:
            self.distribution.data_files = []
        self.execute(self.updatePOT, ())
        self.execute(self.generate_mo_files, ())
        self.execute(self.buildInkscapeExt, ())

        if 'CURRENTLY_PACKAGING' in os.environ:
            # we are most probably building a Debian package
            # let us define a simple path!
            path="/usr/share/inkscape/extensions"
            self.distribution.data_files.append(
                (path,
                 [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
            self.distribution.data_files.append((path, ['scripts/boxes']))
        else:
            # we are surely not building a Debian package
            # then here is the default behavior:
            try:
                path = check_output(["inkscape", "-x"]).decode().strip()
                if not os.access(path, os.W_OK): # Can we install globally
                    # Not tested on Windows and Mac
                    path = os.path.expanduser("~/.config/inkscape/extensions")
                self.distribution.data_files.append(
                    (path,
                     [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
                self.distribution.data_files.append((path, ['scripts/boxes']))
            except CalledProcessError:
                pass # Inkscape is not installed

        build_py.run(self)


setup(
    name='seaborn-model-house',
    description='Generates SVG for laser cutters to create a model house',
    version="1.0.0",
    author="Michael Christenson",
    packages=['seaborn_model_house'],
    install_requires=[
        'pycairo',
        'cairocffi==0.8.0',
        'markdown',
        'lxml',
        'seaborn_table',
    ],
    cmdclass={
        'build_py': CustomBuildExtCommand,
    },
    test_suite="test",
    long_description=open('README.md').read(),
    package_data={
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Computer Aided Design",
    ],
    keywords=['glowforge', 'model', 'svg', 'laser cutter', 'model house'],
)
