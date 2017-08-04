#!/bin/bash

SCRIPT_DIR=${0%/*} # https://stackoverflow.com/a/3588939
PORT=$1

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