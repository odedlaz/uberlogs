#!/bin/sh
SERVER=${1:-"test"}

echo "Uploading uberlogs to ${SERVER}"

rm -rf build/ dist/ uberlogs.egg-info/ 1> /dev/null
python setup.py sdist bdist_wheel 1> /dev/null
twine upload -r $SERVER -s dist/uberlogs*
