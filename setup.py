from setuptools import setup, find_packages

setup(
    name='ipybrowser',
    version='0.0.1',
    author='Ahmad Abdal Qader',
    author_email='anonyIDmous@protonmail.com',
    description='A file browser for interactive python environments',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    url='https://github.com/X4ndri/ipybrowser',  
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pandas',
        'requests',
        'ipython',
        'jupyter',
        'sidecar',
        'ipywidgets',
        'ipydatagrid',
        'jupyterlab-widgets'

    ]
)
