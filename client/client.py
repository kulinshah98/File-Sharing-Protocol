import os, socket, hashlib, time, re, mimetypes, threading

def md5(fn):
    hash = hashlib.md5()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def downloadTCPfile(split_command):
    with open(split_command[2], "wb") as f:
        print "File Opened"
        data = s.recv(1024)
        s.send("Done")
        while data!="END":
            f.write(data)
            #print data
            data = s.recv(1024)
            s.send("Done")

def downloadUDPfile(split_command):
    f_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    f_socket.sendto("abcd", ("", 51216))
    with open(split_command[2], 'wb') as f:
        print("File opened")
        while True:
            print("Receiving Data")
            info, udpaddr = f_socket.recvfrom(1024)
            print(info)
            #print("Data=%s", (info))
            if info=="END":
                break
            f.write(info)
    f_socket.close()


s = socket.socket()
host = ""
port = 51215

s.connect((host, port))
s.send("Hello server!")

while True:
    print "Prompt ->",
    command = raw_input()
    s.send(command)
    count=0
    split_command = command.split()
    if split_command[0]=="download":
        if split_command[1]=="TCP":
            hashfs = s.recv(1024)
            if os.path.isfile(split_command[2]):
                hashfc = md5(split_command[2])
                print str(hashfs), str(hashfc)
                if str(hashfs)!=str(hashfc):
                    s.send("yes")
                    print "Downloading File"
                    downloadTCPfile(split_command)
                else:
                    s.send("no")
            else:
                s.send("yes")
                print "Downloading File"
                downloadTCPfile(split_command)
        elif split_command[1]=="UDP":
            hashfs = s.recv(1024)
            if os.path.isfile(split_command[2]):
                hashfc = md5(split_command[2])
                if str(hashfs)!=str(hashfc):
                    s.send("yes")
                    print "Downloading File"
                    downloadUDPfile(split_command)
                else:
                    s.send("no")
            else:
                s.send("yes")
                print "Downloading File"
                downloadUDPfile(split_command)
    elif split_command[0]=="close":
        print "Closing connection"
        break

    data = s.recv(1024)
    s.send("done")
    while data!="123":
        print data
        data = s.recv(1024)
        s.send("done")
    print command
#f.close()

s.close()
print('Connection closed')
