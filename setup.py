from setuptools import setup, find_packages

setup(
    name='igrowth',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'plotly',
        'loguru',
        'click',
        'requests',
        
    ],
    entry_points='''
        [console_scripts]
        igrowth=src.cli:cli
    ''',
)

