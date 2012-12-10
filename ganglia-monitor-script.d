#!/bin/sh
#
# chkconfig: 2345 20 81
# description: gmond startup script
#
LANCER=ganglia-script
BINPATH=/usr/bin/
SCRIPTPATH=/usr/share/ganglia-monitor-script/script/
PATH=$PATH:$BINPATH

. /etc/rc.d/init.d/functions

RETVAL=0

case "$1" in
   start)
      gprintf "Starting GANGLIA monitor scripts: "
      [ -f $BINPATH/$LANCER ] || exit 1

      daemon $LANCER $SCRIPTPATH
      RETVAL=$?
      echo
      [ $RETVAL -eq 0 ] && touch /var/lock/subsys/ganglia-monitor-script
	;;

  stop)
      gprintf "Shutting down GANGLIA monitor scripts: "
      killproc $LANCER 
      RETVAL=$?
      echo
      [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/ganglia-monitor-script
	;;

  restart|reload)
   	$0 stop
   	$0 start
   	RETVAL=$?
	;;
  status)
   	status $LANCER
   	RETVAL=$?
	;;
  *)
	gprintf "Usage: %s {start|stop|restart|status}\n" "$0"
	exit 1
esac

exit $RETVAL
