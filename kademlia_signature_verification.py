from twisted.internet import reactor, defer
from twisted.python import log
from kademlia.network import Server
from kademlia import utils
from kademlia import Node
from Crypto import Random
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


class FreemeServer(Server):
    def __init__(self, ksize=20, alpha=3, id=None, storage=None):
        return super(FreemeServer, self).__init__(ksize, alpha, id, storage)

    def verify_origin(self, hash, signed_message, sid):
        self.log.debug("verifying signed message...")
        
        dkey = utils.digest(hash)
        node = Node(dkey)
        
        def verify(nodes):
            

        
        nearest = self.protocol.router.findNeighbors(node)
        if len(nearest) == 0:
            self.log.warning("There are no known neighbors to verify signed message")
            return defer.succeed(False)
        spider = NodeSpiderCrawl(self.protocol, node, nearest, self.ksize, self.alpha)
        return spider.find().addCallback(verify)

    def set(self, key, value, signed_message):
        hash = SHA256.new(value)
        sid = Random.random.randint(0, 65535)
        if self.verify_origin(hash, signed_message, sid):
            return super(FreemeServer, self).set(key, value)


def process_result(result, key):
    if result:
        print "{0} : {1}".format(key, result)
    else:
        print "Notfing found for Key: {0}".format(key)
    reactor.stop()


def get_val(found, server, key):
    bootstrapDone(found)
    server.get(key).addCallback(process_result, key)


def set_val(found, server, key, val):
    bootstrapDone(found)
    if server.set(key, val):
        print "Set successfully!"
        #reactor.stop()


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
