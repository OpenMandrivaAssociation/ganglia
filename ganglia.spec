%define api 3.2.0.0
%define major 0
%define libname %mklibname %{name} %{api} %{major}
%define devname %mklibname %{name} -d

%define script_version 0.3

Summary:	Cluster Toolkit
Name:		ganglia
Version:	3.2.0
Release:	6
License:	BSD
Group:		Monitoring
Url:		https://ganglia.sourceforge.net
Source0:	http://downloads.sourceforge.net/ganglia/%{name}-%{version}.tar.gz
Source2:	%{name}-monitor-script-%{script_version}.tar.bz2
Source3:	%{name}-monitor-script.service
Source4:	ganglia-script
Source5:	README.script
Source6:	ganglia-monitor-logrotate.d
Source7:	gmond.service
Source8:	gmetad.service
Buildrequires:	apr-devel
Buildrequires:	gettext-devel
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(libconfuse)
BuildRequires:	pkgconfig(librrd)
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(python)

%description
Ganglia is a scalable, real-time cluster monitoring and execution environment
with all execution requests and cluster statistics expressed in an open
well-defined XML format.

#----------------------------------------------------------------------------

%package core
Summary:	Cluster Core
Group:		Monitoring
Conflicts:	%{_lib}ganglia1 < 3.2.0-4
Requires(post,preun):	rpm-helper

%description core
The core package of Ganglia Monitor.

%files core
%doc AUTHORS COPYING INSTALL gmond/gmond.conf.html BUGS NEWS
%{_bindir}/gmetric
%{_bindir}/gstat
%{_bindir}/ganglia-config
%{_sbindir}/gmond
%{_libdir}/ganglia/*.so
%config(noreplace) %{_unitdir}/gmond.service
%config(noreplace) %{_sysconfdir}/gmond.conf
%{_mandir}/man1/*
%{_mandir}/man5/*
%attr(644,root,root)%config(noreplace) %{_sysconfdir}/logrotate.d/ganglia-monitor-core

%post core
%systemd_post gmond.service

%preun core
%systemd_preun gmond.service

%postun core
%systemd_postun_with_restart gmond.service

#----------------------------------------------------------------------------

%package gmetad
Summary:	Meta daemon
Group:		Monitoring
Requires:	%{name}-core
Requires(post,preun):	rpm-helper

%description gmetad
Ganglia is a scalable, real-time monitoring and execution environment with all
execution requests and statistics expressed in an open well-defined XML format.

This gmetad daemon can aggregate monitoring data from several clusters
to form a monitoring grid. It also keeps metric history using the RRD tool.

%files gmetad
%attr(0777,nobody,nobody)/var/lib/ganglia/rrds
%{_sbindir}/gmetad
%config(noreplace) %{_unitdir}/gmetad.service
%config(noreplace) %{_sysconfdir}/conf.d/modpython.conf
%config(noreplace) %{_sysconfdir}/gmetad.conf

%post gmetad
%systemd_post gmetad.service
if [ -d "var/lib/ganglia/rrds" ]; then
	echo "gmetad is launched as nobody users now, changing /var/lib/ganglia/rrds permissions to nobody.nobody"
	chown -R nobody.nobody /var/lib/ganglia/rrds
fi

%preun gmetad
%systemd_preun gmetad.service

%postun gmetad
%systemd_postun_with_restart gmetad.service

#----------------------------------------------------------------------------

%package script
Summary:	Cluster Script
Group:		Monitoring
Requires:	%{name}-core
Requires(post,preun):	rpm-helper

%description script
Ganglia Monitor Script is an extrension for Ganglia Monitor. It's a easy way
to add value to monitor for your Ganglia Monitor.

%files script
%config(noreplace) %attr(744,root,root) %{_unitdir}/%{name}-script.service
%{_bindir}/ganglia-script
%{_datadir}/%{name}-script
%doc %{_defaultdocdir}/%{name}-script-%{version}/README

%post script
%systemd_post ganglia-script.service

%preun script
%systemd_preun ganglia-script.service

%postun script
%systemd_postun_with_restart ganglia-script.service

#----------------------------------------------------------------------------

%package webfrontend
Summary:	Ganglia Web Frontend
Group:		Monitoring
Requires:	%{name}-core
Requires:	%{name}-gmetad
Requires:	mod_php
Requires:	php-xml
Requires:	php-gd
Requires:	rrdtool

%description webfrontend
This component presents all the historical data saved to Round-Robin databases
by Gmetad in HTML allowing all cluster, hosts and host metrics to be viewed in
real-time.

%files webfrontend
%{_var}/www/html/ganglia/*

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Cluster Toolkit Library
Group:		Development/Other
Conflicts:	%{_lib}ganglia1 < 3.2.0-4
Obsoletes:	%{_lib}ganglia1 < 3.2.0-4

%description -n %{libname}
The Ganglia Monitoring Core library provides a set of functions that
programmers can use to build scalable cluster or grid applications.

%files -n %{libname}
%doc AUTHORS COPYING INSTALL
%{_libdir}/libganglia-%{api}.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Cluster Toolkit Library
Group:		Development/Other
Provides:	libganglia-devel = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Conflicts:	%{_lib}ganglia1-devel < 3.2.0-4
Obsoletes:	%{_lib}ganglia1-devel < 3.2.0-4

%description -n %{devname}
The Ganglia Monitoring Core library provides a set of functions that
programmers can use to build scalable cluster or grid applications.

%files -n %{devname}
%doc AUTHORS COPYING INSTALL
%{_includedir}/*
%{_libdir}/libganglia.so

#----------------------------------------------------------------------------

%prep
%setup -q -T -n %{name}-monitor-script-%{script_version} -b 2
%setup -q -T -n %{name}-%{version} -b 0

%build
%configure2_5x \
	--with-gmetad \
	--enable-status \
	--disable-static
%make GLDADD="-ltirpc"

%install
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/ganglia
mkdir -p %{buildroot}%{_oldincludedir}/ganglia
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
mkdir -p %{buildroot}/var/lib/ganglia/rrds
mkdir -p %{buildroot}/var/www/html

%makeinstall_std

#Disabling setuid
echo "setuid off" >> %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf

find  %{_builddir}/%{name}-%{version}/ -name "CVS" | xargs rm -rf

cp -f %{_builddir}/%{name}-%{version}/mans/* %{buildroot}%{_mandir}/man1/
install -D -m 644 %{SOURCE8} %{buildroot}%{_unitdir}/gmetad.service
cp -avf %{_builddir}/%{name}-%{version}/web %{buildroot}/var/www/html/ganglia

#script
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}-script/script/
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-script-%{version}/
install -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-script.service
install %{SOURCE4} %{buildroot}%{_bindir}
install %{_builddir}/%{name}-monitor-script-%{script_version}/* %{buildroot}%{_datadir}/%{name}-script/script/
install %{SOURCE5} %{buildroot}%{_defaultdocdir}/%{name}-script-%{version}/README
install %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/ganglia-monitor-core
install -D -m 644 %{SOURCE7} %{buildroot}%{_unitdir}/gmond.service
rm -rf  %{buildroot}%{_includedir}/*.h

%{_builddir}/%{name}-%{version}/gmond/gmond -t > %{buildroot}%{_sysconfdir}/gmond.conf
perl -pi -e 's|name = "unspecified".*|name = "Cluster"|' %{buildroot}%{_sysconfdir}/gmond.conf

