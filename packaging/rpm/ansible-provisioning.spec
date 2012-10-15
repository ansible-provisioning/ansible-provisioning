%if 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name: ansible-provisioning
Release: 1%{?dist}
Summary: SSH-based configuration management, deployment, and task execution system
Version: 0.8
License: GPLv3
Group: Development/Libraries
URL: http://ansible.cc/

Source0: https://github.com/downloads/ansible/ansible-provisioning/ansible-provisioning-%{version}.tar.gz
BuildRoot: %{_tmppath}/root-%{name}-%{version}-%{release}

BuildArch: noarch
BuildRequires: python2-devel
Requires: ansible

%description
Ansible is a radically simple model-driven configuration management,
multi-node deployment, and remote task execution system. Ansible works
over SSH and does not require any software or daemons to be installed
on remote nodes. Extension modules can be written in any language and
are transferred to managed machines automatically.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --root="%{buildroot}"
%{__install} -d -m0755 %{buildroot}%{_mandir}/man3/
%{__cp} -av docs/man/man3/*.3 %{buildroot}%{_mandir}/man3/
%{__install} -d -m0755 %{buildroot}%{_datadir}/ansible/
%{__cp} -av library/* %{buildroot}%{_datadir}/ansible/

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc COPYING PKG-INFO README.md
%doc %{_mandir}/man3/ansible.*
%{python_sitelib}/ansible*
%{_datadir}/ansible/

%changelog
* Mon Oct 15 2012 Dag Wieers <dag@wieers.com> - 0.8-0
- Initial package.
