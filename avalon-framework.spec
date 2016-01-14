%global pkg_name avalon-framework
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%global short_name    framework
%global short_Name    Avalon

Name:        %{?scl_prefix}%{pkg_name}
Version:     4.3
Release:     10.10%{?dist}
Epoch:       0
Summary:     Java components interfaces
License:     ASL 2.0
URL:         http://avalon.apache.org/%{short_name}/
Source0:     http://archive.apache.org/dist/excalibur/avalon-framework/source/%{pkg_name}-api-%{version}-src.tar.gz
Source1:     http://archive.apache.org/dist/excalibur/avalon-framework/source/%{pkg_name}-impl-%{version}-src.tar.gz

# pom files are not provided in tarballs so get them from external site
Source2:     http://repo1.maven.org/maven2/avalon-framework/%{pkg_name}-api/%{version}/%{pkg_name}-api-%{version}.pom
Source3:     http://repo1.maven.org/maven2/avalon-framework/%{pkg_name}-impl/%{version}/%{pkg_name}-impl-%{version}.pom

# remove jmock from dependencies because we don't have it
Patch0:     %{pkg_name}-impl-pom.patch
Patch1:     %{pkg_name}-xerces.patch

Requires:    %{?scl_prefix_java_common}apache-commons-logging
Requires:    %{?scl_prefix}avalon-logkit
Requires:    %{?scl_prefix_java_common}log4j
Requires:    %{?scl_prefix_java_common}xalan-j2

BuildRequires:    %{?scl_prefix_java_common}ant
BuildRequires:	  %{?scl_prefix_java_common}ant-junit
BuildRequires:	  %{?scl_prefix_java_common}apache-commons-logging
BuildRequires:    %{?scl_prefix}avalon-logkit
BuildRequires:    %{?scl_prefix_java_common}javapackages-tools
# For converting jar into OSGi bundle
BuildRequires:    %{?scl_prefix}aqute-bnd
BuildRequires:    %{?scl_prefix_java_common}junit
BuildRequires:	  %{?scl_prefix_java_common}log4j


BuildArch:    	  noarch


%description
The Avalon framework consists of interfaces that define relationships
between commonly used application components, best-of-practice pattern
enforcements, and several lightweight convenience implementations of the
generic components.
What that means is that we define the central interface Component. We
also define the relationship (contract) a component has with peers,
ancestors and children.

%package javadoc
Summary:      API documentation %{pkg_name}

%description javadoc
%{summary}.

%prep
%setup -q -n %{pkg_name}-api-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
tar xvf %{SOURCE1}

cp %{SOURCE2} .

pushd %{pkg_name}-impl-%{version}/
cp %{SOURCE3} .
%patch0
%patch1 -p2
popd
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
export CLASSPATH=$(build-classpath avalon-logkit junit commons-logging log4j)
export CLASSPATH="$CLASSPATH:../target/%{pkg_name}-api-%{version}.jar"
ant jar test javadoc
# Convert to OSGi bundle
java -jar $(build-classpath aqute-bnd) wrap target/%{pkg_name}-api-%{version}.jar

