from distutils.core import setup

setup(name='hacspec',
      version='0.0.1.dev1',
      description='hacspec is a new specification language for crypto primitives that is succinct, that is easy to read and implement, and that lends itself to formal verification.',
      url='https://github.com/HACS-workshop/hacspec',
      author='Franziskus Kiefer et al.',
      author_email='franziskuskiefer@gmail.com',
      license='MIT',
      # package_dir = {'hacspec': '.'},
      # packages=['.'],
      py_modules = ['speclib'],
      install_requires = ['setuptools', 'typeguard'],
      entry_points={
          'console_scripts': [
              'hacspec-check=check:main',
          ],
      })
