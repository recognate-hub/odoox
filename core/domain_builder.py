"""
Strongly-typed Odoo domain builder.

Replaces raw ``list[Any]`` domain construction with a fluent,
compile-time-safe API that serialises to the Polish-notation lists
Odoo's XML-RPC ``search_read`` / ``search`` endpoints expect.

Usage::

    domain = (
        Domain()
        .eq("type", "opportunity")
        .ilike("name", "Acme")
        .build()
    )
    # => [["type", "=", "opportunity"], ["name", "ilike", "Acme"]]

    domain = (
        Domain()
        .or_(
            Domain().ilike("name", "widget"),
            Domain().ilike("default_code", "widget"),
        )
        .build()
    )
    # => ["|", ["name", "ilike", "widget"], ["default_code", "ilike", "widget"]]
"""

from __future__ import annotations

from typing import Any

# Allowed Odoo comparison operators (exhaustive list)
type OdooOperator = str  # One of the values below at runtime

_VALID_OPERATORS: frozenset[str] = frozenset({
    "=", "!=", ">", ">=", "<", "<=",
    "=like", "like", "not like",
    "=ilike", "ilike", "not ilike",
    "in", "not in",
    "child_of", "parent_of",
    "=?",
})


class DomainLeaf:
    """A single ``[field, operator, value]`` triple."""

    __slots__ = ("field", "operator", "value")

    def __init__(self, field: str, operator: str, value: Any) -> None:
        if operator not in _VALID_OPERATORS:
            raise ValueError(
                f"Invalid Odoo domain operator '{operator}'. "
                f"Must be one of: {', '.join(sorted(_VALID_OPERATORS))}"
            )
        self.field = field
        self.operator = operator
        self.value = value

    def serialise(self) -> list[Any]:
        """Return the standard Odoo triple."""
        return [self.field, self.operator, self.value]


class Domain:
    """
    Fluent builder for Odoo search domains.

    All filter methods return ``self`` so calls can be chained.
    The final domain is obtained via :meth:`build`.
    """

    def __init__(self) -> None:
        # Internal list of leaves *or* raw prefix-notation tokens
        self._parts: list[DomainLeaf | str | list[Any]] = []

    # ── comparison helpers ──────────────────────────────────────────

    def _add(self, field: str, operator: str, value: Any) -> Domain:
        self._parts.append(DomainLeaf(field, operator, value))
        return self

    def eq(self, field: str, value: Any) -> Domain:
        """``field = value``"""
        return self._add(field, "=", value)

    def neq(self, field: str, value: Any) -> Domain:
        """``field != value``"""
        return self._add(field, "!=", value)

    def gt(self, field: str, value: Any) -> Domain:
        """``field > value``"""
        return self._add(field, ">", value)

    def gte(self, field: str, value: Any) -> Domain:
        """``field >= value``"""
        return self._add(field, ">=", value)

    def lt(self, field: str, value: Any) -> Domain:
        """``field < value``"""
        return self._add(field, "<", value)

    def lte(self, field: str, value: Any) -> Domain:
        """``field <= value``"""
        return self._add(field, "<=", value)

    def ilike(self, field: str, value: str) -> Domain:
        """Case-insensitive pattern match."""
        return self._add(field, "ilike", value)

    def like(self, field: str, value: str) -> Domain:
        """Case-sensitive pattern match."""
        return self._add(field, "like", value)

    def not_ilike(self, field: str, value: str) -> Domain:
        """Negated case-insensitive pattern match."""
        return self._add(field, "not ilike", value)

    def in_(self, field: str, values: list[Any]) -> Domain:
        """``field in [...]``"""
        return self._add(field, "in", values)

    def not_in(self, field: str, values: list[Any]) -> Domain:
        """``field not in [...]``"""
        return self._add(field, "not in", values)

    def child_of(self, field: str, value: int) -> Domain:
        """Hierarchical ``child_of``."""
        return self._add(field, "child_of", value)

    def parent_of(self, field: str, value: int) -> Domain:
        """Hierarchical ``parent_of``."""
        return self._add(field, "parent_of", value)

    # ── logical combinators ─────────────────────────────────────────

    @staticmethod
    def or_(*domains: Domain) -> Domain:
        """
        Combine multiple sub-domains with ``|`` (OR).

        Each sub-domain is serialised and wrapped with the correct
        number of ``|`` prefix tokens for Polish notation.
        """
        if len(domains) < 2:
            raise ValueError("or_() requires at least 2 sub-domains")

        merged = Domain()
        # n sub-domains need (n - 1) OR operators prepended
        for _ in range(len(domains) - 1):
            merged._parts.append("|")
        for d in domains:
            merged._parts.extend(d._parts)
        return merged

    @staticmethod
    def and_(*domains: Domain) -> Domain:
        """
        Combine multiple sub-domains with ``&`` (AND).

        In Odoo, consecutive leaves are implicitly AND-ed,
        but explicit ``&`` is needed when nesting inside ``or_``.
        """
        if len(domains) < 2:
            raise ValueError("and_() requires at least 2 sub-domains")

        merged = Domain()
        for _ in range(len(domains) - 1):
            merged._parts.append("&")
        for d in domains:
            merged._parts.extend(d._parts)
        return merged

    def not_(self) -> Domain:
        """Negate the entire current domain with ``!``."""
        negated = Domain()
        negated._parts.append("!")
        negated._parts.extend(self._parts)
        return negated

    # ── serialisation ───────────────────────────────────────────────

    def build(self) -> list[Any]:
        """
        Serialise to the list format Odoo expects.

        Returns an empty list if no filters have been added,
        which Odoo interprets as *match all records*.
        """
        result: list[Any] = []
        for part in self._parts:
            if isinstance(part, DomainLeaf):
                result.append(part.serialise())
            elif isinstance(part, str):
                # Prefix operator: "|", "&", "!"
                result.append(part)
            else:
                # Already-serialised raw list (escape hatch)
                result.append(part)
        return result

    def __len__(self) -> int:
        return len(self._parts)

    def __bool__(self) -> bool:
        return len(self._parts) > 0

    def __repr__(self) -> str:
        return f"Domain({self.build()!r})"
