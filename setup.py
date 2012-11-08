from setuptools import setup

setup(
    name='miami',
    version='0.1',
    packages=['miami'],
    py_modules=['run_server'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'simplejson==2.6.1',
        'flask==0.9',
        'flask_principal==0.3.3',
        'flup==1.0.3.dev_20110405',
        'sqlalchemy==0.7.9',
        'flask_restless==0.7.0',
        'flask_sqlalchemy==0.16'
    ]
)