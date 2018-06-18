import os
from setuptools import setup, find_packages

__version__ = '1.0.0'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'smplot',
    version = __version__,
    author = 'Qi Fu',
    author_email = 'qi@xmotors.ai',
    url = 'https://github.com/vgm64/gmplot',
    description = 'Plotting data with Google Satellite Maps, Thanks gmplot!!',
    long_description=read('README.rst'),
    license='MIT',
    keywords='python wrapper google maps',
    packages = find_packages(),
    include_package_data=True,
    package_data = {
        'smplot': ['markers/*.png'],
    },
    install_requires=['requests'],
)
