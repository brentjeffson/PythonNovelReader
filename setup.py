from setuptools import setup, find_packages

setup(
    name='NovelReader-Openiom',
    version='0.1',
    description='Novel Reader',
    author='Brent Jeffson F. Florendo',
    author_email='brentjeffson@gmail.com',
    packages=find_packages(
        exclude=()
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='~=3.7',
    install_requires=[
        'aiohttp==3.6.2',
        'beautifulsoup4==4.9.1',
        'lxml==4.5.2'
    ]
)