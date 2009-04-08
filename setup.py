from distutils.core import setup
from mudbug import __version__ as VERSION

setup(
    name='mudbug',
    author='Antti Kaihola',
    author_email='akaihol+mudbug@ambitone.com',
    version=VERSION,
    url='http://github.com/akaihola/mudbug',
    py_modules=['mudbug'],
    description='MS Access JET engine MDB file helpers',
    description_full=__doc__,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python'
    ]
)
