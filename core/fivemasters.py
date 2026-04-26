from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FiveMastersReport:
    korotkevich: bool
    torvalds: bool
    carmack: bool
    hamilton: bool
    ritchie: bool

    def score(self) -> int:
        return sum([
            self.korotkevich,
            self.torvalds,
            self.carmack,
            self.hamilton,
            self.ritchie,
        ])


def evaluate_code(code: str) -> FiveMastersReport:
    """
    Lightweight heuristic evaluator.
    Replace later with AST-based analysis.
    """

    korotkevich = "for i in range(len" not in code  # crude inefficiency flag
    torvalds = "except:" not in code  # unsafe exception handling check
    carmack = "O(" not in code or "naive" not in code  # placeholder heuristic
    hamilton = "try:" in code or "raise" in code
    ritchie = "magic" not in code.lower()

    return FiveMastersReport(
        korotkevich=korotkevich,
        torvalds=torvalds,
        carmack=carmack,
        hamilton=hamilton,
        ritchie=ritchie,
    )