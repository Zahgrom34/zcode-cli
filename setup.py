from setuptools import setup, find_packages

# with open('README.md', 'r') as fh:
    # long_description = fh.read()

with open('requirements.txt', 'r') as f:
    required_packages = f.read().splitlines()


setup(
    name='zhcode-cli',
    version='1.0.0',
    description='Class Based CLI tools for your application',
    author='Zahcoder34',
    author_email='zakhriw@gmail.com',
    url='https://github.com/Zahgrom34/zcode-cli',
    packages=find_packages(),
    install_requires=required_packages,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
