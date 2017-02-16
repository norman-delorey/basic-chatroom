__author__ = 'Norman Delorey'
__version__ = '1.0'
"""
    This contains two classes (User and Host) to send and receive text messages.
"""
import socket
import pickle

class User:
    def __init__(self, name, tempHost, tempPort=12345):
        """
        Creates an object to send/receive messages to/from a host.
        :param name: the name for the user to identify as
        :param tempHost: the hostname to connect to
        :param tempPort: the port number to connect to
        :return: none
        """
        self.decoded = [] #the de-serialized messages
        self.userName = name
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
        self.host = tempHost #needs to be set to the host machine
        self.port = int(tempPort) #needs to be the same as that of the host, otherwise connection denied

    def connect(self):
        """
        Initially connects to the hostname
        :return: none
        """
        self.s.connect((self.host, self.port))
        self.s.send(b'')
        self.s.close()

    def sendMessage(self, message):
        """
            Sends a serialized message to the host
        :param message: the text for the user to send
        :return:
        """
        self.s = socket.create_connection((self.host, self.port)) #re-connects to the host
        info = [socket.gethostname(), self.port, self.userName, message]
        data = pickle.dumps(info) #serializes the message
        self.s.send(data) #sends the message
        self.s.close()

    def setPort(self, newPort):
        """
            Sets the port number
        :param newPort: the new port number
        :return: none
        """
        self.port = newPort

    def getPort(self):
        """
        :return: the port number (self.port)
        """
        return self.port

    def getName(self):
        """
        :return: the user's name (self.userName)
        """
        return self.userName

    def getDecoded(self):
        """
        :return: returns the de-serialized messages (self.decoded)
        """
        return self.decoded

    def accept(self):
        """
            Receives messages from the host.
        :return: none
        """
        acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #makes a new socket
        self.decoded.append("Your ip is: " + socket.gethostbyname(socket.gethostname()))
        acceptor.bind((socket.gethostbyname(socket.gethostname()), self.port)) #sets to the local hostname and the given port
        acceptor.listen(5) #starts listening for a connecting

        while True: #will loop until program closes
            try:
                c, addr = acceptor.accept()
                received = c.recv(4096) #takes in messages
                message = pickle.loads(received) #de-serializes messages
                decodedMessage = message[2] + ": " + message[3] #formats the message with the username and message

                #added to fix an issue where the same message was received > 1 times
                #maybe change later to allow for spam/repeat messages
                if len(self.decoded) > 0 and self.decoded[-1] != decodedMessage:
                    self.decoded.append(decodedMessage)
                elif len(self.decoded) == 0:
                    self.decoded.append(decodedMessage)
            except:
                print(":( something went wrong...")

            c.close()


class Host(User):
    def __init__(self, name, tempPort=12345):
        """
        Creates a new host to send/receive messages to/from users
        :param name: the name to identify the user
        :param tempPort: the port that the server is hosted on
        :return: none
        """
        self.host = socket.gethostbyname(socket.gethostname()) #gets host machine
        self.port = tempPort
        ipString = "Your hostname: " + socket.gethostname()
        portString = "with port number: " + str(self.port)
        self.decoded = [ipString, portString]
        self.users = [] #the de-serialized messges
        self.userName = name
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object

    def sendMessage(self, message):
        """
            Sends messages to everyone on the server
        :param message: the message to send
        :return:
        """
        for i in self.users: #loops through every connected user
            self.s = socket.create_connection((i[0], self.port)) #connects to the user
            info = [socket.gethostname(), self.port, self.userName, message]
            if len(self.decoded) > 0 and self.decoded[-1] != info[2] + ": " + info[3]:
                self.decoded.append(info[2] + ": " + info[3]) #adds the message to the host's list
            elif len(self.decoded) == 0:
                self.decoded.append(info[2] + ": " + info[3]) #adds the message to the host's list
            data = pickle.dumps(info) #serializes the message
            self.s.send(data) #sends the message
            self.s.close()

    def accept(self):
        """
            Accepts messages from clients
        :return: none
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a new socket
        self.s.bind(('', self.port))        # Bind to the port
        self.s.listen(5)                 # Now wait for client connection.

        while True:
           c, addr = self.s.accept()     # Establish connection with client.
           recievedData = c.recv(4096) #receives data

           if addr not in self.users:
                self.users.append(addr) #adds any new users to the user list
                self.decoded.append("Received connection from: " + str(addr[0])) #informs the host that there is a new user
           try:
               try:
                   message = pickle.loads(recievedData) #de-serializes the message
                   self.decoded.append(message[2] + ": " + message[3])
                   recieved = True #has received a message
               except:
                   pass

               if recieved: #if a message has been received
                   for i in self.users: #relays the message to every connected user
                        sender = socket.create_connection((i[0], self.port)) #connects to the user
                        sender.send(pickle.dumps(message))
                        sender.close()

               c.close()                # Close the connection
           except:
               pass