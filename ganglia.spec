%define lib_name_orig lib%{name}
%define lib_major 1
%define lib_name %mklibname %name %{lib_major}
%define script_version 0.3

Name:		ganglia
License:	BSD
Version:	3.2.0
Release:	3
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

%install
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/ganglia
%{__mkdir} -p %{buildroot}%{_oldincludedir}/ganglia
%{__mkdir} -p %{buildroot}%{_mandir}/man1
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d/
%{__mkdir} -p %{buildroot}/var/lib/ganglia/rrds
%{__mkdir} -p %{buildroot}/var/www/html

%makeinstall_std

#Disabling setuid
echo "setuid off" >> %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf

find  %{_builddir}/%{name}-%{version}/ -name "CVS" | xargs rm -rf

#cp -f %{_builddir}/%{name}-core-%{version}/lib/ganglia/* %{buildroot}/%{_oldincludedir}/ganglia/
cp -f %{_builddir}/%{name}-%{version}/mans/* %{buildroot}%{_mandir}/man1/
#%__cp -f %{_builddir}/%{name}-%{version}/gmetad/gmetad.conf %{buildroot}/%{_sysconfdir}/ganglia/gmetad.conf
%__cp -f %{SOURCE8} %{buildroot}/%{_initrddir}/gmetad
cp -avf %{_builddir}/%{name}-%{version}/web %{buildroot}/var/www/html/ganglia

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



%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 3.2.0-2mdv2012.0
+ Revision: 772976
- relink against libpcre.so.1

* Wed Jan 25 2012 Antoine Ginies <aginies@mandriva.com> 3.2.0-1
+ Revision: 768208
- fix %%multiarch_binaries
  add missing man5 page
- fix BR on freetype
- update ganglia tarball
- drop ganglia-3.1.2-fix-format-errors.patch (merge upstream)
  upgrade to release 3.2.0

* Thu Dec 02 2010 Paulo Andrade <pcpa@mandriva.com.br> 3.1.7-4mdv2011.0
+ Revision: 605290
- Rebuild with apr with workaround to issue with gcc type based

* Mon Oct 18 2010 Funda Wang <fwang@mandriva.org> 3.1.7-3mdv2011.0
+ Revision: 586587
- fix pacakge file list

* Mon Apr 26 2010 Antoine Ginies <aginies@mandriva.com> 3.1.7-2mdv2010.1
+ Revision: 539043
- fix bump release, fix gmond script (bad path to gmond.conf file)
- fix path to gmond.conf file
- version 3.1.7, fix summary, move ganglia conf in /etc/, now gmetad is launched as nobody user (fix some perms)

* Tue Dec 15 2009 Antoine Ginies <aginies@mandriva.com> 3.1.2-4mdv2010.1
+ Revision: 478979
- bump to release 4

* Tue Dec 15 2009 Antoine Ginies <aginies@mandriva.com> 3.1.2-2mdv2010.1
+ Revision: 478816
- fix ganglia hang, (#56428 thx J.A. Magallon)

* Tue Jun 23 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.2-1mdv2010.0
+ Revision: 388671
- new version
- rediff format patch

* Sun Jan 04 2009 Jérôme Soyer <saispo@mandriva.org> 3.1.1-1mdv2009.1
+ Revision: 324719
- New upstream release

* Sat Sep 20 2008 Oden Eriksson <oeriksson@mandriva.com> 3.1.0-2mdv2009.0
+ Revision: 286183
- fix deps

  + Antoine Ginies <aginies@mandriva.com>
    - fix initscript and path to configurations files
    - fix path to so lib
    - new gmetad initscript, new release 3.1.0
    - fix initscript

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - fix no-buildroot-tag

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Feb 12 2008 Antoine Ginies <aginies@mandriva.com> 3.0.6-1mdv2008.1
+ Revision: 165772
- new source
- new release

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Wed Jan 17 2007 Erwan Velu <erwan@mandriva.org> 3.0.4-1mdv2007.0
+ Revision: 109923
- 3.0.4
  Removing unecessary patch0 & patch1
- Import ganglia

* Wed Aug 09 2006 Antoine Ginies <aginies@mandriva.com> 3.0.3-1mdv2007.0
- 3.0.3 release

* Thu Jul 06 2006 Thierry Vignaud <tvignaud@mandriva.com> 3.0.2-2mdv2007.0
- fix group

* Mon Apr 24 2006 Nicolas L�cureuil <neoclust@mandriva.org> 3.0.2-2mdk
- Add BuildRequires
- Fix PreReq

* Thu Nov 17 2005 Antoine Ginies <aginies@n2.mandriva.com> 3.0.2-1mdk
- 3.0.2 release

* Wed Mar 30 2005 Antoine Ginies <aginies@n1.mandrakesoft.com> 3.0.1-1mdk
- serious bugs fixed in 3.0.1 release: 
    gmond Unicast Communication Bug Fixed
    gmond.conf Conversion Bug Fixed
    Network Metrics Bug Fixed for Linux 2.6.x Kernels
- use noarch (ganglia-webfrontend)

* Fri Mar 25 2005 Eskild Hustvedt <eskild@mandrake.org> 3.0.0-5mdk
- Fixed group of ganglia-webfrontend
- %%mkrel

* Tue Mar 22 2005 Antoine Ginies <aginies@n1.mandrakesoft.com> 3.0.0-4mdk
- fix service for ganglia-script

* Sat Mar 19 2005 Antoine Ginies <aginies@n1.mandrakesoft.com> 3.0.0-3mdk
- use gmond -t to create a default configuration file

* Sat Mar 19 2005 Antoine Ginies <aginies@mandrakesoft.com> 3.0.0-2mdk
- fix requires and use Ganglia 3.0.0 web pages (thx J.A. Magallon report)
- add gmond.conf.html in ganglia-core package

* Thu Mar 17 2005 Antoine Ginies <aginies@mandrakesoft.com> 3.0.0 -1mdk
- new release 3.0.0
- use

* Fri Oct 29 2004 Erwan Velu <erwan@mandrakesoft.com> 2.5.7-1mdk
- 2.5.7

* Fri Jun 18 2004 Erwan Velu <erwan@mandrakesoft.com> 2.5.6-2mdk
- Fixing segfault when gmond is not started

* Tue Apr 06 2004 Erwan Velu <erwan@mandrakesoft.com> 2.5.6-1mdk
- New release
- Remove patch0

* Thu Feb 26 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 2.5.4-2mdk
- Fix DIRM (distlint)
- %%mklibname
- patch2: fix DESTDIR
- cleanup, cleanup, cleanup... /me slaps Erwan and Aginies :)
 Tue Aug 19 2003 Erwan Velu <erwan@mandrakesoft.com> 2.5.4-1mdk
- 2.5.4

