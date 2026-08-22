import pytest
from modules.command_line_custom import (
    _remove_block, _block_exists, _build_block,
    _get_current_state, PROMPT_BLOCK_START, PROMPT_BLOCK_END,
)

SAMPLE_BASHRC = """export PATH=$PATH:/usr/local/bin
alias ll='ls -la'

# === PROMPT CONFIGURED BY SERVERSETUP_CLI ===
# FEATURE:branch
# FEATURE:time
parse_git_branch() {
    git branch 2> /dev/null
}
PS1='\\u@\\h\\$ '
# =============================================

export EDITOR=nano
"""

SAMPLE_BASHRC_NO_BLOCK = """export PATH=$PATH:/usr/local/bin
alias ll='ls -la'
"""

class TestBlockExists:
    def test_detects_existing_block(self):
        assert _block_exists(SAMPLE_BASHRC) is True

    def test_no_block_returns_false(self):
        assert _block_exists(SAMPLE_BASHRC_NO_BLOCK) is False

class TestRemoveBlock:
    def test_removes_block_completely(self):
        result = _remove_block(SAMPLE_BASHRC)
        assert PROMPT_BLOCK_START not in result
        assert PROMPT_BLOCK_END not in result
        assert "parse_git_branch" not in result

    def test_preserves_content_outside_block(self):
        result = _remove_block(SAMPLE_BASHRC)
        assert "export PATH=$PATH:/usr/local/bin" in result
        assert "alias ll='ls -la'" in result
        assert "export EDITOR=nano" in result

    def test_removing_nonexistent_block_is_noop(self):
        result = _remove_block(SAMPLE_BASHRC_NO_BLOCK)
        assert result == SAMPLE_BASHRC_NO_BLOCK

class TestGetCurrentState:
    def test_detects_active_features(self):
        state = _get_current_state(SAMPLE_BASHRC)
        assert state["branch"] is True
        assert state["time"] is True
        assert state["venv"] is False

    def test_no_features_when_no_block(self):
        state = _get_current_state(SAMPLE_BASHRC_NO_BLOCK)
        assert state["branch"] is False
        assert state["time"] is False
        assert state["venv"] is False

class TestBuildBlock:
    def test_branch_only_contains_git_functions(self):
        block = _build_block(branch=True, time=False, venv=False)
        assert "parse_git_branch" in block
        assert "parse_git_dirty" in block
        assert "show_venv" not in block
        assert "FEATURE:branch" in block
        assert "FEATURE:time" not in block

    def test_all_features_present(self):
        block = _build_block(branch=True, time=True, venv=True)
        assert "parse_git_branch" in block
        assert "show_venv" in block
        assert "\\t" in block 
        assert "FEATURE:branch" in block
        assert "FEATURE:time" in block
        assert "FEATURE:venv" in block

    def test_no_features_still_has_base_prompt(self):
        block = _build_block(branch=False, time=False, venv=False)
        assert "\\u@\\h" in block
        assert "parse_git_branch" not in block
        assert "show_venv" not in block

    def test_block_has_start_and_end_markers(self):
        block = _build_block(branch=True, time=True, venv=True)
        assert PROMPT_BLOCK_START in block
        assert PROMPT_BLOCK_END in block
