#!/bin/bash
PERSONALITY=anybot
docker \
    run \
    --entrypoint /bin/bash \
    -v $PWD/:/app \
    -v $PWD/devel/$PERSONALITY/configs:/app/configs \
    -v $PWD/devel/$PERSONALITY/logs:/logs \
    -v $PWD/devel/$PERSONALITY/personality:/app/personality \
    -it \
    softbeing:devel
