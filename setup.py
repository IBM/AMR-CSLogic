from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from pip._internal.req import parse_requirements
from subprocess import run

VERSION = '0.1.0'


def run_script(path):
    print("Running {} ...".format(path))
    run("bash {}".format(path).split(), check=True)


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        run_script("scripts/download_third_party.sh")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        run_script("scripts/download_third_party.sh")


install_reqs = parse_requirements('requirements.txt', session='install')
reqs = [str(ir.requirement) for ir in install_reqs]

setup(
    name='amr_verbnet_semantics',
    version=VERSION,
    description='Enhancing AMR with VerbNet semantics',
    author='Zhicheng (Jason) Liang and Dr. Rosario Uceda-Sosa',
    author_email='liangz4@rpi.edu and rosariou@us.ibm.com',
    url='https://github.com/CognitiveHorizons/AMR-CSLogic',
    packages=find_packages(include=[
        'amr_verbnet_semantics',
        'amr_verbnet_semantics.*',
        'KG.*']),
    install_requires=reqs,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    extras_require={
        'interactive': ['matplotlib>=2.2.0', 'jupyter'],
    },
    setup_requires=[
        'pytest-runner', 
        'flake8'],
    tests_require=[
        'pytest', 
        'pytest-flask'],
    package_data={'': ['*.yaml', '*.ttl.zip']}
)
