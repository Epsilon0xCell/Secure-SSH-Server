#!/bin/bash

# Generate a random password
password=$(openssl rand -base64 12)

# Prompt for server port and username
# we use a different port default to mitigate attack surface.
read -p "Enter the server port (default: 25): " port
port=${port:-25}
read -p "Enter the username for SSH access: " username

# Validate the port and username before either is used in a command or
# written into the SSH server configuration
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
sudo pacman -S --needed openssh

# Create a new user
sudo useradd -m -s /bin/bash "$username"

# Set the generated password for the user
echo -e "$password\n$password" | sudo passwd "$username" > /dev/null

# Backup the SSH server configuration
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Update the SSH server configuration
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

# Restart the SSH service
sudo systemctl restart sshd

# Enable and start the SSH service on boot
sudo systemctl enable sshd

# Function to terminate SSH server and exit script
function cleanup {
    sudo pkill -u "$username"
    sudo userdel -r "$username"
    sudo systemctl stop sshd
    # Restore the SSH server configuration that was backed up at setup
    if [ -f /etc/ssh/sshd_config.bak ]; then
        sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
    fi
    echo "SSH server terminated"
    exit
}

# Register the cleanup function to be called when script is interrupted with Ctrl+C
trap cleanup INT TERM

# Get the server IP address, skipping the loopback address
server_ip=$(ip addr show | awk '/inet /{print $2}' | sed 's/\/.*//' | grep -v '^127\.')

# Print connection information
echo "SSH server setup complete!"
echo "Connection Information:"
echo "Server IP: $server_ip"
echo "Server Port: $port"
echo "Username: $username"
echo "Password: $password"

# Keep the script running until interrupted
while true; do
    sleep 1
done
