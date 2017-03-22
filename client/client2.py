import socket, os, time, re, mimetypes, hashlib, threading


def md5(fn):
    hash = hashlib.md5()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def indexLongList(split_command, conn):
    list_files = os.listdir('.')
    #s.send('hi')
    for fl in list_files:
        info=""
        fl_stat = os.stat(fl)
        sz = str(fl_stat.st_size)
        ct = time.ctime(fl_stat.st_ctime)
        mt = time.ctime(fl_stat.st_mtime)
        f_type, code = mimetypes.guess_type(fl, False)
        if not f_type:
            f_type = "Unknown"
        info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
        #print info, len(info)
        conn.send(info)
        ans = conn.recv(4096)
        #print ans
    conn.send("123")

def indexShortList(split_command, conn):
    list_files = os.listdir('.')
    for fl in list_files:
        mint=time.mktime(time.strptime(' '.join(split_command[2:6]), '%d %m %Y %H:%M:%S'))
        maxt=time.mktime(time.strptime(' '.join(split_command[6:10]), '%d %m %Y %H:%M:%S'))
        info=""
        fl_stat = os.stat(fl)
        sz = str(fl_stat.st_size)
        ct = time.ctime(fl_stat.st_ctime)
        mt = time.ctime(fl_stat.st_mtime)
        f_type, code = mimetypes.guess_type(fl, False)
        if not f_type:
            f_type = "Unknown"
        #print mt, mint, maxt
        if mint <= os.path.getmtime(fl) <=maxt:
            info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
            #print info, len(info)
            conn.send(info)
            ans = conn.recv(4096)
            #print ans
    conn.send("123")

def indexRegex(split_command, conn):
    list_files = os.listdir('.')
    #s.send('hi')
    reprog = re.compile(' '.join(split_command[2:]).strip())
    for fl in list_files:
        info=""
        fl_stat = os.stat(fl)
        sz = str(fl_stat.st_size)
        ct = time.ctime(fl_stat.st_ctime)
        mt = time.ctime(fl_stat.st_mtime)
        f_type, code = mimetypes.guess_type(fl, False)
        if not f_type:
            f_type = "Unknown"
        if reprog.match(fl):
            info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
            conn.send(info)
            ans = conn.recv(4096)
    conn.send("123")

def hashVerify(split_command, conn):
    filename = split_command[2]
    check_sum = md5(filename)
    fl_stat = os.stat(filename)
    mt = time.ctime(fl_stat.st_mtime)
    st = str(check_sum) + " " + str(mt)
    conn.send(st)
    ans = conn.recv(4096)

def hashCheckAll(split_command, conn):
    list_files = os.listdir('.')
    for fl in list_files:
        check_sum = md5(fl)
        fl_stat = os.stat(fl)
        mt = time.ctime(fl_stat.st_mtime)
        st = str(check_sum) + " " + str(mt)
        conn.send(st)
        ans = conn.recv(4096)

def downloadTCP(filename, conn2):
    hashf = md5(filename)
    conn2.send(hashf)
    signal = conn2.recv(4096)
    if signal=="yes":
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                conn2.send(chunk)
                data = conn2.recv(4096)
        conn2.send("END")
        data = conn2.recv(4096)
    else:
        pass

def downloadUDP(split_command, conn):
    filename = split_command[2]
    stat = os.stat(filename)
    size = str(stat.st_size)
    mod_t = time.ctime(stat.st_mtime)
    hashval=md5(filename)
    conn.send(hashval)
    signal = conn.recv(4096)
    if signal=="yes":
        t_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        t_sock.bind(("", 51218))
        data, (taddr, destinport) = t_sock.recvfrom(4096)
        print data
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                #print(chunk)
                t_sock.sendto(chunk, (taddr, destinport))
        t_sock.sendto("END", (taddr, destinport))
        t_sock.close()
    else:
        pass

