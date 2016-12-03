#!/bin/sh
# The deploy script bumps the version of gapi and pushes it to github
# when the tests are done, travis will bake a docker image and push it to
# a remote registroy because the commit is tagged on master
set -e
bumpversion $1
git push --tags origin master

