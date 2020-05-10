"""
Usage instructions:
- If you are installing: `python setup.py install`
- If you are developing: `python setup.py sdist --format=zip bdist_wheel --universal bdist_wininst && twine check dist/*`
"""
import DAWController

from setuptools import setup
setup(
    name='DAWController',
    version=DAWController.version,
    author='Malik Enes Safak',
    author_email='e.maliksafak@gmail.com',
    packages=['DAWController'],
    url='https://github.com/NullMember/DAWController',
    license='MIT',
    install_requires=[
        "python-rtmidi"
    ],
    description='Use Python as DAW Controller',
    keywords = 'universal daw controller mackie emulator'
)