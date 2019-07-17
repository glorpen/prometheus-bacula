import setuptools

setuptools.setup(
    name="prometheus-bacula",
    version="1.0.0",
    author="Arkadiusz Dzięgiel",
    author_email="arkadiusz.dziegiel@glorpen.pl",
    description="A small example package",
    url="https://github.com/glorpen/prometheus-bacula",
    packages=setuptools.find_packages('src/'),
    package_dir = {'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Monitoring"
    ],
    install_requires=[
        "prometheus_client>=0.7.1,<1.0.0",
        "PyMySQL>=0.9.3,<1.0.0"
    ],
    entry_points = {
        'console_scripts': ['prometheus-bacula=prometheus_bacula.cli:main'],
    }
)
