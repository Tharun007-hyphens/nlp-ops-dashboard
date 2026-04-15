from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Venkata Tharun Seemakurthi',
	author_email='tharuns.dev@gmail.com',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)