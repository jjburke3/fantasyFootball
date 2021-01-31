from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name = 'player filter module',
    ext_modules=cythonize("filterPlayer.pyx"),
    include_dirs=[numpy.get_include()],
    zip_safe=False,
)
