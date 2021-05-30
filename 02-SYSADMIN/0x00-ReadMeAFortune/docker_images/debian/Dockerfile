FROM baseimage-debian-sysadmin:1.0

# Create user groups
RUN groupadd -g 6666 team

# Create users
RUN useradd -m -d /home/team -s /bin/bash -g 6666 -G team -u 6666 team -p $(python3 -c 'import crypt; print(crypt.crypt("team", crypt.mksalt(crypt.METHOD_SHA512)))')

# Allow SSH access to users
RUN echo "AllowUsers team" >> /etc/ssh/sshd_config

# Set working directory
WORKDIR /home/team

# Copy necessary files
COPY flag.txt /tmp/
COPY actualflag.txt /usr/games/actualflag.txt

# Change host perms
RUN chown -R "root:team" /home/team/ && \
    chown -R "root:root" /var/tmp/ && \
    chmod -R 750 /home/team/ && \
    chmod -R 750 /var/tmp/

# Give them appropriate permissions, ownership, group membership
RUN chown "root:team" /tmp/flag.txt && \
    chmod 640 /tmp/flag.txt && \
    chown "root:team" /usr/games/actualflag.txt && \
    chmod 440 /usr/games/actualflag.txt

# Edit .profile
RUN echo "alias cd='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias ls='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias more='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias less='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias vi='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias vim='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias nano='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias pico='fortune | cowsay'" >> /home/team/.profile && \
    echo "alias cat='fortune | cowsay'" >> /home/team/.profile

# Edit .bashrc
RUN echo "alias cd='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias ls='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias more='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias less='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias vi='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias vim='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias nano='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias pico='fortune | cowsay'" >> /home/team/.bashrc && \
    echo "alias cat='fortune | cowsay'" >> /home/team/.bashrc


