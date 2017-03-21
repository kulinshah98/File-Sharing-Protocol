import socket, os, time, re, mimetypes, hashlib


def md5(fn):
    hash = hashlib.md5()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

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
                info+='\t'.join([fl,                data = conn.recv(1024)
                    print data
            conn.send("END")
            conn.recv(1024)
            conn.send(hashf)
            data = conn.recv(1024)
        elif split_command[1]=="UDP":
            filename = split_command[2]
            t_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            t_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            t_sock.bind(("", 51216))
            conn.recv(1024)
            stat = os.stat(filename)
            size = str(stat.st_size)
            mod_t = time.ctime(stat.st_mtime)
            hashval=md5(filename)
            fileinfo = str(filename) + ' ' + str(size) + ' ' + str(mod_t) + ' ' + str(hashval) + '\n'
            conn.send(fileinfo)
            data, (taddr, destinport) = t_sock.recvfrom(1024)
            print data
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    #print(chunk)
                    t_sock.sendto(ch