from threading import *
from socket import *
import time
import sys

channels = {}

class RecvLoop(Thread):
    def __init__(self,socket,client):
        Thread.__init__(self)
        self.socket = socket
        self.client = client

    def run(self):
        print("Accepting data from server.")
        while True:
            d = self.socket.recv(1024)
            self.client.handle(d)

class Client(Thread):
    def __init__(self,server,port):
        Thread.__init__(self)
        self.server = server
        self.port = port
        self.start()
        self.channels = {}
        self.current_channel = None

    def run(self):
        print("Connecting to server...")
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.connect((self.server,self.port))
        print("Welcome to SquirrelChat!")
        print("Not logged in yet, either /authenticate or /register\n")
        print("Commands:\n")
        print("/join #channel")
        print("/register <username> <password>")
        print("/authenticate <username> <password>")
        print("/topic <new topic> <-- Sets topic for current channel")
        print("/block <username>")
        print("/ban <username> <channel>")
        print("/ban <username> <channel>")
        print("/unban <username> <channel>")
        print("/privmsg <username> << open up chat with <username>")
        self.loop()

    def display_chat(self,entity,chat):
        print("{}> {}".format(entity,chat))

    # Handle a message from the server
    def handle(self,d):
        pieces = d.split()
        if len(pieces) == 0:
            print("error: got empty packet")
            exit(1)
        # These are the only things that should come back from the server
        elif pieces[0] == "chatfrom":
            chat = d.split(' ', 3)
            if not chat[2] in self.channels:
                # Notify the user of the first chat on a channel
                self.channels[chat[2]] = [(chat[1],chat[3])]
                print("Attention: First chat on channel {}".format(chat[2]))
            else:
                # Log this in case they go back later
                self.channels[chat[2]].append((chat[1],chat[3]))
            if self.current_channel == chat[2]:
                self.display_chat(chat[1],chat[3])
        elif pieces[0] == "topic":
            topic = d.split(' ', 2)
            print("The topic for {} is {}".format(topic[1],topic[2]))
        elif pieces[0] == "error":
            print("Error! {}".format(d.split(' ', 1)[1]))
        else:
            print("The server has sent back a response I can't parse:")
            print(d)

    # Note: Doesn't check whether channel login was successful
    def change_to(self,channel):
        self.current_channel = channel
        print("Changed to channel {}".format(self.current_channel))
        # To all you students: perhaps think about showing the sent
        # since the last time that the user logged into this channel.
        
    # Note: No checking on the client end
    def handle_input(self,i):
        print("Here!")
        cmd = i.split()
        if (cmd[0] == "/join"):
            print("Joining {}..".format(cmd[1]))
            self.send("join {}".format(cmd[1]))
            time.sleep(.2)
            self.send("gettopic {}".format(cmd[1]))
            self.change_to(cmd[1])
        elif (cmd[0] == "/register"):
            print("Registering...")
            self.send("register {} {}".format(cmd[1],cmd[2]))
            self.current_user = cmd[1]
        elif (cmd[0] == "/authenticate"):
            self.send("authenticate {} {}".format(cmd[1],cmd[2]))
            self.current_user = cmd[1]
        elif (cmd[0] == "/gettopic"):
            self.send("gettopic {}".format(cmd[1]))
        elif (cmd[0] == "/settopic"):
            self.send("settopic {} {}".format(cmd[1],i.split(' ', 2)[2]))
        elif (cmd[0] == "/block"):
            self.send("block {}".format(cmd[1]))
        elif (cmd[0] == "/ban"):
            self.send("ban {} {}".format(cmd[1],cmd[2]))
        elif (cmd[0] == "/privmsg"):
            print("Now in private message with user {}".format(cmd[1]))
            self.change_to(cmd[1])
        elif (cmd[0] == "/unban"):
            self.send("unban {} {}".format(cmd[1],cmd[2]))
        else:
            self.send("chat {} {}".format(self.current_channel,i))

    def send(self,msg):
        self.connection.send(msg)

    def loop(self):
        x = RecvLoop(self.connection,self)
        x.start()
        while True:
            i = raw_input('>')
            self.handle_input(i)

if (len(sys.argv) == 3):
    client = Client(sys.argv[1],int(sys.argv[2]))
else:
    raise Exception("python textclient.py <server> <port> <-- If running on same machine, <server> is localhost")
