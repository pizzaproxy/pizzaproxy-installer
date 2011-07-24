#!/usr/bin/python
#
# PizzaProxy Setup file for easier setup/removal
import sys
import shutil
import os
import ConfigParser

def write_apache_config(path,project,domain,wwwroot):
    config = open('apache_sample_config').read().replace('PROJECT',project).replace('DOMAIN',domain).replace('WWW-ROOT',wwwroot)
    file = open(path + project + '.' + domain + '.conf')
    file.write(config)
    file.close()
    print config

def delete_apache_config(path,project,domain):
    os.remove(path + project + '.' + domain + '.conf')

def restart_apache():
    os.system('/etc/init.d/apache2 restart')

def help():
    print 'Usage '+sys.argv[0]+' install/remove <SHORTEVENTALIAS> <EVENTNAME>'

def publish(eventfile,shortname,name,url):
    evconf = ConfigParser.RawConfigParser()
    if os.path.exists(eventfile):
        evconf.readfp(open(eventfile))
    evconf.add_section(shortname)
    evconf.set(shortname,'name',name)
    evconf.set(shortname,'url',url)
    with open(eventfile,'w+') as neweventfile:
            evconf.write(neweventfile)

def unpublish(eventfile,shortname):
    evconf = ConfigParser.RawConfigParser()
    evconf.readfp(open(eventfile))
    evconf.remove_section(shortname)
    with open(eventfile,'w+') as neweventfile:
        evconf.write(neweventfile)

"""
Check amount of commandline arguments
"""
if len(sys.argv) <> 4:
    help()
    sys.exit(1)
if sys.argv[1] not in ('install','remove'):
    help()
    sys.exit(1)
"""
So far everything looks okay with the commandline arguments
Let's go on with the installation process \o/
"""
config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

"""
Declare often used variables to clean up code
"""
action = sys.argv[1]
shortname = sys.argv[2]
eventname = sys.argv[3]

apache_create_config = config.get('main','apache-create-config')
apache_restart = config.get('main','apache-restart')
apache_vhost_dir = config.get('main','apache-vhost-dir')
domain = config.get('main','domain')
www_root = config.get('main','www-root')
event_file = config.get('main','event-file')

"""
Let's handle the installation stuff,
checking whether we should create the config file
and where to publish the eventfile and so on
"""
if action == 'install':
    if apache_create_config == 'true':
        # publish under short-alias!
        write_apache_config(apache_vhost_dir,shortname,domain,www_root)
    if not os.path.exists(www_root+shortname+"."+domain+"/htdocs/"):
        os.makedirs(www_root+shortname+"."+domain+"/htdocs/")
    shutil.copytree("../web/",www_root+shortname+"."+domain+"/htdocs/")
    print "Do not forget to open http://"+shortname+"."+domain+"/setup.php before you start"
    if apache_restart == 'true':
        restart_apache()
    publish(event_file,shortname,eventname,shortname+"."+domain)
else:
    delete_apache_config(apache_vhost_dir,shortname,domain)
    shutil.rmtree(www_root+shortname+"."+domain)
    if apache_restart == 'true':
        restart_apache()
    unpublish(event_file,shortname)

