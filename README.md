Provisioning with Ansible
=========================

Ansible is a radically simple configuration-management, deployment, task-execution and multinode orchestration framework. Its modular design enables to extend core functionality with custom or specific needs.

This sub-project extends Ansible for provisioning so that orchestrating the installation of new systems is using the same methodology and processes as normal systems management. It includes modules for adding inventory information (facts) from external sources and modules for booting physical and virtual systems using (custom) boot media.

For more information about Ansible, read the documentation at http://ansible.cc/


Modules
=======
We currently provide the following modules for provisioning:

 - generic network information (network_facts)
 - LVM management (lvol)
 - HP iLO (hponcfg, hpilo_facts and hpilo_boot)
 - VMWare vSphere (vsphere_facts and vsphere_boot)
 - KVM (virt_guest, virt_facts and virt_boot)
 - VirtualBox (vbox_facts and vbox_boot)
 - Amazon EC² (ec2_create)

We anticipate contributions from users, e.g.

 - IPMI (ipmi_facts and ipmi_boot)
 - IBM RSA (ibmrsa_facts and ibmrsa_boot)
 - DELL DRAC (drac_facts and drac_boot)
 - Xen (as part of virt_guest, virt_facts and virt_boot ?)
 - VirtualBox (vbox_guest)
 - VMWare vSphere (vsphere_guest)
 - RHEV (rhev_guest, rhev_facts and rhev_boot)
 - Cobbler (cobbler_facts)
 - RHN (rhn_facts)

Anything that adds facts to systems (wrt. provisioning and/or systems management) has a place in this repository.


Example provisioning process
============================
Here is an example how you could perform the following steps:

 - Gather facts from separate network inventory (based on IP ranges)
 - Gather facts from HP iLO, KVM or vSphere
 - Create custom cdrom image for out-of-band ISO-based provisioning
 - Create custom PXE configuration for PXE-based provisioning
 - Boot system using ISO or PXE method
 - Clean up

The syntax of the network inventory yaml file only requires that a cidr-attribute exists for each entry. Based on the gw-option, a gateway strategy will add a gateway attribute (first or last address) if one is missing.  Everything else is optional depending on your use-case.

Here is an example *network-inventory.yml*:
```yaml
---
- vlan: 10
  cidr: 10.1.10.0/25
  description: Production servers in DMZ2
  nameservers: [ 10.1.2.10, 10.1.3.10 ]
  domains: [ prod.corp.intra, hw.corp.intra, mgmt.corp.intra ]
  environment: prod
  datacenter: brussels
  tier: dmz2
  gateway: 10.1.10.232
- vlan: 15
  cidr: 10.2.12.0/25
  description: QA servers in DMZ3
  nameservers: [ 10.1.2.10, 10.1.3.10 ]
  domains: [ nonprod.corp.intra, hw.corp.intra, mgmt.corp.intra ]
  environment: nonprod
  datacenter: antwerp
  tier: dmz3
- vlan: 20
  cidr: 10.3.148.0/22
  description: Management servers in Trusted
  environment: nonprod
  datacenter: antwerp
  tier: trusted
```

