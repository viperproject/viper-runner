#!/bin/bash

SCRIPT_DIR=${0%/*} # https://stackoverflow.com/a/3588939
PORT=$1

$SCRIPT_DIR/warmup-viper.sh \
    --repetitions 2 \
    "$SCRIPT_DIR/silicon.sh --mode nailgun --port $PORT" \
    $SCRIPT_DIR/warmup.vpr
