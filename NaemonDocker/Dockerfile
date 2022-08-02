FROM centos:7

LABEL maintainer="LE LUYER Anthony <anthony.leluyer@gmail.com>"
LABEL description="This Dockerfile installs Naemon and set it up"

RUN curl -s https://download.opensuse.org/repositories/home:/naemon/CentOS_7/home:naemon.repo >> /etc/yum.repos.d/naemon-stable.repo && \
    yum -y install epel-release && \
    yum -y install naemon nagios-plugins nagios-plugins-all nagios-plugins-nrpe nrpe

ADD ./scripts/* /usr/local/bin/
ADD ./naemon.cfg /etc/naemon/