def server_func():
    print "started Client"
    s1 = socket.socket()
    host1 = ""
    port1 = 51217
    print host1, port1
    s1.connect((host1, port1))
    print "started Client"
    #s1.send("Hello server!")

    while True:
        command = s1.recv(4096)
        split_command = command.split()
        if split_command[0]=="index":
            if split_command[1]=="longlist":
                indexLongList(split_command, s1)
            elif split_command[1]=='shortlist':
                indexShortList(split_command, s1)
            elif split_command[1]=='regex':
                indexRegex(split_command, s1)
        elif split_command[0]=="hash":
            if split_command[1]=="verify":
                if os.path.isfile(split_command[2]):
                    hashVerify(split_command, s1)
                else:
                    print "Invalid Command"
            elif split_command[1]=="checkall":
                hashCheckAll(split_command, s1)
            s1.send("123")
        elif split_command[0]=="download":
            if split_command[1]=="TCP":
                if os.path.isfile(split_command[2]):
                    downloadTCP(split_command[2], s1)
                else:
                    print "Invalid Command"
            elif split_command[1]=="UDP":
                if os.path.isfile(split_command[2]):
                    downloadUDP(split_command, s1)
                else:
                    print "Invalid Command"
            s1.send("123")
            data = s1.recv(4096)
        elif split_command[0]=="sync":
            list_files = os.listdir('.')
            str_files = ""
            count1=0
            for f in list_files:
                if count1!=0:
                    str_files += " "
                str_files += f
                count1+=1
            s1.send(str_files)
            d = s1.recv(4096)
            for f in list_files:
                downloadTCP(f, s1)
            s1.send("123")
            data = s1.recv(4096)
        elif split_command[0]=="close":
            print "Closing connection"
            break
        #print('Server received', repr(data))

    s1.close()
    print('Connection closed')


def downloadTCPfile(fn12, s2):
    print fn12
    with open(fn12, "wb") as f:
        print "File Opened"
        data1 = s2.recv(4096)
        print data1
        s2.send("Done")
        while data1!="END":
            f.write(data1)
            #print data
            data1 = s2.recv(4096)
            s2.send("Done")

def downloadUDPfile(split_command, s2):
    f_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    f_socket.sendto("abcd", ("", 51216))
    with open(split_command[2], 'wb') as f:
        #print("File opened")
        #print info
        while True:
            print("Receiving Data")
            info, udpaddr = f_socket.recvfrom(4096)
            #print(info)
            #print("Data=%s", (info))
            if info=="END":
                break
            f.write(info)
    f_socket.close()

def client_func():
    print "started Client"
    s = socket.socket()
    count1=1
    host = ""
    port = 51215
    print host, port
    s.connect((host, port))
    print "started Client"
    s.send("Hello server!")

    while True:
        count1 = count1 + 1
        command = ""   
        if count1%2==0:
            print "Prompt ->",
            command = raw_input()
        elif count1%2==1 and count1>=3:
            command = "sync"
        print "=====", count1, command
        s.send(command)
        split_command = command.split()
        if split_command[0]=="download":
            if split_command[1]=="TCP":
                hashfs = s.recv(4096)
                if os.path.isfile(split_command[2]):
                    hashfc = md5(split_command[2])
                    print str(hashfs), str(hashfc)
                    if str(hashfs)!=str(hashfc):
                        s.send("yes")
                        print "Downloading File"
                        downloadTCPfile(split_command[2], s)
                    else:
                        s.send("no")
                else:
                    s.send("yes")
                    print "Downloading File"
                    downloadTCPfile(split_command[2], s)
            elif split_command[1]=="UDP":
                hashfs = s.recv(4096)
                if os.path.isfile(split_command[2]):
                    hashfc = md5(split_command[2])
                    if str(hashfs)!=str(hashfc):
                        s.send("yes")
                        print "Downloading File"
                        downloadUDPfile(split_command, s)
                    else:
                        s.send("no")
                else:
                    s.send("yes")
                    print "Downloading File"
                    downloadUDPfile(split_command, s)
        elif split_command[0]=="sync":
            list_files = s.recv(4096).split()
            s.send("done")
            for f in list_files:
                hashfs = s.recv(4096)
                if os.path.isfile(f):
                    hashfc = md5(f)
                    #print str(hashfs), str(hashfc)
                    if str(hashfs)!=str(hashfc):
                        s.send("yes")
                        print "Downloading File"
                        downloadTCPfile(f, s)
                    else:
                        s.send("no")
                else:
                    s.send("yes")
                    print "Downloading File"
                    downloadTCPfile(f, s)
        elif split_command[0]=="close":
            print "Closing connection"
            break

        data = s.recv(4096)
        s.send("done")
        while data!="123":
            print data
            data = s.recv(4096)
            s.send("done")
        print command

    s.close()
    print('Connection closed')


server_thread = threading.Thread(name='server', target=server_func)
client_thread = threading.Thread(name='client', target=client_func)

server_thread.start()
client_thread.start()
