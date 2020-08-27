from setuptools import setup, find_packages

setup(
    name='cod',
    version='0.1',
    packages=find_packages(),
    py_modules=['cod/cli'],
    install_requires=[
        'botocore>=1.13',
        'boto3>=1.10',
        'Click>=7.0',
        'easygui>=0.98',
    ],
    entry_points={
        'console_scripts': ['cod=cod.cli:main'],
    },
    author='Jeffrey Massung',
    author_email='massung@gmail.com',
    description='Cod Shell SSH connection manager',
    keywords='cod shell ssh',
    url='https://github.com/massung/cod-shell',
    project_urls={
        'Issues': 'https://github.com/massung/cod-shell/issues',
        'Source': 'https://github.com/massung/cod-shell',
    },
    license='BSD3',
)
