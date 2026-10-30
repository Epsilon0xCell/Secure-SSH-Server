#!/bin/bash

# I treat this script as one half of a pair. The setup below creates a
# user and replaces the live sshd_config, and cleanup near the bottom
# is supposed to undo both. If I change one side I have to check the
# other, because a setup step with no cleanup step leaves the machine
# changed after I said the server was temporary.

# Generate a random password
# I make the password before the prompts so the value exists by the
# time user creation needs it. It comes from 12 bytes from openssl,
# base64 encoded, so what gets printed later is longer than 12
# characters. I store it in no file. The printout at the end is the
# only copy, and closing the terminal before connecting loses it.
# Nothing here checks that openssl succeeded.
password=$(openssl rand -base64 12)

# Prompt for server port and username
# we use a different port default to mitigate attack surface.
read -p "Enter the server port (default: 25): " port
port=${port:-25}
read -p "Enter the username for SSH access: " username
# Port 25 is the default if I just press enter. That port is well
# known and normally belongs to mail, so on a machine that already
# runs a mail server this default can collide instead of working.

# Validate the port and username before either is used in a command or
# written into the SSH server configuration
# I do this check before sudo, pacman, or any file write. Once the
# port reaches the heredoc below it becomes a line in sshd_config,
# and once the username reaches useradd a bad value is harder to
# take back than a rejected prompt.
# The username pattern has no length limit. A very long name passes
# here and can still fail at useradd further down, and this script
# keeps going after that failure.
if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
    echo "Error: port must be a number between 1 and 65535."
    exit 1
fi
if ! [[ "$username" =~ ^[a-z_][a-z0-9_-]*$ ]]; then
    echo "Error: username must start with a lowercase letter or underscore and contain only lowercase letters, digits, '-' and '_'."
    exit 1
fi

# Install required packages
# Use -S instead of -Sy so the package database is not refreshed on its own,
# which would leave the system in a partial upgrade state
# There is no set -e in this script, and I did not add one. If this
# install fails, the lines below still run, and the script can still
# print that setup is complete at the end. I read a success message
# from this script as a claim to check, not as proof.
sudo pacman -S --needed openssh

# Create a new user
# -m makes the home directory that cleanup later deletes with
# userdel -r. If the name already exists on the machine, useradd
# fails, the password step below then changes that existing
# account password, and cleanup deletes the account. I only run
# this with a name I made up for this server.
sudo useradd -m -s /bin/bash "$username"

# Set the generated password for the user
# I pipe the same value twice because passwd asks for the new
# password twice. The output goes to /dev/null so passwd chatter
# does not mix with the connection details I print at the end.
echo -e "$password\n$password" | sudo passwd "$username" > /dev/null

# Backup the SSH server configuration
# This backup is the only copy cleanup can restore from. If I run
# the script a second time, this line copies my hardened config
# over the backup, and the config from before the first run is gone.
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Update the SSH server configuration
# The heredoc marker is unquoted, on purpose and with a risk: $port
# expands into the Port line of the file, which is why the
# validation at the top has to be finished before this block runs.
# I write a whole replacement file instead of editing single lines,
# so settings from the old config do not survive by accident. The
# trade off is that local settings I wanted to keep are gone until
# cleanup puts the backup back.
sudo tee /etc/ssh/sshd_config > /dev/null <<EOT
# SSH Server Configuration
Port $port
PermitRootLogin no
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
AllowAgentForwarding no
AllowTcpForwarding no
PrintMotd no
PrintLastLog yes
PermitEmptyPasswords no
PermitUserEnvironment no
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 0

# Additional hardening options
Protocol 2
MaxAuthTries 3
MaxSessions 3
HostbasedAuthentication no
IgnoreUserKnownHosts yes
LoginGraceTime 30s
StrictModes yes
UseDNS no
PermitTunnel no

# Ciphers and MACs
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,umac-128-etm@openssh.com

EOT

# Nothing here runs sshd -t on the new file before the restart. If
# a line in the block above is wrong for the OpenSSH version on the
# machine, the restart below is the first place that shows up.

# Restart the SSH service
sudo systemctl restart sshd

# Enable and start the SSH service on boot
# Enable is a separate promise from restart. It makes sshd start at
# boot, and cleanup stops the service but never disables it, so a
# reboot after cleanup brings sshd back under the restored config.
sudo systemctl enable sshd

# Function to terminate SSH server and exit script
# The order in this function is the teardown order: the user
# sessions end first, then the user goes, then the service stops,
# then the config file comes back. The restore does not restart
# sshd, because the service was just stopped on purpose. The
# restored config takes effect the next time sshd starts.
function cleanup {
    sudo pkill -u "$username"
    sudo userdel -r "$username"
    sudo systemctl stop sshd
    # Restore the SSH server configuration that was backed up at setup
    if [ -f /etc/ssh/sshd_config.bak ]; then
        sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
    fi
    echo "SSH server terminated"
    # This exit takes the status of the echo above. A caller that
    # checks $? cannot tell a clean teardown from a failed one.
    exit
}

# Register the cleanup function to be called when script is interrupted with Ctrl+C
# I set the trap here, not at the top, and that placement leaves a
# hole. An interrupt during install, user creation, or the config
# write above lands before any trap exists, so cleanup cannot run
# and the new user or the replaced config can be left behind.
trap cleanup INT TERM

# Get the server IP address, skipping the loopback address
# This collects every inet address on the machine, not just one a
# guest should use. A machine with VPN or container addresses can
# print addresses that do not reach this server at all.
server_ip=$(ip addr show | awk '/inet /{print $2}' | sed 's/\/.*//' | grep -v '^127\.')

# Print connection information
# I print the password in plain text because the person connecting
# needs it and I stored it nowhere else. It also sits in terminal
# scrollback until the terminal is closed or cleared.
echo "SSH server setup complete!"
echo "Connection Information:"
echo "Server IP: $server_ip"
echo "Server Port: $port"
echo "Username: $username"
echo "Password: $password"

# Keep the script running until interrupted
# This loop is the server lifetime. Staying alive is what holds
# cleanup pending on a signal instead of letting the script end
# right after setup, so I do not exit or background this part.
while true; do
    sleep 1
done
