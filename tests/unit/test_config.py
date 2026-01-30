"""Unit tests for configuration system."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from cac_mcp_server.config.settings import (
    BuildSettings,
    ContentSettings,
    Settings,
    TestingSettings,
)


class TestContentSettings:
    """Test ContentSettings."""

    def test_default_values(self):
        """Test default content settings."""
        settings = ContentSettings()

        assert settings.repository == "managed"
        assert settings.branch == "master"
        assert settings.auto_update is True

    def test_env_var_override(self):
        """Test environment variable override."""
        os.environ["CAC_MCP_CONTENT__REPOSITORY"] = "/custom/path"
        os.environ["CAC_MCP_CONTENT__BRANCH"] = "develop"

        settings = ContentSettings()

        assert settings.repository == "/custom/path"
        assert settings.branch == "develop"

        # Cleanup
        del os.environ["CAC_MCP_CONTENT__REPOSITORY"]
        del os.environ["CAC_MCP_CONTENT__BRANCH"]


class TestBuildSettings:
    """Test BuildSettings."""

    def test_default_values(self):
        """Test default build settings."""
        settings = BuildSettings()

        assert settings.max_concurrent_builds == 2
        assert settings.timeout == 3600
        assert settings.keep_logs is True

    def test_validation(self):
        """Test settings validation."""
        # Valid values
        settings = BuildSettings(max_concurrent_builds=5)
        assert settings.max_concurrent_builds == 5

        # Invalid values should raise
        with pytest.raises(Exception):  # Pydantic validation error
            BuildSettings(max_concurrent_builds=0)  # ge=1

        with pytest.raises(Exception):
            BuildSettings(max_concurrent_builds=100)  # le=10


class TestTestingSettings:
    """Test TestingSettings."""

    def test_default_values(self):
        """Test default testing settings."""
        settings = TestingSettings()

        assert settings.backend == "podman"
        assert settings.max_concurrent_tests == 4
        assert settings.timeout == 1800

    def test_backend_validation(self):
        """Test backend validation."""
        # Valid backends
        settings1 = TestingSettings(backend="podman")
        assert settings1.backend == "podman"

        settings2 = TestingSettings(backend="docker")
        assert settings2.backend == "docker"

        # Invalid backend should raise
        with pytest.raises(Exception):
            TestingSettings(backend="invalid")


class TestSettings:
    """Test main Settings class."""

    def test_default_settings(self):
        """Test loading default settings."""
        settings = Settings()

        assert settings.content.repository == "managed"
        assert settings.server.mode == "stdio"
        assert settings.build.max_concurrent_builds == 2
        assert settings.testing.backend == "podman"

    def test_yaml_loading(self):
        """Test loading settings from YAML file."""
        yaml_content = """
content:
  repository: /custom/content
  branch: develop

server:
  mode: stdio

build:
  max_concurrent_builds: 4
  timeout: 7200

testing:
  backend: docker
  max_concurrent_tests: 8
"""
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            settings = Settings.from_yaml(Path(yaml_path))

            assert settings.content.repository == "/custom/content"
            assert settings.content.branch == "develop"
            assert settings.build.max_concurrent_builds == 4
            assert settings.build.timeout == 7200
            assert settings.testing.backend == "docker"
            assert settings.testing.max_concurrent_tests == 8
        finally:
            os.unlink(yaml_path)

    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings()
            settings.content.managed_path = Path(tmpdir) / "content"
            settings.build.build_dir = Path(tmpdir) / "builds"
            settings.jobs.database = Path(tmpdir) / "db" / "jobs.db"

            # Directories shouldn't exist yet
            assert not settings.content.managed_path.exists()
            assert not settings.build.build_dir.exists()

            # Create directories
            settings.ensure_directories()

            # Now they should exist
            assert settings.content.managed_path.exists()
            assert settings.build.build_dir.exists()
            assert settings.jobs.database.parent.exists()


class TestConfigMerging:
    """Test configuration merging."""

    def test_yaml_overrides_defaults(self):
        """Test YAML file overrides defaults."""
        yaml_content = """
content:
  repository: /yaml/path

build:
  max_concurrent_builds: 3
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            settings = Settings.load(Path(yaml_path))

            # From YAML
            assert settings.content.repository == "/yaml/path"
            assert settings.build.max_concurrent_builds == 3

            # From defaults (not overridden)
            assert settings.content.branch == "master"
            assert settings.testing.backend == "podman"
        finally:
            os.unlink(yaml_path)

    def test_env_overrides_defaults(self):
        """Test environment variables override defaults when no YAML file provided."""
        # Clean up environment first
        env_var = "CAC_MCP_CONTENT__BRANCH"
        original_value = os.environ.get(env_var)

        try:
            # Set environment variable
            os.environ[env_var] = "env-branch"

            # Load without config file - should use defaults + env vars
            settings = ContentSettings()

            # Env var wins over defaults
            assert settings.branch == "env-branch"

            # Default value used
            assert settings.repository == "managed"
        finally:
            # Clean up
            if original_value is not None:
                os.environ[env_var] = original_value
            elif env_var in os.environ:
                del os.environ[env_var]


class TestPathExpansion:
    """Test path expansion."""

    def test_tilde_expansion(self):
        """Test ~ expansion in paths."""
        settings = ContentSettings(managed_path="~/test/path")

        expanded = settings.managed_path.expanduser()
        assert "~" not in str(expanded)
        assert str(expanded).startswith(str(Path.home()))
