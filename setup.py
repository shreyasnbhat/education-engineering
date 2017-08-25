from setuptools import setup
##ToDO
setup(name='education-engineering',
      version='0.1',
      description='A tool to help students predict grades',
      url='http://github.com/shreyasnbhat/education-engineering',
      author='Shreyas and Gautam',
      author_email='none@none.none',
      packages=['app', 'tests'],
      install_requires=['Flask>=0.2',
        'SQLAlchemy>=0.6'],
      zip_safe=False)
