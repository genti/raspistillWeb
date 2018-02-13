#!/usr/bin/env python
from subprocess import Popen,PIPE, check_output
from os.path import splitext, join
import shlex
import re
from threading import Thread

def map_client_name(suffix,clients_name):
    lst = clients_name.split('\n')
    
    n = len(suffix)
    
    for line in lst:
        mac,name = line.split(',')
        mac = mac.replace(':','')
        
        if (mac[-n:] == suffix):
            return name
    
    return suffix

def trigger_pictures_from_clients(command,filename):
    threads = []
    
    ips,macs = get_clients()
    
    for host in zip(ips,macs):
        t = Thread(target=get_picture_from_using_ssh,args=([host],command,filename))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

def get_picture_from_using_ssh(hosts,command,filename):
    command += ' -o -' 
    cmds = shlex.split(command,posix=True)
    for ip,mac in hosts:
        print "Getting image from %s" % ip
        try:
            
            print "Acquiring image"
            

            image = check_output(["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, command])

            camera_id = ''.join(mac.split(':')[-2:])
            name,ext = splitext(filename)
            new_fname = name+".%s%s" % (camera_id,ext)
            
            print "Downloading image in %s" % new_fname
            
            handle = open(new_fname,'wb');
            handle.write(image)
            handle.close()
            
            print "[DONE]"
        except Exception as e:
            print "[ERROR] This is not a Phenotiki Device"      
            raise e


def get_clients():
    lst = Popen(['sudo', 'hostapd_cli', 'all_sta'],stdout=PIPE).stdout.read().split('\n')
    
    mac = []
    
    prog = re.compile('^([0-9a-f]{2}:){5}[0-9a-f]{2}$',flags=re.I)
    
    for line in lst:
        if (prog.match(line)):
            mac.append(line)
    
    mac = sorted(mac)
            
    lst = Popen(['arp', '-a', '-n'],stdout=PIPE).stdout.read().split('\n')
    
    found_ip = []
    found_mac = []
    prog = re.compile('([0-9]{1,3}\.){3}[0-9]{1,3}')
    for m in mac:
        for line in lst:
            if m in line:
                res = prog.search(line)
                found_ip.append(res.group())
                found_mac.append(m)
    
    return found_ip,mac
 
def get_registered_clients(registered):
    registered_clients = {  }
    clients = {}
    
    lst = registered.split('\n')
    
    is_registered = lambda x : x in registered_clients.keys()
    
    for c in lst:
        mac,name = c.split(',')
        
        registered_clients[str(mac)] = name
        
    ips,macs = get_clients()
 
    
    for mac,ip in zip(macs,ips):
        if (is_registered(mac)):
            clients[ip] = registered_clients[mac]
            
    return clients
    
    
    

def get_default_clients_name():
    _,macs = get_clients()
    
    names = []
    for j,mac in enumerate(macs):
        def_name = 'client_%d' % (j+1)
        line = '%s,%s' % (mac,def_name)
        
        names.append(line)
    
    return '\n'.join(names)
    
if (__name__ == "__main__"):
    print ("Current external clients")
    ips,macs=get_clients()
    
    for (ip,mac) in zip(ips,macs):
        print "\t"+ip +"\t"+mac
