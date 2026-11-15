import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.core.config import settings


class SecurityError(Exception):
    """Raised when an unsafe path or security policy violation occurs."""
    pass


class WorkspaceService:
    """
    Manages isolated filesystem workspaces for generated projects.
    Guarantees strict sandbox containment and protects against directory traversal attacks.
    """

    def __init__(self, root_dir: Optional[str] = None):
        if root_dir:
            self.root_dir = Path(root_dir).resolve()
        else:
            # Point to generated_projects directory at repo root
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.root_dir = (base_dir / "generated_projects").resolve()

        os.makedirs(self.root_dir, exist_ok=True)

    def slugify(self, text: str) -> str:
        """Create a filesystem-safe project slug."""
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug or "unnamed-project"

    def get_workspace_dir(self, project_slug: str) -> Path:
        """Return the absolute path of a project workspace."""
        clean_slug = self.slugify(project_slug)
        workspace = (self.root_dir / clean_slug).resolve()
        os.makedirs(workspace, exist_ok=True)
        return workspace

    def resolve_safe_path(self, project_slug: str, relative_path: str) -> Path:
        """
        Resolve and strictly validate a relative file path within the project workspace.
        Raises SecurityError if directory traversal or path escape is detected.
        """
        workspace = self.get_workspace_dir(project_slug)

        # Normalize slashes and reject obvious absolute path prefixes
        clean_rel = relative_path.replace("\\", "/").lstrip("/")
        if not clean_rel or clean_rel == "." or clean_rel == "..":
            raise SecurityError(f"Invalid file path: '{relative_path}'")

        target_path = (workspace / clean_rel).resolve()

        # Strict containment verification
        try:
            target_path.relative_to(workspace)
        except ValueError:
            raise SecurityError(
                f"Path traversal detected! Path '{relative_path}' escapes workspace '{workspace}'."
            )

        return target_path

    def write_file(
        self,
        project_slug: str,
        relative_path: str,
        content: str,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        """
        Safely write content to a file inside the isolated project workspace.
        Automatically creates parent directories and calculates SHA-256 hash.
        """
        safe_path = self.resolve_safe_path(project_slug, relative_path)

        if safe_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists and overwrite is False: '{relative_path}'")

        # Create parent directories safely
        os.makedirs(safe_path.parent, exist_ok=True)

        content_bytes = content.encode("utf-8")
        file_hash = hashlib.sha256(content_bytes).hexdigest()

        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)

        workspace = self.get_workspace_dir(project_slug)
        rel_to_workspace = str(safe_path.relative_to(workspace)).replace("\\", "/")

        return {
            "relative_path": rel_to_workspace,
            "absolute_path": str(safe_path),
            "size_bytes": len(content_bytes),
            "sha256": file_hash,
        }

    def read_file(self, project_slug: str, relative_path: str) -> str:
        """Safely read content from a file inside the project workspace."""
        safe_path = self.resolve_safe_path(project_slug, relative_path)
        if not safe_path.exists():
            raise FileNotFoundError(f"File not found in workspace: '{relative_path}'")

        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_files(self, project_slug: str) -> List[Dict[str, Any]]:
        """List all generated files within the project workspace."""
        workspace = self.get_workspace_dir(project_slug)
        results = []

        ignore_dirs = {".git", "__pycache__", "node_modules", ".pytest_cache", ".venv"}

        for root, dirs, files in os.walk(workspace):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file_name in files:
                file_path = Path(root) / file_name
                rel_path = str(file_path.relative_to(workspace)).replace("\\", "/")
                content_bytes = file_path.read_bytes()
                results.append({
                    "relative_path": rel_path,
                    "size_bytes": len(content_bytes),
                    "sha256": hashlib.sha256(content_bytes).hexdigest(),
                })

        return sorted(results, key=lambda x: x["relative_path"])


workspace_service = WorkspaceService()
