#!/bin/bash

PROGRAM_NAME=${0##*/} # https://stackoverflow.com/a/3588939
PROGRAM_VERSION=0.1

usage() {
  echo "Usage:"
  echo "  $PROGRAM_NAME [options] <command> <file.vpr> [files.vpr]";
  echo
  echo "Executes '<command> <file_i.vpr>' for each provided file.'"
  echo 
  echo "Options:"
  echo "  -h, --help"
  echo "  -v, --version"
  echo "  --port <port>"
  echo "  --repetitions <#repetitions>"
}

version() {
  printf "%s, version %s\n" "$PROGRAM_NAME" "$PROGRAM_VERSION"; 
}

die() {
  EXIT_CODE=$1
  shift
  echo $@ >&2
  exit $EXIT_CODE
}

# Declare valid arguments and parse provided ones
TEMP=$(getopt \
-n $PROGRAM_NAME \
-o hv \
--long \
port:,\
repetitions:,\
help,version \
-- "$@")
# --quiet \  ## suppress getopt errors

[ $? -eq 0 ] || { echo; usage; exit 2; }

JAVA_CMD="java"
JAVA_OPTS="-Xss16m -Dfile.encoding=UTF-8"
NAILGUN_CLIENT="ng-nailgun"
PORT=2113
REPETITIONS=2
COMMAND=

eval set -- "$TEMP"
while true; do
  case $1 in
    -h|--help) usage; exit 0 ;;
    -v|--version) version; exit 0 ;;
    --port) PORT=$2; shift ;;
    --repetitions) REPETITIONS=$2; shift ;;
    --) shift; break ;; # no more arguments to parse                                
    *) printf "Unhandled option %s\n" "$1"; exit 2 ;;
  esac
  shift
done

# echo "Trailing arguments \$@: '$@'"
# echo "Port: '$PORT'"

COMMAND=$1
shift
# echo "Command: '$COMMAND'"

declare -a FILES
declare -i LEN

while [ ! -z $1 ]; do
#   echo $1
  LEN=${#FILES[@]}
#   echo $LEN
  FILES[$LEN]=$1
  shift
done
# echo "Files: '${FILES[*]}'"

[ ! -z $LEN ] || die 1 "At least one file must be provided"

for FILE in ${FILES[@]}; do
  CMD="$COMMAND $FILE"
  # echo "Command: '$CMD'"
  for ((R=0; $R < $REPETITIONS; R++)); do
    $CMD
  done
done
