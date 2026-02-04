"""Setup configuration for poker-hand-analyzer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name='poker-hand-analyzer',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Real-time poker hand analyzer using computer vision',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/poker-hand-analyzer',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'poker-analyzer=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'poker_analyzer': ['../config/*.yaml'],
    },
)