# build implementation now
pushd %{pkg_name}-impl-%{version}
# tests removed because we don't have jmock
rm -rf src/test/*
ant jar javadoc
# Convert to OSGi bundle
java -jar $(build-classpath aqute-bnd) wrap target/%{pkg_name}-impl-%{version}.jar
popd
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/
install -d -m 755 $RPM_BUILD_ROOT/%{_mavenpomdir}

install -m 644 target/%{pkg_name}-api-%{version}.bar $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}-api.jar
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}/%{pkg_name}-api

# pom file
install -pm 644 %{pkg_name}-api-%{version}.pom $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{pkg_name}-api.pom
%add_maven_depmap JPP-%{pkg_name}-api.pom %{pkg_name}-api.jar -a "org.apache.avalon.framework:%{pkg_name}-api"

# javadocs
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}/%{pkg_name}-api/


pushd %{pkg_name}-impl-%{version}
install -m 644 target/%{pkg_name}-impl-%{version}.bar $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}-impl.jar
ln -sf %{_javadir}/%{pkg_name}-impl.jar ${RPM_BUILD_ROOT}%{_javadir}/%{pkg_name}.jar

# pom file
install -pm 644 %{pkg_name}-impl-%{version}.pom $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{pkg_name}-impl.pom
%add_maven_depmap JPP-%{pkg_name}-impl.pom %{pkg_name}-impl.jar -a "org.apache.avalon.framework:%{pkg_name}-impl,%{pkg_name}:%{pkg_name}"

# javadocs
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}/%{pkg_name}-impl
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}/%{pkg_name}-impl/
popd
%{?scl:EOF}


%files -f .mfiles
%doc LICENSE.txt NOTICE.txt
%{_mavenpomdir}/JPP-%{pkg_name}-impl.pom
%{_javadir}/%{pkg_name}-impl.jar
%{_javadir}/%{pkg_name}.jar

%files javadoc
%doc LICENSE.txt NOTICE.txt
%{_javadocdir}/%{name}

%changelog
* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 0:4.3-10.10
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michal Srb <msrb@redhat.com> - 4.3-10.9
- Fix BR/R

* Wed Jan 07 2015 Michal Srb <msrb@redhat.com> - 4.3-10.8
- Migrate to .mfiles

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 0:4.3-10.7
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.6
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.5
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.4
- Mass rebuild 2014-02-18

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.3
- SCL-ize requires and build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-10.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 04.3-10
- Mass rebuild 2013-12-27

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:4.3-9
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 06 2012 Tomas Radej <tradej@redhat.com> - 0:4.3-6
- Fixed xerces dep

* Fri Apr 6 2012 Alexander Kurtakov <akurtako@redhat.com> 0:4.3-5
- Remove unneeded BR/R.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Oct 18 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:4.3-3
- aqute-bndlib renamed to aqute-bnd (#745163)
- Use new maven macros
- Packaging tweaks

* Tue May 3 2011 Severin Gehwolf <sgehwolf@redhat.com> 0:4.3-3
- Convert jar's to OSGi bundles using aqute-bndlib.

* Tue May  3 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:4.3-2
- Add compatibility depmap for org.apache.avalon.framework groupId

* Wed Apr 20 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:4.3-1
- Latest version
- Split into two jars, provide backward compatible symlink
- Cleanups according to new guidelines

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.1.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Dec 29 2010 Alexander Kurtakov <akurtako@redhat.com> 0:4.1.4-7
- Drop gcj.
- Use global.
- No versioned jars.
- Fix permissions.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.1.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:4.1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:4.1.4-4
- drop repotag
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:4.1.4-3jpp.14
- Autorebuild for GCC 4.3

* Thu Mar 08 2007 Permaine Cheung <pcheung at redhat.com> - 0:4.1.4-2jpp.14
- rpmlint cleanup.

* Thu Aug 10 2006 Matt Wringe <mwringe at redhat.com> - 0:4.1.4-2jpp.13
- Add missing javadoc requires

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:4.1.4-2jpp_12fc
- Rebuilt

* Wed Jul 19 2006 Matt Wringe <mwringe at redhat.com> - 0:4.1.4-2jpp_11fc
- Removed separate definition of name, version and release.

* Wed Jul 19 2006 Matt Wringe <mwringe at redhat.com> - 0:4.1.4-2jpp_10fc
- Added conditional native compling.

* Thu Jun  8 2006 Deepak Bhole <dbhole@redhat.com> - 0:4.1.4-2jpp_9fc
- Updated description for fix to Bug# 170999

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:4.1.4-2jpp_8fc
- stop scriptlet spew

* Wed Dec 21 2005 Gary Benson <gbenson@redhat.com> 0:4.1.4-2jpp_7fc
- Rebuild again

* Thu Dec 15 2005 Gary Benson <gbenson@redhat.com> 0:4.1.4-2jpp_6fc
- Rebuild for new gcj.

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> 0:4.1.4-2jpp_5fc
- Build into Fedora.

* Thu Oct 28 2004 Gary Benson <gbenson@redhat.com> 0:4.1.4-2jpp_4fc
- Bootstrap into Fedora.

* Thu Sep 30 2004 Andrew Overholt <overholt@redhat.com> 0:4.1.4-2jpp_3rh
- Remove avalon-logkit as a Requires

* Mon Mar  8 2004 Frank Ch. Eigler <fche@redhat.com> 0:4.1.4-2jpp_2rh
- RH vacuuming part II

* Fri Mar  5 2004 Frank Ch. Eigler <fche@redhat.com> 0:4.1.4-2jpp_1rh
- RH vacuuming

* Fri May 09 2003 David Walluck <david@anti-microsoft.org> 0:4.1.4-2jpp
- update for JPackage 1.5

* Fri Mar 21 2003 Nicolas Mailhot <Nicolas.Mailhot (at) JPackage.org> 4.1.4-1jpp
- For jpackage-utils 1.5
- Forrest is not used right now

* Tue May 07 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.1.2-3jpp
- hardcoded distribution and vendor tag
- group tag again

* Thu May 2 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.1.2-2jpp
- distribution tag
- group tag

* Sun Feb 03 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.1.2-1jpp
- 4.1.2
- section macro

* Thu Jan 17 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.1-2jpp
- versioned dir for javadoc
- no dependencies for manual and javadoc packages
- requires xml-commons-apis

* Wed Dec 12 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.1-1jpp
- 4.1
- Requires and BuildRequires xalan-j2

* Wed Dec 5 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.0-4jpp
- javadoc into javadoc package

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 4.0-3jpp
- changed extension --> jpp

* Sat Oct 6 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.0-2jpp
- first unified release
- used original tarball

* Thu Sep 13 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.0-1mdk
- first Mandrake release
