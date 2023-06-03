from setuptools import find_packages, setup

setup(
    name='mbrs-api',
    version='1.0.0',
    packages=find_packages('app', exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'flask',
        'pyjwt',
        'mysql-connector-python',
        'apispec',
        'apispec-webframeworks',
        'marshmallow',
        'webargs',
        'flask-cors',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)