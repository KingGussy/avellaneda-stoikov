from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np                      

extensions = [
    Extension(
        name="engine.queue",
        sources=["src/engine/queue.pyx"],
        include_dirs=[np.get_include()],  #→ numpy/arrayobject.h found
    ),
]

setup(
    ext_modules=cythonize(
        extensions,
        language_level="3",
    ),
)