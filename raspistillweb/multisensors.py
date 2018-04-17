#!/usr/bin/env python
from subprocess import Popen,PIPE, check_output,call
from os.path import splitext, join,split
from threading import Thread,Condition
import shlex
import re
from views import RASPISTILL_DIRECTORY

cv=Condition()
NewImages=False


def init_thread(app_settings):
    if ((app_settings.multisensor_enabled.lower() == 'yes') and (app_settings.multisensor_download_asynch.lower() == 'yes')):
        ips,macs = get_clients()
        hosts = zip(ips,macs)
        
        Thread(target=async_download_images,args=[hosts,app_settings.encoding_mode]).start()

def async_download_images(hosts,encoding_mode):
    global NewImages
    print "Async downloading initializated"
    while True:
        cv.acquire()
        while NewImages==False:
            cv.wait(60)
        cv.release()
        
        print '>>> DOWNLOADING NEW IMAGES'
        for ip,_ in hosts:
            call(['sshpass','-p','raspberry','scp','pi@'+ip+':*.'+encoding_mode,RASPISTILL_DIRECTORY])
            call(['sshpass','-p','raspberry',"ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, 'rm *.'+encoding_mode])
        
        NewImages= False
        print '<<< DOWNLOAD FINISHED'

def check_for_new_images(hosts,encoding_mode):
    global NewImages
    for ip,_ in hosts:
        try:
            output = check_output (["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, 'ls *.'+encoding_mode])
            cv.acquire()
            print '>>>NOTIFING'
            NewImages=True
            cv.notifyAll()
            cv.release()
            return True
        except:
            pass  #no images found
            
    return False



def shutdown_clients(hosts):
    for ip,_ in hosts:
        call (["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, 'sudo shutdown -hP now'],stdout=PIPE, shell=True)

def reboot_clients(hosts):
    for ip,_ in hosts:
        call (["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, 'sudo shutdown -r now'],stdout=PIPE, shell=True)

def get_clients_parameters(registered):
    lst = registered.split('\n')
    
    clients = {}
    
    for l in lst:
        tokens = l.split(',')
        params = {}
        mac = tokens[0].strip()
        if (len(tokens)>2):
            for i in range(2,len(tokens)):
                key,val = tokens[i].split('=');
                params[key.strip()] = val.strip()
        
        clients[mac] = params
    
    return clients
            

def map_client_name(suffix,clients_name):
    lst = clients_name.split('\n')
    
    n = len(suffix)
    
    for line in lst:
        tokens = line.split(',')
        mac = tokens[0].replace(':','')
        
        if (mac[-n:] == suffix):
            return tokens[1]
    
    return suffix

def trigger_pictures_from_clients(command,filename,download=True,join=True):
    threads = []
    
    ips,macs = get_clients()
    
    for host in zip(ips,macs):
        if (type(command) != dict):
            t = Thread(target=get_picture_from_using_ssh,args=([host],command,filename,download))
            t.start()
            threads.append(t)
        else:
            mac = host[1]
            print command
            if (mac in command.keys()):
                t = Thread(target=get_picture_from_using_ssh,args=([host],command[mac],filename,download),name='ClientAcq'+mac)
                t.start()
                threads.append(t)
    if join:
    	for t in threads:
        	t.join()
    else:
       return threads

def get_picture_from_using_ssh(hosts,command,filename,download=True,convertName=True):
    
    cmds = shlex.split(command,posix=True)
    for ip,mac in hosts:
        print "Getting image from %s" % ip
        try:
            
            print "Acquiring image"
            
            camera_id = ''.join(mac.split(':')[-2:])
                
            if (convertName):
                name,ext = splitext(filename)
                new_fname = name+".%s%s" % (camera_id,ext)
            else:
                new_fname = filename
            
            if download:
                command += ' -o -' 
                
                image = check_output(["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, command])
  
                print "Downloading image in %s" % new_fname
                
                handle = open(new_fname,'wb');
                handle.write(image)
                handle.close()
            else:
                _,filename = split(new_fname)
                command += ' -o '+ filename
                output = check_output(["sshpass", "-p", "raspberry", "ssh", '-oStrictHostKeyChecking=no', "pi@"+ip, command])
                print output
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
 
def get_registered_clients(registered,ip_keys=True):
    registered_clients = {  }
    clients = {}
    
    lst = registered.split('\n')
    
    is_registered = lambda x : x in registered_clients.keys()
    
    for c in lst:
        tokens = c.split(',')
        mac = str(tokens[0])
        name = tokens[1]
        
        registered_clients[mac] = name
        
    ips,macs = get_clients()
 
    
    for mac,ip in zip(macs,ips):
        if (is_registered(mac)):
            clients[ip if ip_keys else mac] = registered_clients[mac]
            
    return clients
    
    
    

def get_default_clients_name():
    _,macs = get_clients()
    
    names = []
    for j,mac in enumerate(macs):
        def_name = 'client_%d' % (j+1)
        line = '%s,%s' % (mac,def_name)
        
        names.append(line)
    
    return '\n'.join(names)
    
#def get_sensor_camera_configurations(mac,registered_clients):
#    lines = registered_clients.split('\n')
#    
#    for l in lines:
#        tokens = l.split(',')
#        if len(tokens)>2:
#            if (tokens[1] == mac):
#                params = tokens[2].split(';')
#                return { t.split('=')[0].strip():t.split('=')[1].strip() for t in params }
#    
#    return None
    
if (__name__ == "__main__"):
    print ("Current external clients")
    ips,macs=get_clients()
    
    for (ip,mac) in zip(ips,macs):
        print "\t"+ip +"\t"+mac
