#!/bin/bash

PROGRAM_NAME=${0##*/} # https://stackoverflow.com/a/3588939
PROGRAM_VERSION=0.1

usage() {
  echo "Usage:"
  echo "  $PROGRAM_NAME [options] <fat.jar>";
  echo
  echo "Options:"
  echo "  -h, --help"
  echo "  -v, --version"
  echo "  --port <port>"
  echo "  --stop"
  echo "  --restart"
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
stop,restart,\
help,version \
-- "$@")
# --quiet \  ## suppress getopt errors

[ $? -eq 0 ] || { echo; usage; exit 2; }

JAVA_CMD="java"
JAVA_OPTS="-Xss16m -Dfile.encoding=UTF-8"
NAILGUN_JAR="/usr/share/java/nailgun-server-0.9.1.jar"
NAILGUN_MAIN="com.martiansoftware.nailgun.NGServer"
NAILGUN_CLIENT="ng-nailgun"
PORT=2113
STOP=false
RESTART=false

eval set -- "$TEMP"
while true; do
  case $1 in
    -h|--help) usage; exit 0 ;;
    -v|--version) version; exit 0 ;;
    --port)
      PORT=$2
      shift ;;
    --restart) RESTART=true ;;
    --stop) STOP=true ;;
    --) shift; break ;; # no more arguments to parse                                
    *) printf "Unhandled option %s\n" "$1"; exit 2 ;;
  esac
  shift
done

# echo "Trailing arguments \$@: '$@'"
# echo "Port: '$PORT'"

if [ "$STOP" = true ]; then
  CMD="$NAILGUN_CLIENT --nailgun-port $PORT ng-stop"
  # echo "Command: '$CMD'"
  $CMD
  exit
fi

FATJAR=$1
shift
# echo "Fat jar: '$FATJAR'"
[ ! -z $FATJAR ] || die 2 "Mandatory argument <fat.jar> not supplied"

if [ "$RESTART" = true ]; then
  CMD="$NAILGUN_CLIENT --nailgun-port $PORT ng-stop"
  # echo "Command: '$CMD'"
  $CMD
fi

CMD="$JAVA_CMD $JAVA_OPTS -cp $NAILGUN_JAR:$FATJAR $NAILGUN_MAIN $PORT"
# echo "Command: '$CMD'"
coproc $CMD &
