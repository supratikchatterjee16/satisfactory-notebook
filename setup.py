# from ast import keyword
# import os
# import glob
from setuptools import setup, find_packages  # , Extension


with open('README.md') as f:
    extd_desc = f.read()

with open('LICENSE.md') as f:
    license = f.read()

# creeper = Extension(
#     'creeper',
#     sources=sorted(glob.glob(os.path.join('creeper', '*.cpp'))),
#     extra_compile_args=['-std=c99', '-fno-strict-aliasing', '-fcommon',
#                         '-fPIC', '-Wall', '-Wextra', '-Wno-unused-parameter',
#                         '-Wno-missing-field-initializers', '-g']
# )

requirements_noversion = [
    'pandas',
    'scikit-image',
    'matplotlib',
    'scikit-learn',
    'appdirs'
]

setup(
    # Non-Technical requirements
    name="satisfactory_planner",
    version="0.0.1",
    description="Analyze data, find all recipes and more in the game of Satisfactory",
    # https://stackoverflow.com/questions/14399534/reference-requirements-txt-for-the-install-requires-kwarg-in-setuptools-setup-py
    long_description=extd_desc,
    long_description_content_type='text/markdown',
    keywords=['satisfactory', 'game', 'analysis', 'jupyter', 'supply-chain'],
    license=license,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Free for non-commercial use"
    ],
    # Technical Requirements
    # ext_modules=[],
    packages=find_packages(),
    install_requires=requirements_noversion,
    package_dir={'satisfactory_planner': './satisfactory_planner'},
    package_data={'satisfactory_planner': ['res/images/*']},
    # entry_points={'console_scripts': ['track = et:run'], },
    zip_safe=True
)
