#!/bin/bash

PORT=$1

/home/developer/source/viper-runner/warmup-viper.sh --repetitions 2 "./silicon.sh --mode nailgun --port $PORT" warmup.vpr
