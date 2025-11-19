# Clients register with the follwing format:
# name
# description
# list of publishers
#.   each publisher has a type of boolean, range (0-1023), string, or json
# list of subscribers
#.   each subscriber has a type of boolean, range (0-1023), string, or json

# name, desc, pubs(pub1:type, pub2:type, pub3:type), subs(sub1:type, sub2:type, sub3:type)

class Spacebrew2Client:
    def __init__(self, clientName, clientDesc, clientPubs, clientSubs):
        self.clientName = clientName
        self.clientDesc = clientDesc
        self.clientPubs = clientPubs # Expecting a list of dicts or strings
        self.clientSubs = clientSubs # Expecting a list of dicts or strings