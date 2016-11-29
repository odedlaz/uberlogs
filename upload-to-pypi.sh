#!/bin/sh
rm -rf build/ dist/ uberlogs.egg-info/
python setup.py sdist bdist_wheel
twine upload -r test -s dist/uberlogs*
