__author__ = 'Norman Delorey'
__version__ = '1.0'
"""
    This class creates the two windows for the user to interface with.
"""
from idlelib.ToolTip import *
import connect
import threading

class startWindow():
    def __init__(self):
        """
        This is the constructor for the initial window seen by the user.
        It contains the options for selecting how the user will interact with the chat room
        :return: none
        """
        self.master = Tk()
        self.options = StringVar()
        self.options.set("Choose an option:")
        self.options.trace('w', self.changeMode)
        self.userType = OptionMenu(self.master, self.options, "Host", "User")
        self.userTip = ToolTip(self.userType, "Host: Create a lobby for others to join \n"
                                              "User: Join a lobby with specific hostname and port")
        self.userType.grid(row=0, column=0)
        self.instructionsButton = Button(self.master, text="Instructions", command=self.openInstructions)
        self.instructionsButton.grid(row=0, column=1)

        self.ipString = StringVar()
        self.ipString.set("Enter a hostname here!")
        self.ipEntry = Entry(self.master, textvariable=self.ipString, width=25)
        self.nameString = StringVar()
        self.nameString.set("Enter your name here!")
        self.nameEntry = Entry(self.master, textvariable=self.nameString)
        self.enterButton = Button(self.master)
        self.portLabel = Label(self.master, text="Enter your port:")
        self.portNum = Spinbox(self.master, from_=10000, to_=13345, width=7)
        mainloop()

    def openInstructions(self):
        instructions = instructionsWindow()

    def changeMode(self, *args):
        """
            Changes the available options depending on the user's choice.
            Called by self.options.trace() function.
        :param args: needed arguments for .trace()
        :return: none
        """
        if self.options.get() == "Host":
            #Removes existing entities
            try:
                self.nameEntry.grid_forget()
                self.enterButton.grid_forget()
                self.ipEntry.grid_forget()
                self.portNum.grid_forget()
                self.portLabel.grid_forget()
            except:
                print("Something went wrong :(")

            self.nameTip = ToolTip(self.nameEntry, "What other users will see you as.")
            self.portTip = ToolTip(self.portLabel, "The port that others will connect to.")
            self.portTip = ToolTip(self.portNum, "The port that others will connect to.")
            self.enterTip = ToolTip(self.enterButton, "Create a lobby!")

            self.portLabel.grid(row=0, column=2)
            self.portNum.grid(row=0, column=3)

            self.nameEntry.grid(row=0, column=4)
            self.enterButton['text'] = "Host!"
            self.enterButton['command'] = self.newHost
            self.enterButton.grid(row=0, column=5)
        elif self.options.get() == "User":
            #Removes existing entities
            try:
                self.nameEntry.grid_forget()
                self.enterButton.grid_forget()
                self.portLabel.grid_forget()
                self.portNum.grid_forget()
            except:
                print("Something went wrong :(")

            self.nameTip = ToolTip(self.nameEntry, "What other users will see you as.")
            self.portTip = ToolTip(self.portLabel, "The port that you will connect to.")
            self.portTip = ToolTip(self.portNum, "The port that you will connect to.")
            self.enterTip = ToolTip(self.enterButton, "Enter a lobby!")
            self.ipTip = ToolTip(self.ipEntry, "The hostname to connect to.")

            self.portLabel['text'] = 'Enter a port:'
            self.ipEntry.grid(row=0, column=3, columnspan=2)
            self.portLabel.grid(row=0, column=5)
            self.portNum.grid(row=0, column=6)
            self.nameEntry.grid(row=1, column=4)
            self.enterButton['text'] = "Connect!"
            self.enterButton['command'] = self.newUser
            self.enterButton.grid(row=1, column=5)

    def newHost(self):
        """
            Creates a new connect.Host object from the user's settings
        :return: none
        """
        hostName = self.nameString.get()
        portNum = self.portNum.get()
        host = connect.Host(hostName, int(portNum))
        self.master.destroy()
        w = Window(host)

    def newUser(self):
        """
            Creates a new connect.User object from the user's settings
        :return: none
        """
        userName = self.nameString.get()
        user = connect.User(userName, self.ipString.get(), self.portNum.get())
        self.master.destroy()
        w = Window(user)

class instructionsWindow():
    def __init__(self):
        self.instructionRoot = Tk()
        self.instructionRoot.title("Instructions")
        self.hostLabel = Label(self.instructionRoot, text="""To Host a chatroom: Simply select an unused port number, enter your nameand press the \"host\" button.
        Then give the port number and hostname to those who want to connect.""")
        self.hostLabel.pack()

        self.connectLabel = Label(self.instructionRoot, text="""To connect to an existing room: Get the hostname and port number of
                                                   an existing room. Then enter your name and press the \"connect\" button!""")
        self.connectLabel.pack()
        self.instructionRoot.mainloop()

class Window():
    def __init__(self, newUser):
        """
            The constructor for the window that the user uses
            to send and receive messages
        :param newUser: takes either a connect.Host or a connect.User object
        :return: none
        """
        self.root = Tk()
        self.root.title(newUser.getName())
        self.messages = []
        self.messageBox = Listbox(self.root, listvariable=self.messages, width=50) #width is just a number to show messages
        self.messageBox.grid(row=0, column=0, columnspan=5)

        self.textEntry = Entry(self.root, width=40) #width is just for better formatting
        self.textEntry.grid(row=1, column=0)

        self.enterButton = Button(self.root, text="Send!", command=self.sendText)
        self.enterButton.grid(row=1, column=2)

        if isinstance(newUser, connect.Host): #creates a new thread for connect.Host.accept()
            self.hosting = True
            self.host = newUser
            self.hostThread = threading.Thread(target=self.host.accept, daemon=True) #daemon is True so the thread closes with the window
            self.hostThread.start()
        else: #creates a new thread for connect.User.accept()
            self.hosting = False
            self.user = newUser
            self.userThread = threading.Thread(target=self.user.accept, daemon=True) #daemon is True so the thread closes with the window
            self.userThread.start()
            self.user.connect()

        #a new thread to update the messages as the come in
        updateThread = threading.Thread(target=self.updateMessages, daemon=True) #daemon is True so the thread closes with the window
        updateThread.start()
        mainloop()

    def sendText(self):
        """
            Uses the sendMessage() function in either connect.Host or connect.User to send a message
            to the host or client(s).
        :return:
        """
        if not self.hosting: #changes to Host or User depending on prior options
            self.user.sendMessage(self.textEntry.get())
        else:
            self.host.sendMessage(self.textEntry.get())

        self.textEntry.delete(0, END)

    def updateMessages(self):
        """
            This updates the strings in self.messageBox as either self.host
            or self.user receives them
        :return:
        """
        while True:
            #probably not efficient
            if not self.hosting:
                received = self.user.getDecoded()
                if len(received) > len(self.messages):
                    for i in range(len(self.messages), len(received)): #adds any messages not in self.messageBox to self.messages
                        self.messages.append(received[i])
            else:
                received = self.host.getDecoded()
                if len(received) > len(self.messages):
                    for i in range(len(self.messages), len(received)): #adds any messages not in self.messageBox to self.messages
                        self.messages.append(received[i])

            for i in range(self.messageBox.size(), len(self.messages)): #adds anything in self.messages to self.messageBox that isn't already there
                self.messageBox.insert(END, self.messages[i])

            self.root.update() #needed or the widget won't change