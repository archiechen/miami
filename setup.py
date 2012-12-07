from setuptools import setup

setup(
    name='miami',
    version='0.1.6',
    packages=['miami'],
    py_modules=['run_server'],
    entry_points={
        'console_scripts': [
            'miamid=run_server:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'simplejson==2.6.1',
        'flup==1.0.3.dev_20110405',
        'flask==0.9',
        'flup==1.0.3.dev_20110405',
        'sqlalchemy==0.7.9',
        'flask_restless==0.7.0',
        'flask_login==0.1.3',
        'flask_sqlalchemy==0.16',
        'flask-gravatar==0.2.3',
        'apscheduler==2.0.3',
        'MySQL-Python==1.2.4c1'
    ]
)