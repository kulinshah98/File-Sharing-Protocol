import socket, os, time, re, mimetypes, hashlib


def md5(fn):
    hash = hashlib.md5()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def indexLongList(split_command):
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
        print info, len(info)
        conn.send(info)
        ans = conn.recv(1024)
        print ans
    conn.send("123")

def indexShortList(split_command):
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
        print mt, mint, maxt
        if mint <= os.path.getmtime(fl) <=maxt:
            info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
            print info, len(info)
            conn.send(info)
            ans = conn.recv(1024)
            print ans
    conn.send("123")

def indexRegex(split_command):
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
            print fl
            info+='\t'.join([fl, sz, ct, mt, f_type])+'\n'
            print info, len(info)
            conn.send(info)
            ans = conn.recv(1024)
            print ans
    conn.send("123")

def hashVerify(split_command):
    filename = split_command[2]
    check_sum = md5(filename)
    fl_stat = os.stat(filename)
    mt = time.ctime(fl_stat.st_mtime)
    st = str(check_sum) + " " + str(mt)
    conn.send(st)
    ans = conn.recv(1024)

def hashCheckAll(split_command):
    list_files = os.listdir('.')
    for fl in list_files:
        check_sum = md5(fl)
        fl_stat = os.stat(fl)
        mt = time.ctime(fl_stat.st_mtime)
        st = str(check_sum) + " " + str(mt)
        conn.send(st)
        ans = conn.recv(1024)

def downloadTCP(split_command):
    filename = split_command[2]
    hashf = md5(filename)
    conn.send(hashf)
    signal = conn.recv(1024)
    if signal=="yes":
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                conn.send(chunk)
                data = conn.recv(1024)
                print data
        conn.send("END")
        data = conn.recv(1024)
    else:
        pass

def downloadUDP(split_command):
    filename = split_command[2]
    stat = os.stat(filename)
    size = str(stat.st_size)
    mod_t = time.ctime(stat.st_mtime)
    hashval=md5(filename)
    conn.send(hashval)
    signal = conn.recv(1024)
    if signal=="yes":
        t_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        t_sock.bind(("", 51216))
        data, (taddr, destinport) = t_sock.recvfrom(1024)
        print data
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                #print(chunk)
                t_sock.sendto(chunk, (taddr, destinport))
        t_sock.sendto("END", (taddr, destinport))
        t_sock.close()
    else:
        pass





port = 51215
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)
print 'Server listening....'
conn, addr = s.accept()
print 'Got connection from', addr

while True:
    command = conn.recv(1024)
    split_command = command.split()
    if split_command[0]=="index":
        if split_command[1]=="longlist":
            indexLongList(split_command)
        elif split_command[1]=='shortlist':
            indexShortList(split_command)
        elif split_command[1]=='regex':
            indexRegex(split_command)
    elif split_command[0]=="hash":
        if split_command[1]=="verify":
            hashVerify(split_command)
        elif split_command[1]=="checkall":
            hashCheckAll(split_command)
        conn.send("123")
    elif split_command[0]=="download":
        if split_command[1]=="TCP":
            downloadTCP(split_command)
        elif split_command[1]=="UDP":
            downloadUDP(split_command)
        conn.send("123")
        data = conn.recv(1024)
    elif split_command[0]=="close":
        print "Closing connection"
        break
    #print('Server received', repr(data))

conn.close()
print('Connection closed')
