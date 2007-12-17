%define name	ganglia
%define version 3.0.4
%define release %mkrel 1
%define lib_name_orig lib%{name}
%define lib_major 1
%define lib_name %mklibname %name %{lib_major}
%define script_version 0.3 

Name:         	%{name}
License:      	BSD
Version:        %{version}
Release:        %{release}
Group:        	Monitoring
Summary: 	Ganglia Cluster Toolkit
Url:		http://ganglia.sourceforge.net
Source:		%{name}-%{version}.tar.bz2
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Source1:	gmond.conf
Source2:	%{name}-monitor-script-%{script_version}.tar.bz2
Source3:	%{name}-monitor-script.d
Source4:	ganglia-script
Source5:	README.script
Source6:	ganglia-monitor-logrotate.d
Source7: 	gmond-init-add-route
BuildRequires:	librrdtool-devel
BuildRequires:  freetype2-static-devel

%description
Ganglia is a scalable, real-time cluster monitoring and execution environment 
with all execution requests and cluster statistics expressed in an open 
well-defined XML format.

%package 	core
Group:		Monitoring 
Summary:	Ganglia Cluster Core
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	core
The core package of Ganglia Monitor.

%package	gmetad
Group:		Monitoring
Summary: 	Ganglia Meta daemon
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	%name-core = %{version}-%{release}

%description gmetad
Ganglia is a scalable, real-time monitoring and execution environment
with all execution requests and statistics expressed in an open
well-defined XML format.

This gmetad daemon can aggregate monitoring data from several clusters
to form a monitoring grid. It also keeps metric history using the RRD tool.

%package 	-n %{lib_name}-devel
Group:		Development/Other 
Summary:	Ganglia Cluster Toolkit Library
Provides:	libganglia-devel = %{version}-%{release}
Provides:	%name-devel = %{version}-%{release}
Requires:	lib%name-devel = %{version}-%{release}
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	-n %{lib_name}-devel
The Ganglia Monitoring Core library provides a set of 
functions that programmers can use to build scalable 
cluster or grid applications.

%package 	-n %{lib_name}
Group:		Development/Other 
Summary:	Ganglia Cluster Toolkit Library
Provides:	lib%name = %{version}-%{release}
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	-n %{lib_name}
The Ganglia Monitoring Core library provides a set of 
functions that programmers can use to build scalable 
cluster or grid applications.

%package	script
Group:		Monitoring
Summary:	Ganglia Cluster Script
Provides:	%{name}-script
Requires:	%{name}-core
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	script
Ganglia Monitor Script is an extrension for Ganglia Monitor.
It's a easy way to add value to monitor for your
Ganglia Monitor.

%package        webfrontend
Group:          Monitoring
Summary:        Ganglia Web Frontend
Provides:       %{name}-webfrontend
Requires:       %{name}-core, mod_php, rrdtool >= 1.0.37, %name-gmetad >= 3.0.0, php-xml, php-gd
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description webfrontend
This component presents all the historical data saved
to Round-Robin databases by Gmetad in HTML allowing all
cluster, hosts and host metrics to be viewed in real-time.


%prep
%setup -q -T -n %{name}-monitor-script-%{script_version} -b 2
%setup -q -T -n %{name}-%{version} -b 0

%build
#rm -rf %{buildroot}
#./configure --prefix=%{buildroot}/usr --libdir=%{buildroot}%{_libdir} --with-gmetad
#make

%configure --with-gmetad --enable-debug
%make

#core
%post core
%_post_service gmond

%preun core
%_preun_service gmond

#script
%post script 
%_post_service ganglia-script

%preun script
%_preun_service ganglia-script 

%post gmetad
%_post_service gmetad

%preun gmetad
%_preun_service gmetad 

%post -p /sbin/ldconfig -n %{lib_name} 

%post -p /sbin/ldconfig -n %{lib_name}-devel 

%postun -p /sbin/ldconfig -n %{lib_name} 

%postun -p /sbin/ldconfig -n %{lib_name}-devel 

