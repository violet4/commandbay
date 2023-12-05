#!/bin/sh
set -ex

# build base+test images
docker build -f docker/Dockerfile.base -t commandbay-base .
docker build -f docker/Dockerfile.test -t commandbay-test .

# run the tests and extract the coverage report
docker run --name commandbay-test-container commandbay-test
docker cp commandbay-test-container:/app/htmlcov ./htmlcov

# cleanup
# docker rm commandbay-test-container
