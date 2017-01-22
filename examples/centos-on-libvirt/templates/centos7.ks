network --bootproto dhcp
url --url http://ftp.belnet.be/ftp.centos.org/7/os/x86_64
repo --name=updates --baseurl=http://ftp.belnet.be/ftp.centos.org/7/updates/x86_64

services --disabled=ip6tables,iptables,netfs,rawdevices --enabled=network,sshd

install
text
skipx
poweroff

lang en_US.UTF-8
keyboard --vckeymap=us
timezone Europe/Brussels --isUtc --nontp
auth --enableshadow --passalgo=sha512
rootpw "centos"
firewall --disabled
selinux --enforcing

zerombr
bootloader --location=mbr
clearpart --all --initlabel

part /boot --fstype=xfs --size=500 --asprimary --fsoptions="defaults"
part pv.01 --size=1 --grow
volgroup vg_root pv.01 --pesize=32768
logvol /    --fstype=xfs  --name=lv_root --vgname=vg_root --size=4096 --fsoptions="defaults,relatime"
logvol /var --fstype=xfs --name=lv_var --vgname=vg_root --size=4096
logvol /tmp --fstype=xfs --name=lv_tmp --vgname=vg_root --size=1024
logvol swap --fstype=swap --name=lv_swap --vgname=vg_root --size=512 --fsoptions="defaults"

%packages --nobase
@core --nodefaults
-*-firmware
-NetworkManager*
-alsa*
-audit
-cron*
-iprutils
-kexec-tools
-microcode_ctl
-plymouth*
-postfix
-rdma
-tuned
-wpa_supplicant
%end