%install 
rm -fr %buildroot
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_oldincludedir}/ganglia
%{__mkdir} -p %{buildroot}%{_mandir}/man1
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d/
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/ganglia/rrds
%{__mkdir} -p $RPM_BUILD_ROOT/var/www/html

%makeinstall_std 

#Disabling setuid
echo "setuid off" >> %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf

find  $RPM_BUILD_DIR/%{name}-%{version}/ -name "CVS" | xargs rm -rf

#cp -f %{_builddir}/%{name}-core-%{version}/lib/ganglia/* %{buildroot}/%{_oldincludedir}/ganglia/
cp -f %{_builddir}/%{name}-%{version}/mans/* %{buildroot}%{_mandir}/man1/
%__cp -f %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf $RPM_BUILD_ROOT/etc/gmetad.conf
%__cp -f %{_builddir}/%{name}-%{version}/gmetad/gmetad.init $RPM_BUILD_ROOT/etc/rc.d/init.d/gmetad
cp -avf %{_builddir}/%{name}-%{version}/web $RPM_BUILD_ROOT/var/www/html/ganglia

# Patching libdir in libganglia.la : removing buildroot path
# perl -pi -e 's|%buildroot||g' "%{buildroot}%{_exec_prefix}/%{_lib}/libganglia.la"

#install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/gmond.conf

#script
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_bindir}
%{__mkdir} -p %{buildroot}%{_datadir}/%{name}-script/script/
%{__mkdir} -p %{buildroot}%{_defaultdocdir}/%{name}-script-%{version}/
install %{SOURCE3} %{buildroot}%{_initrddir}/%{name}-script
install %{SOURCE4} %{buildroot}%{_bindir}
install %{_builddir}/%{name}-monitor-script-%{script_version}/* %{buildroot}%{_datadir}/%{name}-script/script/
install %{SOURCE5} %{buildroot}%{_defaultdocdir}/%{name}-script-%{version}/README
install %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/ganglia-monitor-core
install %{SOURCE7} %{buildroot}/%{_initrddir}/gmond
rm -rf  %{buildroot}%{_includedir}/*.h

%{_builddir}/%{name}-%{version}/gmond/gmond -t > %{buildroot}%{_sysconfdir}/gmond.conf
perl -pi -e 's|name = "unspecified".*|name = "Cluster"|' %{buildroot}%{_sysconfdir}/gmond.conf

%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/ganglia-config

%files gmetad
%defattr(-,root,root)
%attr(0777,root,root)/var/lib/ganglia/rrds
%{_sbindir}/gmetad
%config(noreplace) %{_initrddir}/gmetad
%config(noreplace) /etc/gmetad.conf

%files core 
%defattr(-,root,root)
%doc README AUTHORS ChangeLog COPYING INSTALL gmond/gmond.conf.html
%{_bindir}/gmetric
%{_bindir}/gstat
%multiarch %{multiarch_bindir}/ganglia-config
%{_bindir}/ganglia-config
%{_sbindir}/gmond
%config(noreplace) %{_initrddir}/gmond
%config(noreplace) %{_sysconfdir}/gmond.conf
%{_mandir}/man1/*
%attr(644,root,root)%config(noreplace) %{_sysconfdir}/logrotate.d/ganglia-monitor-core


%files -n %{lib_name}
%defattr(-,root,root)
%doc README AUTHORS ChangeLog COPYING INSTALL
%{_libdir}/lib%{name}*

%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc README AUTHORS ChangeLog COPYING INSTALL
%{_includedir}/*
#%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a

%files script
%defattr(-,root,root)
%config(noreplace) %attr(744,root,root)%{_initrddir}/%{name}-script
%{_bindir}/ganglia-script
%{_datadir}/%{name}-script
%doc %{_defaultdocdir}/%{name}-script-%{version}/README

%files webfrontend
%defattr(-,root,root)
/var/www/html/ganglia/*

%clean
rm -rf %{buildroot}


