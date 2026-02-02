"""Plain text document parser."""

import re
from pathlib import Path

from content_agent.core.parsing.base_parser import BaseParser, ParsingError
from content_agent.models.control import ParsedDocument


class TextParser(BaseParser):
    """Parser for plain text documents."""

    def parse(self, source: str | Path) -> ParsedDocument:
        """Parse a plain text document.

        Args:
            source: Path to text file

        Returns:
            ParsedDocument with extracted content

        Raises:
            ParsingError: If parsing fails
        """
        path = Path(source) if isinstance(source, str) else source

        if not path.exists():
            raise ParsingError(f"Text file not found: {path}")

        try:
            # Read file content
            text = self.extract_text(path)

            # Extract title (first non-empty line or filename)
            title = ""
            for line in text.split("\n"):
                if line.strip():
                    title = line.strip()
                    break
            if not title:
                title = path.stem

            # Parse sections
            sections = self._parse_sections(text)

            return ParsedDocument(
                title=title,
                sections=sections,
                requirements=[],  # Will be populated by AI extraction
                metadata={"filename": path.name},
                source_path=str(path),
                source_type="text",
            )

        except Exception as e:
            raise ParsingError(f"Failed to parse text file: {e}") from e

    def extract_text(self, source: str | Path) -> str:
        """Extract raw text from file.

        Args:
            source: Path to text file

        Returns:
            Raw text content

        Raises:
            ParsingError: If extraction fails
        """
        path = Path(source) if isinstance(source, str) else source

        try:
            # Try UTF-8 first, fall back to latin-1
            try:
                return path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return path.read_text(encoding="latin-1")
        except Exception as e:
            raise ParsingError(f"Failed to extract text: {e}") from e

    def _parse_sections(self, text: str) -> list:
        """Parse sections from plain text.

        Args:
            text: Plain text content

        Returns:
            List of DocumentSection objects
        """
        lines = text.split("\n")
        flat_sections = []
        current_section: tuple[int, str, list[str]] | None = None

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            heading_level = self._detect_heading_level(stripped)

            if heading_level is not None:
                # Save previous section
                if current_section:
                    level, title, content_lines = current_section
                    flat_sections.append((level, title, "\n".join(content_lines)))

                # Start new section
                current_section = (heading_level, stripped, [])
            elif current_section:
                # Add to current section content
                current_section[2].append(line)

        # Save last section
        if current_section:
            level, title, content_lines = current_section
            flat_sections.append((level, title, "\n".join(content_lines)))

        # If no sections found, treat whole document as one section
        if not flat_sections:
            first_line = text.split("\n")[0].strip() if text else "Document"
            flat_sections.append((1, first_line, text))

        return self._create_section_hierarchy(flat_sections)

    def _detect_heading_level(self, line: str) -> int | None:
        """Detect if line is a heading in plain text.

        Args:
            line: Line of text

        Returns:
            Heading level (1-6) or None
        """
        # Pattern 1: All caps, short lines
        if len(line) < 100 and line.isupper() and len(line.split()) <= 10:
            return 1

        # Pattern 2: Numbered sections (e.g., "1. Introduction", "2.1 Overview")
        numbered_pattern = r"^(\d+\.)+\s+[A-Z]"
        if re.match(numbered_pattern, line):
            dots = line.split()[0].count(".")
            return min(dots + 1, 6)

        # Pattern 3: Section markers
        section_pattern = r"^(Section|Chapter|Part|Appendix)\s+\d+"
        if re.match(section_pattern, line, re.IGNORECASE):
            return 1

        # Pattern 4: Lines followed by underlines (=== or ---)
        # Note: This requires context from multiple lines, handled separately

        return None
