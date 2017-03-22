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
        if reprog.search(fl):
            #print fl
            info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
            #print info, len(info)
            conn.send(info)
            ans = conn.recv(4096)
            #print ans
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
        st = str(fl) + "   " + str(check_sum) + "   " + str(mt)
        conn.send(st)
        ans = conn.recv(4096)

def downloadTCP(filename, conn):
    hashf = md5(filename)
    conn.send(hashf)
    signal = conn.recv(4096)
    if signal=="yes":
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                conn.send(chunk)
                data = conn.recv(4096)
                #print data
        conn.send("END")
        data = conn.recv(4096)
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
        t_sock.bind(("", 51216))
        data, (taddr, destinport) = t_sock.recvfrom(4096)
        #print data
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                #print(chunk)
                t_sock.sendto(chunk, (taddr, destinport))
        t_sock.sendto("END", (taddr, destinport))
        t_sock.close()
    else:
        pass

def server_func():
    port = 51215
    s1 = socket.socket()
    host = ""

    s1.bind((host, port))
    s1.listen(5)
    conn1, addr1 = s1.accept()

    while True:
        command = conn1.recv(4096)
        split_command = command.split()
        if split_command[0]=="index":
            if split_command[1]=="longlist":
                indexLongList(split_command, conn1)
            elif split_command[1]=='shortlist':
                indexShortList(split_command, conn1)
            elif split_command[1]=='regex':
                indexRegex(split_command, conn1)
        elif split_command[0]=="hash":
            if split_command[1]=="verify":
                hashVerify(split_command, conn1)
            elif split_command[1]=="checkall":
                hashCheckAll(split_command, conn1)
            conn1.send("123")
        elif split_command[0]=="download":
            if split_command[1]=="TCP":
                downloadTCP(split_command[2], conn1)
            elif split_command[1]=="UDP":
                downloadUDP(split_command, conn1)
            conn1.send("123")
            data = conn1.recv(4096)
        elif split_command[0]=="sync":
            list_files = os.listdir('.')
            str_files = ""
            for f in list_files:
                str_files += (f + " ")
            conn1.send(str_files)
            d = conn1.recv(4096)
            for f in list_files:
                downloadTCP(f, conn1)
            conn1.send("123")
            data = conn1.recv(4096)
        elif split_command[0]=="close":
            print "Closing connection"
            break
        #print('Server received', repr(data))

    conn1.close()
    print('Connection closed')


def downloadTCPfile(fn, s):
    with open(fn, "wb") as f:
        #print "File Opened"
        data = s.recv(4096)
        s.send("Done")
        while data!="END":
            f.write(data)
            #print data
            data = s.recv(4096)
            s.send("Done")

def downloadUDPfile(split_command, s):
    f_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    f_socket.sendto("abcd", ("", 51218))
    with open(split_command[2], 'wb') as f:
        #print("File opened")
        while True:
            #print("Receiving Data")
            info, udpaddr = f_socket.recvfrom(4096)
            #print(info)
            #print("Data=%s", (info))
            if info=="END":
                break
            f.write(info)
    f_socket.close()

def client_func():
    port1 = 51217
    s = socket.socket()
    host1 = ""
    count2=0
    s.bind((host1, port1))
    s.listen(5)
    conn, addr = s.accept()
    syncMode = 0

    while True:
        count2 = count2 + 1
        if syncMode==0:
            if count2%2==0:
                print "Prompt ->",
                command = raw_input()
            elif count2%2==1 and count2>=1:
                command = "sync"
        elif syncMode==1:
            sleep(7)
            command="sync"
        elif syncMode==2:
            syncMode=0
        #print command
        conn.send(command)
        split_command = command.split()
        if split_command[0]=="download":
            if len(split_command)<3:
                print "Invalid Command"
            elif split_command[1]=="TCP":
                hashfs = conn.recv(4096)
                if os.path.isfile(split_command[2]):
                    hashfc = md5(split_command[2])
                    #print str(hashfs), str(hashfc)
                    if str(hashfs)!=str(hashfc):
                        conn.send("yes")
                        print "Downloading File", split_command[2]
                        downloadTCPfile(split_command[2], conn)
                    else:
                        conn.send("no")
                else:
                    conn.send("yes")
                    print "Downloading File",split_command[2]
                    downloadTCPfile(split_command[2], conn)
            elif split_command[1]=="UDP":
                hashfs = conn.recv(4096)
                if os.path.isfile(split_command[2]):
                    hashfc = md5(split_command[2])
                    if str(hashfs)!=str(hashfc):
                        conn.send("yes")
                        print "Downloading File", split_command[2]
                        downloadUDPfile(split_command, conn)
                    else:
                        conn.send("no")
                else:
                    conn.send("yes")
                    print "Downloading File", split_command[2]
                    downloadUDPfile(split_command, conn)
                hashfc = md5(split_command[2])
                if str(hashfs)!=str(hashfc):
                    print "Unsuccessful Download"
                    syncMode=2
        elif split_command[0]=="sync":
            list_files = conn.recv(4096).split()
            conn.send("done")
            for f in list_files:
                hashfs = conn.recv(4096)
                if os.path.isfile(f):
                    hashfc = md5(f)
                #    print str(hashfs), str(hashfc)
                    if str(hashfs)!=str(hashfc):
                        conn.send("yes")
                        print "Downloading File", f
                        downloadTCPfile(f, conn)
                    else:
                        conn.send("no")
                else:
                    conn.send("yes")
                    print "Downloading File", f
                    downloadTCPfile(f, conn)
        elif split_command[0]=="close":
            print "Closing connection"
            break

        data = conn.recv(4096)
        conn.send("done")
        while data!="123":
            print data
            data = conn.recv(4096)
            conn.send("done")
        #print command
    #f.close()
    conn.close()
    print('Connection closed')




server_thread = threading.Thread(name='server', target=server_func)
client_thread = threading.Thread(name='client', target=client_func)

server_thread.start()
client_thread.start()
