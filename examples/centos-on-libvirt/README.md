# Provisioning a CentOS 7 VM on libvirt

This example demonstrates how the `virt_guest`, `virt_boot` and `qemu_img` modules work together to provision a minimal CentOS 7 VM on a hypervisor running libvirt.

## Requirements

* libvirt with KVM
* libvirt storage in `/var/lib/libvirt/images`
* a `default` libvirt network with dhcp enabled and internet access

This example assumes your local machine is the hypervisor. You might want to update the inventory in `hosts` if this is not the case.

## How it works

A first play runs on the hypervisor. It starts by allocating qcow2 storage for the VM. Then it defines a libvirt virtual machine definition and ensures it is defined in libvirt. If the VM was previously unprovisioned, it will be added to a group with that name.

The second play downloads the CentOS 7 kernel and initrd from a CentOS mirror. It boots the VM using libvirt direct kernel booting and kickstarts the machine. Once this is done, the VM is booted from the qcow2 disk.

## The real world

The CentOS kickstart is fetched from this repository over the internet. In a realistic case these options are typically used:

* build an iso image containing the kernel, initrd and kickstart and use `virt_boot` to boot from CD-ROM
* template the kickstart to a web server you control

A realistic network configuration is also left as an exercise for the reader, just like adding your SSH key in the kickstart.

## Example

```bash
[jeroen@island ansible-provisioning]$ ansible-playbook examples/centos-on-libvirt/centos-on-libvirt.yml -i examples/centos-on-libvirt/hosts

PLAY [Provision a CentOS VM on libvirt] ****************************************

TASK [Allocate storage for the VM] *********************************************
ok: [centos7 -> localhost]

TASK [Create a folder for VM definitions] **************************************
ok: [centos7 -> localhost]

TASK [Create a VM definition] **************************************************
ok: [centos7 -> localhost]

TASK [Create the VM] ***********************************************************
changed: [centos7 -> localhost]

TASK [Create a group of unprovisioned systems] *********************************
ok: [centos7 -> localhost]

PLAY [Provision unprovisioned systems] *****************************************

TASK [Create VM image directory] ***********************************************
ok: [centos7 -> localhost]

TASK [Download PXE images] *****************************************************
ok: [centos7 -> localhost] => (item=initrd.img)
ok: [centos7 -> localhost] => (item=vmlinuz)

TASK [Boot the VM using the PXE images] ****************************************
changed: [centos7 -> localhost]

TASK [Wait until the VM stops] *************************************************
FAILED - RETRYING: TASK: Wait until the VM stops (120 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (119 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (118 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (117 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (116 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (115 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (114 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (113 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (112 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (111 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (110 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (109 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (108 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (107 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (106 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (105 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (104 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (103 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (102 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (101 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (100 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (99 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (98 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (97 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (96 retries left).
FAILED - RETRYING: TASK: Wait until the VM stops (95 retries left).
ok: [centos7 -> localhost]

TASK [Start the VM] ************************************************************
changed: [centos7 -> localhost]

PLAY RECAP *********************************************************************
centos7                    : ok=10   changed=3    unreachable=0    failed=0
```

