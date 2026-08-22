import pytest
from modules.users import (
    is_valid_username, user_exists, create_user,
    add_to_group, grant_sudo, revoke_sudo, delete_user,
    setup_ssh_key, list_users, prompt_new_user,
)

# ── is_valid_username ────────────────────────────────────────────

class TestIsValidUsername:
    def test_accepts_simple_name(self):
        assert is_valid_username("devuser") is True

    def test_accepts_with_underscore_and_hyphen(self):
        assert is_valid_username("dev_user-01") is True

    def test_accepts_starting_with_underscore(self):
        assert is_valid_username("_system") is True

    def test_rejects_empty(self):
        assert is_valid_username("") is False

    def test_rejects_uppercase(self):
        assert is_valid_username("DevUser") is False

    def test_rejects_starting_with_digit(self):
        assert is_valid_username("1devuser") is False

    def test_rejects_spaces(self):
        assert is_valid_username("dev user") is False

    def test_rejects_too_long(self):
        assert is_valid_username("a" * 33) is False

# ── user_exists ───────────────────────────────────────────────────

class TestUserExists:
    def test_returns_true_when_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        assert user_exists("devuser") is True

    def test_returns_false_when_not_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        assert user_exists("nonexistent") is False

# ── create_user ───────────────────────────────────────────────────

