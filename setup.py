from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rcpchgrowth',
    version='2.1.4',  # Required
    description='SDS and Centile calculations for UK Growth Data',
    long_description="https://github.com/rcpch/digital-growth-charts/blob/master/README.md",
    # long_description_content_type='text/markdown',
    url='https://github.com/rcpch/digital-growth-charts/blob/master/README.md',
    author='@eatyourpeas, @marcusbaw @statist7 RCPCH',

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='eatyourpeasapps@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Pick your license as you wish
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    keywords='growth charts anthropometry SDS Centile',  # Optional

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={'': 'rcpchgrowth'},  # Optional
    packages=find_packages(),  # Required
    python_requires='>=3.5, <4',
    install_requires=[],  # Optional
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    include_package_data=True,
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/rcpch/digital-growth-charts/issues',
        'API management': 'https://dev.rcpch.ac.uk',
        'Source': 'https://github.com/rcpch/digital-growth-charts',
    },
)
