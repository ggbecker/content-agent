"""Content repository management."""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

import git

from content_agent.config import get_settings

logger = logging.getLogger(__name__)


class ContentRepository:
    """Manages the ComplianceAsCode/content repository."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize content repository manager.

        Args:
            repo_path: Optional explicit repository path (overrides config)
        """
        self.settings = get_settings()

        if repo_path:
            self._repo_path = repo_path
            self._is_managed = False
        elif self.settings.content.repository == "managed":
            self._repo_path = Path(self.settings.content.managed_path).expanduser()
            self._is_managed = True
        else:
            self._repo_path = Path(self.settings.content.repository).expanduser()
            self._is_managed = False

        self._repo: Optional[git.Repo] = None
        self._initialized = False

    @property
    def path(self) -> Path:
        """Get repository path.

        Returns:
            Repository path
        """
        return self._repo_path

    @property
    def is_managed(self) -> bool:
        """Check if repository is managed by the server.

        Returns:
            True if managed
        """
        return self._is_managed

    @property
    def build_path(self) -> Path:
        """Get build directory path.

        Returns:
            Build directory path (usually content/build)
        """
        return self._repo_path / "build"

    def get_product_build_path(self, product: str) -> Optional[Path]:
        """Get build path for a specific product.

        Args:
            product: Product identifier

        Returns:
            Product build path or None if not built
        """
        product_build = self.build_path / product
        return product_build if product_build.exists() else None

    def initialize(self) -> None:
        """Initialize repository (clone if managed, validate if existing).

        Raises:
            RuntimeError: If repository initialization fails
        """
        if self._initialized:
            return

        logger.info(f"Initializing content repository at {self._repo_path}")

        if self._is_managed:
            self._initialize_managed()
        else:
            self._validate_existing()

        self._add_to_python_path()
        self._initialized = True
        logger.info("Content repository initialized successfully")

    def _initialize_managed(self) -> None:
        """Initialize managed repository (clone or update).

        Raises:
            RuntimeError: If clone/update fails
        """
        if self._repo_path.exists():
            logger.info(f"Managed repository exists at {self._repo_path}")
            try:
                self._repo = git.Repo(self._repo_path)

                if self.settings.content.auto_update:
                    logger.info("Auto-updating managed repository")
                    self.update()
            except git.exc.InvalidGitRepositoryError:
                logger.warning(
                    f"Invalid git repository at {self._repo_path}, removing and re-cloning"
                )
                shutil.rmtree(self._repo_path)
                self._clone_repository()
        else:
            logger.info(f"Cloning repository to {self._repo_path}")
            self._clone_repository()

    def _clone_repository(self) -> None:
        """Clone the repository.

        Raises:
            RuntimeError: If clone fails
        """
        try:
            self._repo_path.parent.mkdir(parents=True, exist_ok=True)
            self._repo = git.Repo.clone_from(
                self.settings.content.repo_url,
                self._repo_path,
                branch=self.settings.content.branch,
                depth=1,  # Shallow clone for speed
            )
            logger.info(f"Repository cloned successfully to {self._repo_path}")
        except git.exc.GitCommandError as e:
            raise RuntimeError(f"Failed to clone repository: {e}") from e

    def _validate_existing(self) -> None:
        """Validate existing repository.

        Raises:
            RuntimeError: If repository is invalid
        """
        if not self._repo_path.exists():
            raise RuntimeError(
                f"Repository path does not exist: {self._repo_path}\n"
                f"Either create it or use 'managed' mode to auto-clone"
            )

        # Check for key directories
        required_dirs = ["ssg", "linux_os", "products"]
        missing_dirs = [d for d in required_dirs if not (self._repo_path / d).exists()]

        if missing_dirs:
            raise RuntimeError(
                f"Repository at {self._repo_path} appears invalid.\n"
                f"Missing required directories: {', '.join(missing_dirs)}"
            )

        # Try to open as git repo (optional, not required)
        try:
            self._repo = git.Repo(self._repo_path)
            logger.info(f"Using existing repository at {self._repo_path}")
        except git.exc.InvalidGitRepositoryError:
            logger.warning(
                f"Path {self._repo_path} is not a git repository, "
                f"but appears to contain content"
            )

    def _add_to_python_path(self) -> None:
        """Add repository to Python path for SSG module imports."""
        repo_str = str(self._repo_path.resolve())
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)
            logger.debug(f"Added {repo_str} to Python path")

    def update(self) -> bool:
        """Update managed repository.

        Returns:
            True if update successful, False if not managed or failed

        Raises:
            RuntimeError: If update fails
        """
        if not self._is_managed:
            logger.warning("Cannot update non-managed repository")
            return False

        if not self._repo:
            raise RuntimeError("Repository not initialized")

        try:
            logger.info("Pulling latest changes")
            origin = self._repo.remotes.origin
            origin.pull(self.settings.content.branch)
            logger.info("Repository updated successfully")
            return True
        except git.exc.GitCommandError as e:
            logger.error(f"Failed to update repository: {e}")
            raise RuntimeError(f"Failed to update repository: {e}") from e

    def get_commit_info(self) -> Optional[dict]:
        """Get current commit information.

        Returns:
            Commit info dict or None if not a git repo
        """
        if not self._repo:
            return None

        try:
            commit = self._repo.head.commit
            return {
                "sha": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
            }
        except Exception as e:
            logger.warning(f"Failed to get commit info: {e}")
            return None

    def get_ssg_version(self) -> Optional[str]:
        """Get SSG version from CMakeLists.txt.

        Returns:
            Version string or None
        """
        cmake_file = self._repo_path / "CMakeLists.txt"
        if not cmake_file.exists():
            return None

        try:
            content = cmake_file.read_text()
            # Look for project(scap_security_guide VERSION X.Y.Z)
            import re

            match = re.search(r"project\([^)]*VERSION\s+(\S+)", content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.warning(f"Failed to parse version from CMakeLists.txt: {e}")

        return None


# Global content repository instance
_content_repo: Optional[ContentRepository] = None


def get_content_repository() -> ContentRepository:
    """Get the global content repository instance.

    Returns:
        ContentRepository instance

    Raises:
        RuntimeError: If not initialized
    """
    if _content_repo is None:
        raise RuntimeError(
            "Content repository not initialized. Call initialize_content_repository() first."
        )
    return _content_repo


def initialize_content_repository(repo_path: Optional[Path] = None) -> ContentRepository:
    """Initialize the global content repository.

    Args:
        repo_path: Optional explicit repository path

    Returns:
        ContentRepository instance
    """
    global _content_repo
    _content_repo = ContentRepository(repo_path)
    _content_repo.initialize()
    return _content_repo