And here is an example of how one would be using hpilo, vsphere, kvm and network plugins for provisioning systems:
```yaml
- name: quick provisioning
  hosts: all
  gather_facts: False

  vars:
    rhel_version: 6.3
    kickstart_file: /var/www/html/ks/${inventory_hostname_short}.cfg
    iso_image: /iso/ks/${inventory_hostname_short}.iso
    rhel_pxeboot: /var/www/mrepo/rhel${rhel_version}-x86_64/disc1/images/pxeboot/.
    isolinux_bin: /usr/share/syslinux/isolinux.bin

  tasks:
  ### Safeguard to protect production systems
  - local_action: fail msg="Safeguard - System is not set to 'to-be-staged' in CMDB"
    only_if: "'$cmdb_status' != 'to-be-staged'"

  ### Get network facts
  - local_action: network_facts host='${inventory_hostname_short}' inventory='../network-inventory.yml' full='yes'

  ### Get HP iLO facts (iLO credentials from group_vars)
  - local_action: hpilo_facts host='${cmdb_parent}' login='${ilologin}' password='${ilopassword}'
    only_if: "'${cmdb_hwtype}'.startswith('HP ')"

  ### Get vSphere facts (vSphere credentials group_vars, guests are named by uuid in vSphere)
  - local_action: vsphere_facts host='${cmdb_parent}' login='${esxlogin}' password='${esxpassword}' guest='${cmdb_uuid}'
    only_if: "'${cmdb_hwtype}'.startswith('VMWare ')"

  ### Get KVM facts (KVM hosts are managed by Ansible as well, guests are named by uuid in KVM)
  - local_action: virt_facts guest='${cmdb_uuid}'
    delegate_to: '${cmdb_parent}'
    only_if: "'${cmdb_hwtype}'.startswith('KVM')"

  ### Create a custom boot ISO (use network_facts info for kickstart templating)
  - local_action: command mktemp -d
    register: tempdir
  - local_action: command cp -av ${rhel_pxeboot} ${isolinux_bin} ${tempdir.stdout}
  - local_action: template src=../templates/kickstart/isolinux.cfg dest=${tempdir.stdout}/isolinux.cfg
  - local_action: template src=../templates/kickstart/ks.cfg dest=${tempdir.stdout}/ks.cfg
  - local_action: command mkisofs -r -N -allow-leading-dots -d -J -T -b isolinux.bin -c boot.cat -no-emul-boot -V "Ansible RHEL${rhel_version} for ${inventory_hostname_short}" -boot-load-size 4 -boot-info-table -o ${iso_image} ${tempdir.stdout}
  - local_action: command rm -rf ${tempdir.stdout}

  ### Create a custom kickstart and PXE configuration (based on iLO or ESX information), only one pxelinux config suffices !
  - local_action: template src=../templates/kickstart/ks.cfg dest=${kickstart_file}
  - local_action: template src=../templates/kickstart/pxelinux.cfg dest=/var/lib/tftpboot/pxelinux.cfg/$item
    with_items:
    - ${inventory_hostname_short}
    - ${hw_product_uuid}
    - ${hw_eth0.macaddress_dash}
    - ${network_ipaddress_hex}

  ### Kick off HP iLO provisioning
  - local_action: hpilo_boot host='${cmdb_parent}' login='${ilologin}' password='${ilopassword}' media='cdrom' image='http://${ansible_server}/iso/ks/${inventory_hostname_short}.iso' state='boot_once'
    only_if: "'${cmdb_hwtype}'.startswith('HP ')"

  ### Kick off vSphere provisioning
  - local_action: vsphere_boot host='${cmdb_parent}' login='${esxlogin}' password='${esxpassword}' guest='${cmdb_uuid}' media='cdrom' image='[nfs-datastore] /iso/ks/${inventory_hostname_short}.iso' state='boot_once'
    only_if: "'${cmdb_hwtype}'.startswith('VMWare ')"

  ### Kick off KVM provisioning
  - local_action: virt_boot guest='${cmdb_uuid}' media='cdrom' image='/iso/ks/${inventory_hostname_short}.iso' state='boot_once'
    delegate_to: '${cmdb_parent}'
    only_if: "'${cmdb_hwtype}'.startswith('KVM')"

  ### Revoke any existing host keys for this server (should become a separate ansible module to avoid conflicts)
  - local_action: command ssh-keygen -R ${inventory_hostname_short}
    ignore_errors: True

  ### Wait for the post-install SSH to become available
  - local_action: wait_for host=$inventory_hostname port=22 state=started timeout=1800 delay=180

  ### Remove PXE boot configuration (we keep the one using the hostname_short for debugging purposes)
  - local_action: file dest=/var/lib/tftpboot/pxelinux.cfg/$item state=absent
    with_items: [${network_ipaddress_hex}, ${hw_eth0.macaddress_dash}, ${hw_product_uuid}]

  ### Check if system is booted into Anaconda
  - local_action: fail msg="Safeguard - System has not booted into Anaconda post-install !"
    only_if: "is_unset('${ansible_cmdline.BOOT_IMAGE}')"

  ### Now continue with configuration management by including those playbooks here !

  ### Finally report success
  - local_action: |
      mail from="Provisioning of ${inventory_hostname} <root>"
      to="<root>"
      cc="<you>"
      subject="Server ${inventory_hostname_short} has been provisioned"
      body="We are happy to report that server ${inventory_hostname} was successfully provisioned.

      Here are some interesting characteristics of the server:

        - Full name: ${network_fqdn}
        - IP address: ${network_ipaddress}
        - Model: ${cmdb_model}
        - Location: ${cmdb_parent} / ${cmdb_datacenter} / ${cmdb_location} / ${cmdb_rack}

      Good luck and may you find your inner peace !
      "
```

Hardware facts module interface
===============================
Every facts module that returns (virtual/physical) hardware facts related to a system (using the hw_ namespace) should at least include the following facts:

    hw_architecture: "x86_64"
    hw_eth0:
    - macaddress: "00:11:22:33:44:55"        # MAC address of the first interface (usually used for provisioning)
      macaddress_dash: "00-11-22-33-44-55"   # MAC address in dashed notation (for syslinux)
    hw_product_uuid: "ef50bac8-2845-40ff-81d9-675315501dac"
    hw_power_status: ("on", "off")           # Indicates the current power status
    module_hw: true

This is necessary so that system facts can be reused in playbooks and tasks regardless of the hardware type.

Hardware boot module interface
==============================
There is a strict set of options that each of the hardware boot modules should accept. Currently the options and values are close to what the interface to the (physical/virtual) hardware uses, but we should harmonize this so all modules accept similar options in the future.

The boot module should return the following facts:

    boot_power_status: ("on", "off")         # Indicates the power status as it was before changing it
    module_boot: true

This is necessary so that system facts can be reused in playbooks and tasks regardless of the hardware type.

Hardware guest module interface
===============================
TBD
