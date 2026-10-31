#!/bin/bash

# I treat this script as one half of a pair. The setup below creates a
# user and replaces the live sshd_config, and cleanup near the bottom
# is supposed to undo both. If I change one side I have to check the
# other, because a setup step with no cleanup step leaves the machine
# changed after I said the server was temporary.
#
# This script needs root level changes (useradd, /etc/ssh, systemctl),
# so it only runs for real on an Arch Linux machine with sudo. On any
# other host the honest checks are bash -n and the static tests in
# test_ssh_static.py, and that is all I claim for them.

# State flags for cleanup. Setup changes the machine in stages, and
# cleanup should undo only the stages that actually happened: deleting
# a user this script did not create, or restoring a backup that does
# not exist, would do damage in the name of tidying up.
user_created=0
config_backed_up=0
username=""
port=""

# Function to terminate SSH server and exit script
# The order in this function is the teardown order: the user
# sessions end first, then the user goes, then the service stops and
# is disabled, then the config file comes back. The restore does not
# restart sshd, because the service was just stopped and disabled on
# purpose. The restored config takes effect the next time sshd is
# enabled and started by hand.
cleanup() {
    if [ "$user_created" -eq 1 ]; then
        sudo pkill -u "$username" 2>/dev/null
        sudo userdel -r "$username"
    fi
    # Disable as well as stop. The setup enables sshd at boot, and the
    # first version of cleanup only stopped it, so a reboot after
    # cleanup brought sshd back under the restored config and the
    # "temporary" server was not temporary.
    sudo systemctl disable --now sshd 2>/dev/null || sudo systemctl stop sshd
    # Restore the SSH server configuration that was backed up at setup
    if [ "$config_backed_up" -eq 1 ] && [ -f /etc/ssh/sshd_config.bak ]; then
        sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
    fi
    echo "SSH server terminated"
    exit 0
}

# Register the cleanup function before anything changes the machine.
# The first version set this trap near the bottom, after install, user
# creation, and the config write, so an interrupt during those steps
# landed before any trap existed and left the new user or the replaced
# config behind. The state flags above are what make an early trap
# safe: before stage one completes, cleanup has nothing to undo.
trap cleanup INT TERM

# Generate a random password
# I make the password before the prompts so the value exists by the
# time user creation needs it. It comes from 12 bytes from openssl,
# base64 encoded, so what gets printed later is longer than 12
# characters. I store it in no file. The printout at the end is the
# only copy, and closing the terminal before connecting loses it.
password=$(openssl rand -base64 12)
if [ -z "$password" ]; then
    echo "Error: openssl failed to generate a password." >&2
    exit 1
fi

# Prompt for server port and username
# I use a different port default to mitigate attack surface.
read -p "Enter the server port (default: 25): " port
port=${port:-25}
read -p "Enter the username for SSH access: " username
# Port 25 is the default if I just press enter. That port is well
# known and normally belongs to mail, so on a machine that already
# runs a mail server this default can collide instead of working.

# Validate the port and username before either is used in a command or
# written into the SSH server configuration. This is the only prompt
# path in the script, and every later use reads these same two
# variables, so validating here covers every path the values can take.
# I do this check before sudo, pacman, or any file write. Once the
# port reaches the heredoc below it becomes a line in sshd_config,
# and once the username reaches useradd a bad value is harder to
# take back than a rejected prompt. The username pattern also gets a
# length cap here: the first version had none, and a very long name
# passed the pattern and then failed at useradd, after which the
# script kept going.
if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
    echo "Error: port must be a number between 1 and 65535."
    exit 1
fi
if ! [[ "$username" =~ ^[a-z_][a-z0-9_-]*$ ]] || [ "${#username}" -gt 32 ]; then
    echo "Error: username must start with a lowercase letter or underscore, contain only lowercase letters, digits, '-' and '_', and be at most 32 characters."
    exit 1
fi

# Refuse a name that already belongs to an account on this machine.
# The first version went ahead when useradd failed on an existing
# name: the password step then changed that existing account's
# password, and cleanup deleted the account. Checking first turns
# that whole class of accident into one clear refusal.
if id "$username" >/dev/null 2>&1; then
    echo "Error: user '$username' already exists. Pick a name made up for this server."
    exit 1
fi

# Install required packages
# Use -S instead of -Sy so the package database is not refreshed on its own,
# which would leave the system in a partial upgrade state.
# If the install fails there is no sshd to configure, so I stop here
# instead of letting the success message at the end claim otherwise.
if ! sudo pacman -S --needed openssh; then
    echo "Error: installing openssh failed." >&2
    exit 1
fi

# Create a new user
# -m makes the home directory that cleanup later deletes with
# userdel -r.
if ! sudo useradd -m -s /bin/bash "$username"; then
    echo "Error: creating user '$username' failed." >&2
    exit 1
fi
user_created=1

# Set the generated password for the user
# I pipe the same value twice because passwd asks for the new
# password twice. The output goes to /dev/null so passwd chatter
# does not mix with the connection details I print at the end.
if ! echo -e "$password\n$password" | sudo passwd "$username" > /dev/null; then
    echo "Error: setting the password failed." >&2
    cleanup
fi

# Backup the SSH server configuration
# This backup is the only copy cleanup can restore from. A second run
# must not overwrite it: the first version copied the already
# hardened config over the backup on a rerun, and the config from
# before the first run was gone. If a backup already exists, I keep
# it and say so.
if [ -f /etc/ssh/sshd_config.bak ]; then
    echo "Keeping the existing /etc/ssh/sshd_config.bak from an earlier run."
    config_backed_up=1
else
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
    config_backed_up=1
fi

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

# Validate the new configuration before restarting sshd with it. If
# a line in the block above is wrong for the OpenSSH version on the
# machine, restarting first would take the running server down with a
# broken config. On a validation failure I put the backup back and
# stop, with sshd still running its previous configuration.
if ! sudo sshd -t; then
    echo "Error: the new sshd_config did not pass sshd -t. Restoring the backup." >&2
    if [ -f /etc/ssh/sshd_config.bak ]; then
        sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
    fi
    exit 1
fi

# Restart the SSH service
if ! sudo systemctl restart sshd; then
    echo "Error: restarting sshd failed." >&2
    exit 1
fi

# Enable and start the SSH service on boot
# Enable is a separate promise from restart. It makes sshd start at
# boot, and cleanup now disables it again, so the pair matches.
if ! sudo systemctl enable sshd; then
    echo "Error: enabling sshd failed." >&2
    exit 1
fi

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
