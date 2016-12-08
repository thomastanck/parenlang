from setuptools import setup

setup(name='parenlang',
      version='0.0.1',
      description='A lang made out of parens.',
      url='http://github.com/thomastanck/parenlang',
      author='Thomas Tan',
      author_email='thomastanck@gmail.com',
      license='MIT',
      packages=['parenlang'],
      entry_points={
            'console_scripts': ['paren=parenlang.__main__:main']
      },
      zip_safe=False)
