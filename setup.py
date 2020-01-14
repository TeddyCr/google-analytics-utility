import setuptools

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.readlines()


setuptools.setup(
    name="googleAnalyticUtility",
    version="0.2.41",
    author="Teddy Crepineau",
    author_email="teddy.crepineau.pro@gmail.com",
    description="A package to easily interact with the Google Analytics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url ="https://github.com/TeddyCr/google-analytics-utility",
    packages=setuptools.find_packages(),
    classifiers=[
        "Python :: 3",
        "Operating Sytem :: OS Independent",
    ],
    install_requires=requirements,
    python_requires= '>=3.6',
)