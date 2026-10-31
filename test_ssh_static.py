"""Static checks for ssh.sh.

This script changes users, /etc/ssh, and systemd state, so I do not
run it on a test host. What I can check honestly without an Arch
machine with sudo is the shape of the script: syntax, and that the
fixes for the weaknesses the security audit listed are present in
the text and in the right order. These tests read the file; they do
not execute the setup.
"""

import pathlib
import subprocess
import unittest

SCRIPT = pathlib.Path(__file__).with_name("ssh.sh")
TEXT = SCRIPT.read_text()


class SyntaxTests(unittest.TestCase):
    def test_bash_syntax(self):
        out = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)


class AuditFixTests(unittest.TestCase):
    def test_trap_registered_before_first_system_change(self):
        self.assertLess(TEXT.index("trap cleanup INT TERM"), TEXT.index("pacman -S"))

    def test_existing_user_is_refused(self):
        self.assertIn('if id "$username"', TEXT)
        self.assertLess(TEXT.index('if id "$username"'), TEXT.index("sudo useradd"))

    def test_cleanup_disables_sshd(self):
        self.assertIn("systemctl disable --now sshd", TEXT)

    def test_config_validated_before_restart(self):
        self.assertLess(TEXT.index("sshd -t"), TEXT.index("systemctl restart sshd"))

    def test_backup_is_not_overwritten_on_rerun(self):
        self.assertIn("Keeping the existing /etc/ssh/sshd_config.bak", TEXT)

    def test_port_range_validation_present(self):
        self.assertIn('[ "$port" -gt 65535 ]', TEXT)

    def test_username_length_cap_present(self):
        self.assertIn('"${#username}" -gt 32', TEXT)

    def test_cleanup_only_undoes_completed_stages(self):
        self.assertIn('"$user_created" -eq 1', TEXT)
        self.assertIn('"$config_backed_up" -eq 1', TEXT)


if __name__ == "__main__":
    unittest.main()
