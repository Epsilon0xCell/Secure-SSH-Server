# Secure-SSH-Server
This SSH server is designed to be easy-to-deploy on arch linux, secure and temporary.

# Todo:
Add Logging of all commands
Blacklist IP after many failed attempts for 1 hour
Restrict SSH server within wifi network
don't echo password to terminal to avoid password in history

# How To Use?
Make the script executable and run the script, then use a desired ssh client like termius or prompt 2.
Press ctrl c to destroy the server.
Select your user if you want persistance, find out using "whoami" and then edit the script to not change the password
