# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import frappe
with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in redtheme_v13b/__init__.py
from dynamic import __version__ as version

setup(
	name='dynamic',
	version=version,
	description='Dynamic',
	author='Dynamic',
	author_email='dynamic@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

