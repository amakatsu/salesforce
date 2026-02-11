#!/usr/bin/env python3
"""Excel specification validator utilities for PR-Agent UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import List, Sequence

import pandas as pd


@dataclass
class SheetSummary:
    name: str
    rows: int
    columns: int
    missing_required_columns: List[str] = field(default_factory=list)
    empty: bool = False


@dataclass
class ExcelValidationResult:
    filename: str
    sheet_summaries: List[SheetSummary]

    @property
    def has_issue(self) -> bool:
        return any(summary.empty or summary.missing_required_columns for summary in self.sheet_summaries)


class ExcelSpecValidator:
    """Validate uploaded Excel files for basic sanity checks."""

    def __init__(self, required_columns: Sequence[str] | None = None) -> None:
        self.required_columns = [col.strip() for col in required_columns or [] if col.strip()]

    def validate_files(self, uploaded_files: Sequence) -> List[ExcelValidationResult]:
        results: List[ExcelValidationResult] = []
        for file in uploaded_files:
            try:
                content = file.getvalue()
            except AttributeError:
                content = file.read()
            data = BytesIO(content)
            excel = pd.ExcelFile(data)
            summaries: List[SheetSummary] = []
            for sheet_name in excel.sheet_names:
                df = excel.parse(sheet_name)
                missing_cols = [col for col in self.required_columns if col not in df.columns]
                summaries.append(
                    SheetSummary(
                        name=sheet_name,
                        rows=int(df.shape[0]),
                        columns=int(df.shape[1]),
                        missing_required_columns=missing_cols,
                        empty=df.empty,
                    )
                )
            results.append(ExcelValidationResult(filename=file.name, sheet_summaries=summaries))
        return results
