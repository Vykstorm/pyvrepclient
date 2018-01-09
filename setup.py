from setuptools import setup


setup(
    name = 'pyvrepclient',
    version = '1.0.0',
    description = 'Remote client of V-rep simulation program implemented en Python',
    url = 'https://github.com/Vykstorm/pyvrepclient',
    author = 'Vykstorm',
    author_email = 'victorruizgomezdev@gmail.com',
    license = 'MIT',
    zip_safe = False,
    packages = [''],
    install_requires = ['numpy', 'Pillow', 'vectormath']
)