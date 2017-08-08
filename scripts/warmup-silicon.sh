#!/bin/bash

SCRIPT_DIR=${0%/*} # https://stackoverflow.com/a/3588939
PORT=2113

if [ ! -z $1]; then
    PORT=$1
fi

$SCRIPT_DIR/warmup-viper.sh \
    --repetitions 1 \
    "$SCRIPT_DIR/silicon.sh --mode nailgun --port $PORT" \
    $SCRIPT_DIR/warmup1.vpr

$SCRIPT_DIR/warmup-viper.sh \
    --repetitions 1 \
    "$SCRIPT_DIR/silicon.sh --mode nailgun --port $PORT" \
    $SCRIPT_DIR/warmup2.vpr

$SCRIPT_DIR/warmup-viper.sh \
    --repetitions 1 \
    "$SCRIPT_DIR/silicon.sh --mode nailgun --port $PORT" \
    $SCRIPT_DIR/warmup3.vpr