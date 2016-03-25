from twisted.internet import reactor
from twisted.python import log
from kademlia.network import Server
import argparse
import sys

parser = argparse.ArgumentParser()

class color:
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'


parser.add_argument(
  '-ip', dest='bootstrap_ip', default='127.0.0.1', help='Bootstrap node IP address')
parser.add_argument(
    '-p', dest='bootstrap_port', default=2277, help='Bootstrap node port address')
parser.add_argument(
    '-q', dest='query', help='Qery a ' + color.RED + 'value ' + color.END
    + 'by the ' + color.YELLOW + 'key' + color.END)
parser.add_argument(
    '-s', dest='set', nargs=2, help='Set a ' + color.RED + 'value ' + color.END
    + 'by the ' + color.YELLOW + 'key' + color.END)
args = parser.parse_args()

def process_get(result, key):
    if result:
        print "{0} : {1}".format(key, result)
    else:
        print "Notfing found for Key: {0}".format(key)
        reactor.stop()


def get_val(found, server, key):
    bootstrapDone(found)
    server.get(key).addCallback(process_get, key)


def process_set(result):
  if result:
    print "Set successfully!"
  else:
    print "Set failed!"
    reactor.stop()


def set_val(found, server, key, val):
    bootstrapDone(found)
    server.set(key, val).addCallback(process_set)


def bootstrapDone(found):
    if len(found) == 0:
        print "Could not connect to the bootstrap server."
        reactor.stop()
    else:
        print "Bootstrapped successfully!"


def main():
    log.startLogging(sys.stdout)
    try:
        bootstrap_ip = args.bootstrap_ip
        bootstrap_port = int(args.bootstrap_port)
        get_v = args.query
        set_v = args.set

        server = Server()
        server.listen(bootstrap_port)

        if set_v:
            server.bootstrap([(bootstrap_ip, bootstrap_port)]).addCallback(set_val, server, set_v[0], set_v[1])
        if get_v:
            server.bootstrap([(bootstrap_ip, bootstrap_port)]).addCallback(get_val, server, get_v)

        reactor.run()

    except KeyboardInterrupt:
        print '\nThe process was interrupted by the user'
        raise SystemExit

if __name__ == '__main__':
    main()
