from setuptools import setup

setup(name='qube',
      version='0.1',
      description='A Library to access Qube Smartbulbs API',
      url='https://github.com/Azelphur/qube-api',
      author='Azelphur',
      author_email='support@azelphur.com',
      license='GPL',
      packages=['qube'],
      zip_safe=False,
      install_requires=[
          'requests'
      ],
)
