#!/bin/bash

PROGRAM_NAME=${0##*/} # https://stackoverflow.com/a/3588939
PROGRAM_VERSION=0.1

usage() {
  echo "Usage:"
  echo "  $PROGRAM_NAME [options]";
  echo
  echo "Options:"
  echo "  -h, --help"
  echo "  -v, --version"
  echo "  --mode default|fatjar|nailgun"
  echo "  --fatjar <file/to/fat.jar>"
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
mode:,\
fatjar:,\
port:,\
help,version \
-- "$@")
# --quiet \  ## suppress getopt errors

# if [ $? -ne 0 ]; then
#   echo "Error parsing arguments. Try $PROGRAM_NAME --help" >&2
#   exit 2
# fi
[ $? -eq 0 ] || { echo; usage; exit 2; }

MODE_DEFAULT=1
MODE_FATJAR=2
MODE_NAILGUN=3
MODE=$MODE_DEFAULT

SILICON_MAIN="viper.silicon.SiliconRunner"
JAVA_CMD="java"
JAVA_OPTS="-Xss16m -Dfile.encoding=UTF-8"
NAILGUN_CLIENT="ng-nailgun"

FATJAR=
PORT=2113

eval set -- "$TEMP"
while true; do
  case $1 in
    -h|--help) usage; exit 0 ;;
    -v|--version) version; exit 0 ;;
    --mode)
      case $2 in
        default) MODE=$MODE_DEFAULT ;;
        fatjar) MODE=$MODE_FATJAR ;;
        nailgun) MODE=$MODE_NAILGUN ;;
        *) printf "Unknown argument %s to option %s\n" "$2" "$1"; exit 2 ;;
      esac
      shift ;;
    --fatjar)
      [ $MODE -eq $MODE_FATJAR ] || die 2 "--fatjar must be preceded by --mode fatjar"
      FATJAR=$2
      shift ;;
    --port)
      [ $MODE -eq $MODE_NAILGUN ] || die 2 "--port must be preceded by --mode nailgun"
      PORT=$2
      shift ;;
    --) shift; break ;; # no more arguments to parse                                
    *) printf "Unhandled option %s\n" "$1"; exit 2 ;;
  esac
  shift
done

# echo "Trailing arguments \$@: '$@'"
# echo "Mode: '$MODE'"

case $MODE in
  $MODE_DEFAULT)
    die 2 "Not yet implemented: --mode default" ;;
  $MODE_FATJAR)
    echo "Fat jar: '$FATJAR'"
    [ ! -z $FATJAR ] || die 2 "--mode fatjar requires supplying --fatjar"
    [ -r $FATJAR ] || die 1 "Supplied fat jar $FATJAR is not readable"
    CMD="$JAVA_CMD $JAVA_OPTS -cp $FATJAR $SILICON_MAIN $@"
    # echo "Command: '$CMD'"
    $CMD
    ;;
  $MODE_NAILGUN)
    CMD="$NAILGUN_CLIENT --nailgun-port $PORT $SILICON_MAIN $@"
    # echo "Command: '$CMD'"
    $CMD
    ;;
esac
