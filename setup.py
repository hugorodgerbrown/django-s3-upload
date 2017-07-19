import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-s3direct-redux',
    version='0.5',
    description=('Django / Redux app for uploading files direct to S3 from the browser.'),
    long_description=readme,
    license="MIT",
    author="YunoJuno",
    author_email='code@yunojuno.com',
    url='https://github.com/yunojuno/django-s3-upload',
    packages=['s3upload'],
    include_package_data=True,
    install_requires=['django>=1.10', 'boto'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
)
