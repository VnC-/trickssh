from twisted.internet.protocol import Protocol
from twisted.conch.ssh import factory
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.interfaces import IConchUser
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.session import SSHSession, SSHSessionProcessProtocol, wrapProtocol
from twisted.cred import credentials, portal
from twisted.internet import defer

with open('id_rsa') as privateBlobFile:
    privateBlob = privateBlobFile.read()
    privateKey = Key.fromString(data=privateBlob)

with open('id_rsa.pub') as publicBlobFile:
    publicBlob = publicBlobFile.read()
    publicKey = Key.fromString(data=publicBlob)

class EchoProtocol(Protocol):
    def connectionMade(self):
        self.transport.write('Faggot %s connected: password %s \r\n' % (EchoProtocol.c.username, EchoProtocol.c.password))
      # self.transport.loseConnection()  # Immediatly disconnect or leave client hanging
    def dataReceived(self, bytes):
        pass
    def connectionLost(self, reason):
        print 'Connection lost', reason

class SimpleSession(SSHSession):
    def request_pty_req(self, data):
        return True

    def request_shell(self, data):
        protocol = EchoProtocol()
        transport = SSHSessionProcessProtocol(self)
        protocol.makeConnection(transport)
        transport.makeConnection(wrapProtocol(protocol))
        return True

class AccessGranted:
    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    def requestAvatarId(self, credentials):
        EchoProtocol.c = credentials
        print '%s %s' % (credentials.username, credentials.password)
        return defer.succeed(1)
      
class UnixSSHdFactory(factory.SSHFactory):
    publicKeys = {'ssh-rsa': publicKey}
    privateKeys = {'ssh-rsa': privateKey}

    def buildProtocol(self, addr):
        print addr
        return factory.SSHFactory.buildProtocol(self, addr)

class SimpleRealm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        user = ConchUser()
        user.channelLookup['session'] = SimpleSession
        return IConchUser, user, lambda: None

portal = portal.Portal(SimpleRealm())
portal.registerChecker(AccessGranted())
UnixSSHdFactory.portal = portal

reactor.listenTCP(2042, UnixSSHdFactory())
reactor.run()

