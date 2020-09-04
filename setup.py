from setuptools import setup

setup(
    name='cloudsnap',
    version='0.1',
    author='nauticalTux',
    description='cloudsnap is a tool for interacting with AWS EC2 snapshots',
    license='GPLv3+',
    packages=['snapper'],
    url='https://github.com/nauticalTux/cloudsnap',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        snapper=snapper.snapper:cli
    ''',
)