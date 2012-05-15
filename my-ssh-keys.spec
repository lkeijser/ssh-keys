Name:           my-ssh-keys
Version:        1.0
Release:        1
Summary:        SSH key based access user management

Group:          Applications/Internet
License:        GPLv2+
URL:            https://github.com/lkeijser/ssh-keys
Source0:        https://github.com/lkeijser/ssh-keys/downloads/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       openssh, python

%description
Package containing logic for managing 
individual ssh access for specific users
in an ssh-keys file

CAUTION: you will need to review this SPEC file
and most likely modify it (file/path names) to 
fit your needs.


%prep
%setup -q


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__install} -m 644 -D ssh-keys-file $RPM_BUILD_ROOT/%{_datadir}/my-ssh-keys/ssh-keys-file
%{__install} -m 755 -D deploy.py $RPM_BUILD_ROOT/%{_datadir}/my-ssh-keys/deploy.py

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README
%{_datadir}/my-ssh-keys/ssh-keys-file
%{_datadir}/my-ssh-keys/deploy.py*

%post
%{__python} %{_datadir}/my-ssh-keys/deploy.py

%postun
# 0 : remove, 1 : upgrade
method=$1
echo "postun called with arg $method"
if [ $method -eq 0 ];then
    rm -rf %{_datadir}/my-ssh-keys
    echo "Removing users.."
    for u in `ls -1 /home/admins/`; do
        userdel -r -f $u
        echo "Removed user $u"
    done
    echo "Removing /home/admins.." 
    rm -rf /home/admins/
fi

%changelog
* Tue May 15 2012 L.S. Keijser <leon@gotlinux.nl> - 1.0-1
- initial release

