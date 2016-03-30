from twisted.internet import reactor, defer, stdio
from twisted.python import log
from kademlia.network import Server
from kademlia.node import Node
from kademlia.utils import digest
from kademlia.crawling import ValueSpiderCrawl
from kademlia.crawling import NodeSpiderCrawl
from kademlia.protocol import KademliaProtocol
from twisted.protocols import basic
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256, SHA
from Crypto import Random
from collections import Counter
import ipgetter
import random
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
args = parser.parse_args()


class ProcessQueries():

    def process_set(self, result):
      if result:
        print "Set successfully!"
      else:
        print "Set failed!"

    def process_get(self, result, key):
        if result:
            print "{0} : {1}".format(key, result)
            return result
        else:
            print "Notfing found for Key: {0}".format(key)
            return None


class FreemeValueSpiderCrawl(ValueSpiderCrawl):
    def __init__(self, protocol, node, peers, ksize, alpha):
        super(FreemeValueSpiderCrawl, self).__init__(protocol, node, peers, ksize, alpha)

    def _handleFoundValues(self, values):
        values = [tuple(el) for el in values]
        valueCounts = Counter(values)
        if len(valueCounts) != 1:
            args = (self.node.long_id, str(values))
            self.log.warning("Got multiple values for key %i: %s" % args)
        value = valueCounts.most_common(1)[0][0]

        peerToSaveTo = self.nearestWithoutValue.popleft()
        if peerToSaveTo is not None:
            d = self.protocol.callStore(peerToSaveTo, self.node.id, value, None)
            return d.addCallback(lambda _: value)
        return value


class FreemeProtocol(KademliaProtocol, ProcessQueries):
    def __init__(self, sourceNode, storage, ksize):
        KademliaProtocol.__init__(self, sourceNode, storage, ksize)

    def verify_origin(self, value, signed_message, pub_key):
        self.log.debug("verifying signed message...")
        hash = SHA256.new(value)
        public_key = RSA.importKey(pub_key)
        verifier = PKCS1_v1_5.new(public_key)
        return verifier.verify(hash, signed_message)

    def rpc_store(self, sender, nodeid, key, value, signed_message):
        def store(result_key):
            if result_key:
                if self.verify_origin(value, signed_message, result_key[0]):
                    self.log.debug("verification is succeeded for {0}".format(nodeid))
                    return KademliaProtocol.rpc_store(self, sender, nodeid, key, (result_key[0], value))
                else:
                    self.log.warning("verification is failed for {0}".format(nodeid))
                    return None
            else:
                self.log.warning("nothing found for {0}".format(nodeid))
                return None

        found_key = KademliaProtocol.rpc_find_value(self, sender, nodeid, key)
        if signed_message is None:
            if not found_key or not type(found_key) is dict:
                self.log.debug("setting login for {0}".format(nodeid))
                return KademliaProtocol.rpc_store(self, sender, nodeid, key, value)
            else:
                self.log.warning("key is setted already")
                return None
        else:
            return store(found_key["value"])

    def callStore(self, nodeToAsk, key, value, signed_message):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.store(address, self.sourceNode.id, key, value, signed_message)
        return d.addCallback(self.handleCallResponse, nodeToAsk)


class FreemeNode(Node):
    def __init__(self, id, ip=None, port=None):
        Node.__init__(self, id, ip, port)

    def distanceTo(self, node):
        return long(digest(self.long_id).encode('hex'), 16) ^ long(digest(node.long_id).encode('hex'), 16)


class FreemeServer(Server, ProcessQueries):
    def __init__(self, ksize=20, alpha=3, id=None, storage=None):
        super(FreemeServer, self).__init__(ksize, alpha, id, storage)
        self.protocol = FreemeProtocol(self.node, self.storage, ksize)
        self.node = FreemeNode(id or digest(random.getrandbits(255)))

    def get(self, key):
        """
        Get a key if the network has it.

        Returns:
            :class:`None` if not found, the value otherwise.
        """
        node = Node(digest(key))
        nearest = self.protocol.router.findNeighbors(node)
        if len(nearest) == 0:
            self.log.warning("There are no known neighbors to get key %s" % key)
            return defer.succeed(None)
        spider = FreemeValueSpiderCrawl(self.protocol, node, nearest, self.ksize, self.alpha)
        return spider.find()

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


class FreemeCommandLine(basic.LineReceiver, ProcessQueries):
    def __init__(self, server):
        self.server = server
        self.delimiter = '\n'

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
                self.sendLine('Error: ' + str(e))

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
        private_key = RSA.generate(2048, random_generator)
        public_key = private_key.publickey()
        with open("{0}_rsa".format(name), "w") as f_private:
            f_private.write(private_key.exportKey())
        with open("{0}_rsa.pub".format(name), "w") as f_public:
            f_public.write(public_key.exportKey())
        self.server.set(name, (public_key.exportKey(), None)).addCallback(self.process_set)

    def do_login(self, name):
        """login <name>: Login as user <name>"""
        my_ip = ipgetter.myip()

        def login(result):
            public_key = RSA.importKey(result[0])
            with open("{0}_rsa".format(name), "r") as f_private:
                private_key = RSA.importKey(f_private.read())
            signature = PKCS1_v1_5.new(private_key)
            hash = SHA256.new(my_ip)
            signed_message = signature.sign(hash)

            if public_key is None:
                print "Login failed! Such profile does not existing."
            else:
                self.server.set(name, my_ip, signed_message).addCallback(self.process_set)

        self.server.get(name).addCallback(self.process_get, name).addCallback(login)

    def do_find(self, name):
        """find <name>: Find a public key and IP of another user"""
        self.server.get(name).addCallback(self.process_get, name)

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

        server = FreemeServer()
        server.listen(bootstrap_port)
        server.bootstrap([(bootstrap_ip, bootstrap_port)]).addCallback(bootstrapDone)

        stdio.StandardIO(FreemeCommandLine(server))
        reactor.run()

    except KeyboardInterrupt:
        print '\nThe process was interrupted by the user'
        raise SystemExit

if __name__ == '__main__':
    main()
