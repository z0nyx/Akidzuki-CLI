"""Smoke tests for the akidzuki CLI entry points."""

import sys


def test_list_command_runs_without_connections(tmp_path, monkeypatch, capsys):
    """`akidzuki list` must run cleanly on a fresh config, not crash on startup."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["akidzuki", "list"])
    from akidzuki_cli.cli import main_cli

    main_cli()
    assert "No connections found" in capsys.readouterr().out
