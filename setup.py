from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='ru_soundex',
    version='1.0.0',
    url='https://github.com/roddar92/russian_soundex',
    author='Daria Rodionova',
    author_email='drodionova86@gmail.com',
    license='MIT',
    packages=find_packages(),
    description = 'Soundex algorithm for russian, english and finnish languages',
    long_description=open(join(dirname(__file__), 'README.md')).read(), install_requires=['pymorphy2', 'editdistance'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3.5',
        'Topic :: Text Processing :: Linguistic'
    ]
)
