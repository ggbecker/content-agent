"""Text comparison tools for validating extracted requirements."""

import difflib
from typing import Any


class TextComparator:
    """Compare original document text with extracted requirements."""

    def compare_texts(
        self,
        original: str,
        extracted: str,
        context_lines: int = 3,
    ) -> dict[str, Any]:
        """Compare original and extracted text.

        Args:
            original: Original text from document
            extracted: Extracted requirement text
            context_lines: Number of context lines in diff

        Returns:
            Dictionary with comparison results
        """
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, original, extracted).ratio()

        # Generate unified diff
        original_lines = original.splitlines(keepends=True)
        extracted_lines = extracted.splitlines(keepends=True)

        diff = list(
            difflib.unified_diff(
                original_lines,
                extracted_lines,
                fromfile="original",
                tofile="extracted",
                lineterm="",
                n=context_lines,
            )
        )

        # Check for exact match
        exact_match = original.strip() == extracted.strip()

        # Detect potential issues
        issues = []

        if similarity < 0.9 and not exact_match:
            issues.append(
                f"Text similarity is low ({similarity:.2%}). Text may have been modified."
            )

        if len(extracted) < len(original) * 0.5:
            issues.append(
                "Extracted text is significantly shorter than original. Content may be missing."
            )

        if len(extracted) > len(original) * 1.5:
            issues.append(
                "Extracted text is significantly longer than original. Extra content may have been added."
            )

        # Check for common rewording patterns
        rewording_indicators = [
            ("must", "should"),
            ("shall", "must"),
            ("required", "needed"),
        ]

        for orig_word, reword in rewording_indicators:
            if orig_word in original.lower() and reword in extracted.lower():
                if orig_word not in extracted.lower():
                    issues.append(
                        f"Possible rewording detected: '{orig_word}' -> '{reword}'"
                    )

        return {
            "exact_match": exact_match,
            "similarity": similarity,
            "diff": "".join(diff) if diff else None,
            "issues": issues,
            "original_length": len(original),
            "extracted_length": len(extracted),
        }

    def batch_compare(
        self,
        comparisons: list[tuple[str, str]],
    ) -> list[dict[str, Any]]:
        """Compare multiple text pairs.

        Args:
            comparisons: List of (original, extracted) tuples

        Returns:
            List of comparison results
        """
        results = []

        for original, extracted in comparisons:
            result = self.compare_texts(original, extracted)
            results.append(result)

        return results

    def generate_comparison_report(
        self,
        comparisons: list[tuple[str, str, str]],  # (id, original, extracted)
    ) -> str:
        """Generate human-readable comparison report.

        Args:
            comparisons: List of (requirement_id, original, extracted) tuples

        Returns:
            Formatted report text
        """
        report_lines = [
            "# Text Comparison Report",
            "",
            f"Total requirements: {len(comparisons)}",
            "",
        ]

        exact_matches = 0
        issues_found = 0

        for req_id, original, extracted in comparisons:
            result = self.compare_texts(original, extracted)

            if result["exact_match"]:
                exact_matches += 1
            if result["issues"]:
                issues_found += 1

            report_lines.extend(
                [
                    f"## Requirement: {req_id}",
                    "",
                    f"- Exact match: {result['exact_match']}",
                    f"- Similarity: {result['similarity']:.2%}",
                    f"- Original length: {result['original_length']} chars",
                    f"- Extracted length: {result['extracted_length']} chars",
                    "",
                ]
            )

            if result["issues"]:
                report_lines.append("**Issues:**")
                for issue in result["issues"]:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

            if result["diff"]:
                report_lines.extend(
                    [
                        "**Diff:**",
                        "```",
                        result["diff"],
                        "```",
                        "",
                    ]
                )

        # Summary
        report_lines.insert(
            3,
            f"Exact matches: {exact_matches}/{len(comparisons)} ({exact_matches/len(comparisons)*100:.1f}%)",
        )
        report_lines.insert(
            4,
            f"Requirements with issues: {issues_found}",
        )

        return "\n".join(report_lines)
