#!/usr/bin/env python

"""
    This is a small script for user management with ssh-keys

    Copyright (C) 2012 L.S. Keijser <leon@gotlinux.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import glob
import os
import sys

# define generic homedir
homedir = '/home/admins'
# file containing  ssh keys
userfile = '/root/ssh-keys-file'
# define generic group
group = 'admins'
# define prefix (this should also be present in the SSH keys file in the comment
# section of the key. For example:
# ssh-rsa AA.....== admin-username@example.com
prefix = 'admin-'


def check_selinux():
    # first, check if the restorecon binary is present
    if os.path.exists('/sbin/restorecon'):
        # do a restorecon on our homedir
        print "SELinux detected. Restoring file security contexts on %s" % homedir
        cmd = '/sbin/restorecon %s' % homedir
        os.system(cmd)

def install():
    # check if generic homedir exists and create it if it doesn't
    if not os.path.exists(homedir):
        print "Generic homedir %s did not exist. Creating.." % homedir
        os.makedirs(homedir)

    # check if default group exists and create it if it doesn't
    f = open('/etc/group', 'r')
    groupexists=0
    for g in f.readlines():
        if g.startswith(group):
            # group exists, do nothing
            groupexists=1
    if groupexists == 0:
        print "Default group %s did not exist. Creating.." % group
        os.system('groupadd ' + group)

    # open keys file and build a dictionary of users:ssh-key
    users = {}
    for line in open(userfile, 'r').readlines():
        user = prefix + line.split(' ')[2].split('@')[0]
        users[user] = line

    # check if subdirectories already present are valid users
    for dirs in glob.glob(homedir + '/' + prefix + '*'):
        userdir = dirs.split('/')[-1]
        if users.get(userdir, 'None') == 'None':
            print "Found dir %s that is NOT a valid user according to our keys file!" % userdir
            if os.system('id ' + userdir + ' > /dev/null 2>&1'):
                # somebody created a normal directory which we'll leave alone
                print "User %s did NOT exist on system. Possibly non-homedir. Skipping.." % userdir
            else:
                # try to remove the user if it exists on the system
                print "User %s found on system. Removing user.." % userdir
                os.system('userdel -r -f ' + userdir)

    # for each user in keys file, create the user if not present yet
    for user, sshkey in users.iteritems():
        if os.system('id ' + user + ' > /dev/null 2>&1'):
            print "User %s is NOT present yet. Creating.." % user
            os.system('useradd -m -G ' + group + ' -d ' + homedir + '/' + user + ' -s /bin/bash ' + user)
            # create ssh subdir if it doesn't exist yet
            if not os.path.exists(homedir + '/' + user + '/.ssh'):
                os.makedirs(homedir + '/' + user + '/.ssh')
            # write ssh key to authorized_keys file
            f = open(homedir + '/' + user + '/.ssh/authorized_keys', 'w')
            f.write(sshkey)
            f.close()
            # set correct ownership and permissions
            os.system('chown -R ' + user + ':' + user + ' ' + homedir + '/' + user + '/.ssh')
            os.system('chmod 700 ' + homedir + '/' + user + '/.ssh')
            os.system('chmod 600 ' + homedir + '/' + user + '/.ssh/authorized_keys')
        else:
            print "Found valid user %s." % user
            # checking if user exists in default group, else add the user to it
            # this is to remain compatible with older versions of this script
            f = open('/etc/group')
            for line in f.readlines():
                if line.startswith(group + ':'):
                    match = line.strip()
                    if user in match:
                        # user already in group
                        pass
                    else:
                        # adding user to group
                        print "Adding user %s to group %s.." % (user,group)
                        os.system('usermod -a -G ' + group + ' ' + user)
            f.close()


if __name__ == "__main__":
    install()
    check_selinux()
