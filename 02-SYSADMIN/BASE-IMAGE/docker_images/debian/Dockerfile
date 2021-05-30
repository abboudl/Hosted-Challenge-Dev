FROM debian:buster

# Update & Upgrade
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y man-db manpages manpages-dev 

# Install Daemons and Services
RUN apt-get install -y openssh-server rsyslog supervisor \ 
    && apt-get install -y nano vim less build-essential bsdmainutils sysstat cowsay fortune \
    && apt-get install -y ltrace strace xxd gdb binutils \
    && apt-get install -y python3-pip libssl-dev libffi-dev python3-dev

# Install needed pip modules for all challenges
RUN apt-get install -y python3-pip && pip3 install keyring && pip3 install keyrings.cryptfile

# Remove Unneeded Software 
RUN dpkg --remove --force-depends \
 openssh-client openssh-sftp-server; \
 apt-get autoremove; \
 exit 0

# Remove executable bit from pip
RUN rm -rf /usr/bin/pip3 /usr/bin/crontab /usr/bin/apt /usr/bin/apt-get /usr/lib/apt 

# Remove Ability to Install Software
RUN rm -r /etc/apt/sources.list*

# Rsyslog Settings: Make Syslog Files World-Readable
RUN sed -i 's/\$FileCreateMode 0640/$FileCreateMode 0644/' /etc/rsyslog.conf

# SSH Setting
RUN mkdir /var/run/sshd \ 
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/#MaxSessions 10/MaxSessions 100/' /etc/ssh/sshd_config \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# Set a Cron Job to Clear History Files of All Users Every 15 Mins
RUN echo '*/10 * * * *   root    for f in /home/*/.bash_history; do cat /dev/null > "$f"; done' >> /etc/crontab


# Cleaning Loose Ends
RUN rm -rf \
  /tmp/* \
  /var/lib/apt/lists/* \
  /var/tmp/*

# Launch Supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]

