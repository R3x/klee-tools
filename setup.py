from setuptools import setup

setup(name='klee-tools',
      version='0.1',
      description='KLEE utilities written in Python',
      url='http://github.com/R3x/klee-tools',
      author='Siddharth Muralee',
      author_email='siddharth.muralee@gmail.com',
      license='MIT',
      packages=['klee_tools'],
      scripts=['bin/ktestutil'],
      install_requires=[
          'click',
      ],
      zip_safe=False)