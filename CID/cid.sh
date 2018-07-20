#!/bin/bash
BRANCH_NAME=`git rev-parse --abbrev-ref HEAD`
if test $BRANCH_NAME = 'master'
then
    #Test the doc build
    make docs
    make clean
fi

if test $BRANCH_NAME = 'production'
then
    # Install twine
    pip install twine
    # Create a source distribution
    python setup.py sdist
    # Upload to pypi
    twine upload dist/*
fi
