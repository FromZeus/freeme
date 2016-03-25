from twisted.internet import reactor, defer
from twisted.python import log
from kademlia.network import Server
from kademlia import utils, Node, KademliaProtocol
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512
from Crypto import Random
import argparse
import sys
from signature_probe import signed_message

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


class FreemeProtocol(KademliaProtocol):
    def __init__(self, sourceNode, storage, ksize):
        super(KademliaProtocol, self).__init__(sourceNode, storage, ksize)

    def verify_origin(self, value, signed_message, pub_key):
        self.log.debug("verifying signed message...")
        hash = SHA256.new(value)
        public_key = RSA.importKey(pub_key)
        verifier = PKCS1_v1_5.new(public_key)
        return verifier.verify(hash, signed_message)

    def rpc_store(self, sender, nodeid, key, value, signed_message):
        if signed_message is None:
            if not super(FreemeProtocol, self).rpc_find_value(sender, nodeid, key):
                self.log.debug("setting login for {0}".format(nodeid))
                super(FreemeProtocol, self).rpc_store(sender, nodeid, key, value)
        elif self.verify_origin(value, signed_message, key):
            self.log.debug("verification is succeeded for {0}".format(nodeid))
            super(FreemeProtocol, self).rpc_store(sender, nodeid, key, value)
        else:
            self.log.warn("verification is failed for {0}".format(nodeid))

    def callStore(self, nodeToAsk, key, value, signed_message):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.store(address, self.sourceNode.id, key, value, signed_message)
        return d.addCallback(self.handleCallResponse, nodeToAsk)


class FreemeServer(Server):
    def __init__(self, ksize=20, alpha=3, id=None, storage=None):
        super(FreemeServer, self).__init__(ksize, alpha, id, storage)
        self.protocol = FreemeProtocol(self.node, self.storage, ksize)

    def set(self, key, value, signed_message=None):
        """
        Set the given key to the given value in the network.
        """
        self.log.debug("setting '%s' = '%s' on network" % (key, value))
        dkey = digest(key)

        def store(nodes):
            self.log.info("setting '%s' on %s" % (key, map(str, nodes)))
            ds = [self.protocol.callStore(node, dkey, value, signed_message) for node in nodes]
            return defer.DeferredList(ds).addCallback(self._anyRespondSuccess)

        node = Node(dkey)
        nearest = self.protocol.router.findNeighbors(node)
        if len(nearest) == 0:
            self.log.warning("There are no known neighbors to set key %s" % key)
            return defer.succeed(False)
        spider = NodeSpiderCrawl(self.protocol, node, nearest, self.ksize, self.alpha)
        return spider.find().addCallback(store)

    def create_user(self, name, pub_key):
        self.set(name, pub_key)

    def authorize(self, name, ip, signed_message):
        pub_key = self.get(name)
        self.set(pub_key, ip, signed_message)


class FreemeCommandLine(basic.LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        self.sendLine("FreeMe console. Type 'help' for help.")

    def lineReceived(self, line):
        if not line: return

        commandParts = line.split()
        command = commandParts[0].lower()
        args = commandParts[1:]

        try:
            method = getattr(self, 'do_' + command)
        except AttributeError, e:
            self.sendLine('Error: no such command.')
        else:
            try:
                method(*args)
            except Exception, e:
                self.sendLine('Error: ' + str(e)

    def do_help(self, command=None):
        """help [command]: List commands, or show help on the given command"""
        if command:
            self.sendLine(getattr(self, 'do_' + command).__doc__)
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            self.sendLine("Valid commands: " +" ".join(commands))

    def do_create_user(self, name):
        """create_user <name>: Creates new user"""
        random_generator = Random.new().read
        key = RSA.generate(2048, random_generator)
        public_key = key.publickey()
        

    def do_login(self, name):
        """login <name>: Login as user <name>"""


    def do_quit(self):
        """quit: Quit this session"""
        self.sendLine('Goodbye.')
        self.transport.loseConnection()
        
    def connectionLost(self, reason):
        # stop the reactor, only because this is meant to be run in Stdio.
        reactor.stop()


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
