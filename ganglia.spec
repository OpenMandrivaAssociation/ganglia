%define lib_name_orig lib%{name}
%define lib_major 1
%define lib_name %mklibname %name %{lib_major}
%define script_version 0.3

Name:		ganglia
License:	BSD
Version:	3.2.0
Release:	%mkrel 1
Group:		Monitoring
Summary:	Cluster Toolkit
URL:		http://ganglia.sourceforge.net
Source:		http://downloads.sourceforge.net/ganglia/%{name}-%{version}.tar.gz
Requires(post):	rpm-helper
Requires(preun): rpm-helper
#Source1:	gmond.conf
Source2:	%{name}-monitor-script-%{script_version}.tar.bz2
Source3:	%{name}-monitor-script.d
Source4:	ganglia-script
Source5:	README.script
Source6:	ganglia-monitor-logrotate.d
Source7:	gmond-init-add-route
Source8:	gmetad.init
Buildrequires:	apr-devel
BuildRequires:	confuse-devel
BuildRequires:	expat-devel
BuildRequires:	%mklibname freetype6-devel
Buildrequires:	gettext-devel
BuildRequires:	python-devel
BuildRequires:	rrdtool-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Ganglia is a scalable, real-time cluster monitoring and execution environment
with all execution requests and cluster statistics expressed in an open
well-defined XML format.

%package 	core
Group:		Monitoring
Summary:	Cluster Core
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	core
The core package of Ganglia Monitor.

%package	gmetad
Group:		Monitoring
Summary:	Meta daemon
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
Summary:	Cluster Toolkit Library
Provides:	libganglia-devel = %{version}-%{release}
Provides:	%name-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}-%{release}
Conflicts:	%{lib_name} < 3.1.7-3
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	-n %{lib_name}-devel
The Ganglia Monitoring Core library provides a set of
functions that programmers can use to build scalable
cluster or grid applications.

%package 	-n %{lib_name}
Group:		Development/Other
Summary:	Cluster Toolkit Library
Provides:	lib%name = %{version}-%{release}
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	-n %{lib_name}
The Ganglia Monitoring Core library provides a set of
functions that programmers can use to build scalable
cluster or grid applications.

%package	script
Group:		Monitoring
Summary:	Cluster Script
Provides:	%{name}-script = %{version}-%{release}
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
Provides:       %{name}-webfrontend = %{version}-%{release}
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
rm -rf %{buildroot}

%configure2_5x --with-gmetad --enable-status
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
if [ -d "var/lib/ganglia/rrds" ]; then 
	echo "gmetad is launched as nobody users now, changing /var/lib/ganglia/rrds permissions to nobody.nobody"
	chown -R nobody.nobody /var/lib/ganglia/rrds
fi

%preun gmetad
%_preun_service gmetad

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{lib_name}
%endif

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{lib_name}-devel
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{lib_name}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{lib_name}-devel
%endif

%install
rm -fr %buildroot
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ganglia
%{__mkdir} -p %{buildroot}%{_oldincludedir}/ganglia
%{__mkdir} -p %{buildroot}%{_mandir}/man1
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d/
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/ganglia/rrds
%{__mkdir} -p $RPM_BUILD_ROOT/var/www/html

%makeinstall_std

#Disabling setuid
echo "setuid off" >> %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf

find  %{_builddir}/%{name}-%{version}/ -name "CVS" | xargs rm -rf

#cp -f %{_builddir}/%{name}-core-%{version}/lib/ganglia/* %{buildroot}/%{_oldincludedir}/ganglia/
cp -f %{_builddir}/%{name}-%{version}/mans/* %{buildroot}%{_mandir}/man1/
#%__cp -f %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf $RPM_BUILD_ROOT/%{_sysconfdir}/ganglia/gmetad.conf
%__cp -f %{SOURCE8} %{buildroot}/%{_initrddir}/gmetad
cp -avf %{_builddir}/%{name}-%{version}/web $RPM_BUILD_ROOT/var/www/html/ganglia

# Patching libdir in libganglia.la : removing buildroot path
# perl -pi -e 's|%buildroot||g' "%{buildroot}%{_exec_prefix}/%{_lib}/libganglia.la"

#install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/gmond.conf

#script
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

%if %mdkversion < 201010
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/ganglia-config
%endif

%files gmetad
%defattr(-,root,root)
%attr(0777,nobody,nobody)/var/lib/ganglia/rrds
%{_sbindir}/gmetad
%config(noreplace) %{_initrddir}/gmetad
%config(noreplace) %{_sysconfdir}/conf.d/modpython.conf
%config(noreplace) %{_sysconfdir}/gmetad.conf

%files core
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL gmond/gmond.conf.html BUGS NEWS
%{_bindir}/gmetric
%{_bindir}/gstat
%if %mdkversion < 201010
%multiarch %{multiarch_bindir}/ganglia-config
%elsif
%{_bindir}/ganglia-config
%endif
%{_bindir}/ganglia-config
%{_sbindir}/gmond
%config(noreplace) %{_initrddir}/gmond
%config(noreplace) %{_sysconfdir}/gmond.conf
%{_mandir}/man1/*
%{_mandir}/man5/*
%attr(644,root,root)%config(noreplace) %{_sysconfdir}/logrotate.d/ganglia-monitor-core


%files -n %{lib_name}
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL
%{_libdir}/libganglia-%{version}.0.so.*
%{_libdir}/ganglia/*.so

%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL
%{_includedir}/*
%{_libdir}/libganglia.so
%{_libdir}/libganglia.la
%{_libdir}/libganglia.a

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