class TestCreateUser:
    def test_rejects_invalid_username(self, mock_run_command):
        mock = mock_run_command("modules.users")
        result = create_user("Invalid User")
        mock.assert_not_called()
        assert result is False

    def test_skips_if_already_exists(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        result = create_user("devuser")
        mock.assert_not_called()
        assert result is True

    def test_creates_if_not_exists(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", side_effect=[False, True])
        mock = mock_run_command("modules.users")
        result = create_user("devuser")
        mock.assert_called_once_with(
            ["adduser", "--disabled-password", "--gecos", "", "devuser"]
        )
        assert result is True

    def test_reports_failure_if_creation_did_not_work(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", side_effect=[False, False])
        mock_run_command("modules.users")
        result = create_user("devuser")
        assert result is False

# ── add_to_group / grant_sudo / revoke_sudo ──────────────────────

class TestAddToGroup:
    def test_fails_if_user_does_not_exist(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=False)
        mock = mock_run_command("modules.users")
        result = add_to_group("ghost", "sudo")
        mock.assert_not_called()
        assert result is False

    def test_adds_user_to_group(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        result = add_to_group("devuser", "docker")
        mock.assert_called_once_with(["usermod", "-aG", "docker", "devuser"])
        assert result is True

class TestGrantSudo:
    def test_calls_add_to_group_with_sudo(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        grant_sudo("devuser")
        mock.assert_called_once_with(["usermod", "-aG", "sudo", "devuser"])

class TestRevokeSudo:
    def test_fails_if_user_does_not_exist(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=False)
        mock = mock_run_command("modules.users")
        result = revoke_sudo("ghost")
        mock.assert_not_called()
        assert result is False

    def test_removes_sudo_group(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        result = revoke_sudo("devuser")
        mock.assert_called_once_with(["deluser", "devuser", "sudo"])
        assert result is True

# ── delete_user ───────────────────────────────────────────────────

class TestDeleteUser:
    def test_warns_if_user_does_not_exist(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=False)
        mock = mock_run_command("modules.users")
        result = delete_user("ghost")
        mock.assert_not_called()
        assert result is False

    def test_deletes_with_home_by_default(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        delete_user("devuser")
        mock.assert_called_once_with(["deluser", "--remove-home", "devuser"])

    def test_deletes_keeping_home_when_requested(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")
        delete_user("devuser", remove_home=False)
        mock.assert_called_once_with(["deluser", "devuser"])

# ── setup_ssh_key ─────────────────────────────────────────────────

class TestSetupSshKey:
    def test_fails_if_user_does_not_exist(self, mocker, mock_run_command):
        mocker.patch("modules.users.user_exists", return_value=False)
        mock = mock_run_command("modules.users")
        result = setup_ssh_key("ghost", "ssh-ed25519 AAAA...")
        mock.assert_not_called()
        assert result is False

    def test_creates_ssh_dir_with_correct_permissions(self, mocker, mock_run_command, tmp_path):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock_run_command("modules.users")

        result = setup_ssh_key("devuser", "ssh-ed25519 AAAAtest", home_dir=str(tmp_path))

        ssh_dir = tmp_path / ".ssh"
        assert ssh_dir.exists()
        assert oct(ssh_dir.stat().st_mode)[-3:] == "700"
        assert result is True

    def test_writes_key_to_authorized_keys(self, mocker, mock_run_command, tmp_path):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock_run_command("modules.users")

        setup_ssh_key("devuser", "ssh-ed25519 AAAAtest comment", home_dir=str(tmp_path))

        auth_keys = tmp_path / ".ssh" / "authorized_keys"
        content = auth_keys.read_text()
        assert "ssh-ed25519 AAAAtest comment" in content

    def test_authorized_keys_has_correct_permissions(self, mocker, mock_run_command, tmp_path):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock_run_command("modules.users")

        setup_ssh_key("devuser", "ssh-ed25519 AAAAtest", home_dir=str(tmp_path))

        auth_keys = tmp_path / ".ssh" / "authorized_keys"
        assert oct(auth_keys.stat().st_mode)[-3:] == "600"

    def test_appends_multiple_keys_without_overwriting(self, mocker, mock_run_command, tmp_path):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock_run_command("modules.users")

        setup_ssh_key("devuser", "ssh-ed25519 AAAAfirst", home_dir=str(tmp_path))
        setup_ssh_key("devuser", "ssh-ed25519 AAAAsecond", home_dir=str(tmp_path))

        auth_keys = tmp_path / ".ssh" / "authorized_keys"
        content = auth_keys.read_text()
        assert "AAAAfirst" in content
        assert "AAAAsecond" in content

    def test_calls_chown_on_ssh_dir(self, mocker, mock_run_command, tmp_path):
        mocker.patch("modules.users.user_exists", return_value=True)
        mock = mock_run_command("modules.users")

        setup_ssh_key("devuser", "ssh-ed25519 AAAAtest", home_dir=str(tmp_path))

        ssh_dir = str(tmp_path / ".ssh")
        mock.assert_called_once_with(["chown", "-R", "devuser:devuser", ssh_dir])

# ── list_users ────────────────────────────────────────────────────

class TestListUsers:
    def test_filters_by_min_uid(self, tmp_path):
        passwd_content = (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            "devuser:x:1000:1000:Dev User:/home/devuser:/bin/bash\n"
            "webuser:x:1001:1001:Web User:/home/webuser:/bin/bash\n"
        )
        passwd_file = tmp_path / "passwd"
        passwd_file.write_text(passwd_content)

        users = list_users(min_uid=1000, passwd_file=str(passwd_file))
        usernames = [u["username"] for u in users]

        assert "devuser" in usernames
        assert "webuser" in usernames
        assert "root" not in usernames
        assert "daemon" not in usernames

    def test_excludes_nologin_shell(self, tmp_path):
        passwd_content = (
            "sysuser:x:1000:1000:System User:/home/sysuser:/usr/sbin/nologin\n"
            "realuser:x:1001:1001:Real User:/home/realuser:/bin/bash\n"
        )
        passwd_file = tmp_path / "passwd"
        passwd_file.write_text(passwd_content)

        users = list_users(min_uid=1000, passwd_file=str(passwd_file))
        usernames = [u["username"] for u in users]

        assert "realuser" in usernames
        assert "sysuser" not in usernames

# ── prompt_new_user ───────────────────────────────────────────────

class TestPromptNewUser:
    def test_returns_none_when_declined(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "n")
        result = prompt_new_user()
        assert result is None

    def test_returns_username_password_sudo_when_confirmed(self, mocker, monkeypatch):
        inputs = iter(["y", "devuser", "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        mocker.patch("getpass.getpass", side_effect=["password123", "password123"])

        result = prompt_new_user()

        assert result == ("devuser", "password123", True)

    def test_reprompts_on_password_mismatch(self, mocker, monkeypatch):
        inputs = iter(["y", "devuser", "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        mocker.patch("getpass.getpass", side_effect=["pass1", "pass2", "pass3", "pass3"])

        result = prompt_new_user()

        assert result == ("devuser", "pass3", True)
