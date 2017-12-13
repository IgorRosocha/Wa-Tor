from setuptools import setup
from Cython.Build import cythonize
import numpy
from distutils.extension import Extension

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='wator',
    version='0.3',
    description='Wa-Tor simulation.',
    long_description=long_description,
    author='Miroslav Hrončok, Marek Suchánek, Igor Rosocha',
    author_email='miroslav.hroncok@fit.cvut.cz, suchama4@fit.cvut.cz, rosocigo@fit.cvut.cz',
    keywords='wator, simulation',
    license='GNU General Public License v3 (GPLv3)',
    url='https://github.com/IgorRosocha/Wa-Tor',
    package_data = {'wator': [
                        'static/pictures/*.svg',
                        'static/ui/*.ui'
        ]
    },
    python_requires='~=3.6',
    ext_modules = cythonize([Extension('wator._cwator', ['wator/_cwator.pyx'],
                                   include_dirs=[numpy.get_include()])],
                        language_level=3),
    include_dirs=[numpy.get_include()],
    install_requires=[
        'Cython',
        'NumPy',
        'PyQt5'
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3.6'
    ]
)
