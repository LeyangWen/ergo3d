from setuptools import setup, find_packages

setup(
    name='ergo3d',  # Name of your package
    version='0.1.0',  # Version number
    description='A Python package for 3D ergonomic calculations.',  # Short description of your package
    url='https://github.com/LeyangWen/ergo3d',  # URL for your package's homepage
    author='Leyang Wen',  # Your name
    author_email='wenleyan@umich.edu',  # Your email
    license='MIT',  # License type for your package
    packages=find_packages(),  # Automatically find all packages and subpackages
    install_requires=[  # List of dependencies
        'numpy',
        'matplotlib'
    ],
    classifiers=[  # Classifiers help users find your project by categorizing it
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',  # Minimum version of Python your package requires
)