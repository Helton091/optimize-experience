from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = PACKAGE_ROOT / "knowledge"
REQUIRED = {
    "type", "title", "description", "tags", "status", "sources",
    "created_at", "updated_at", "platforms",
}
OPTIONAL = {"cann_versions", "aliases", "verified", "replaced_by"}
ROLES = {"primary", "supporting", "example", "constraint", "header", "implementation", "evidence"}
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")


@dataclass
class Card:
    path: Path
    concept: str
    meta: dict
    body: str


def parse_time(value, label, errors):
    if not isinstance(value, str):
        errors.append(f"{label} must be an RFC3339 string")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        errors.append(f"{label} must use YYYY-MM-DDTHH:MM:SSZ")
        return None


def parse_card(path: Path) -> Card:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0] != "---":
        raise ValueError("missing frontmatter opening")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing frontmatter closing") from exc
    meta = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.+)", line)
        if not match:
            raise ValueError(f"frontmatter value must be one-line JSON: {line}")
        key, raw = match.groups()
        if key in meta:
            raise ValueError(f"duplicate frontmatter key: {key}")
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON value for {key}: {raw}") from exc
    concept = path.relative_to(KNOWLEDGE_ROOT).with_suffix("").as_posix()
    return Card(path, concept, meta, "\n".join(lines[end + 1:]))


def load_cards(knowledge_root: Path = KNOWLEDGE_ROOT) -> list[Card]:
    paths = sorted(
        path for path in knowledge_root.rglob("*.md")
        if path.is_file() and path.name != "index.md"
    )
    return [parse_card(path) for path in paths]


def validate_source(source, errors):
    if not isinstance(source, dict) or set(source) - {"resource", "role"}:
        errors.append("source must contain only resource and optional role")
        return
    resource = source.get("resource")
    if not isinstance(resource, str) or not resource:
        errors.append("source.resource must be non-empty")
        return
    parsed = urlparse(resource)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"source must be a public HTTPS URL: {resource}")
    if source.get("role", "evidence") not in ROLES:
        errors.append(f"unknown source role: {source.get('role')}")
    git_hosts = {"atomgit.com", "gitcode.com", "github.com"}
    if parsed.hostname in git_hosts:
        match = re.search(r"/(?:blob|tree)/([^/]+)/", parsed.path)
        if match and not re.fullmatch(r"[0-9a-f]{40}", match.group(1)):
            errors.append(f"Git source must use a 40-character commit: {resource}")


def validate_card(card: Card, concepts: set[str], aliases: dict[str, str]) -> list[str]:
    errors = []
    meta = card.meta
    prefix = card.concept
    missing = REQUIRED - set(meta)
    unknown = set(meta) - REQUIRED - OPTIONAL
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if unknown:
        errors.append(f"unknown fields: {sorted(unknown)}")
    expected_type = "Optimization" if card.path.parent.relative_to(KNOWLEDGE_ROOT).parts[0] == "optimizations" else "Runbook"
    if meta.get("type") != expected_type:
        errors.append(f"type must be {expected_type}")
    for field in ("title", "description"):
        if not isinstance(meta.get(field), str) or not meta.get(field, "").strip():
            errors.append(f"{field} must be non-empty")
    tags = meta.get("tags")
    if not isinstance(tags, list) or not 2 <= len(tags) <= 6 or len(set(tags)) != len(tags):
        errors.append("tags must contain 2-6 unique values")
    elif not any(tag.startswith("task.") for tag in tags) or not any(tag.startswith("topic.") for tag in tags):
        errors.append("tags need task.* and topic.*")
    status = meta.get("status")
    if status not in {"draft", "stable", "deprecated"}:
        errors.append("invalid status")
    sources = meta.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    for source in sources:
        validate_source(source, errors)
    if status == "stable" and expected_type == "Optimization" and not sources:
        errors.append("stable Optimization needs a public source")
    created = parse_time(meta.get("created_at"), "created_at", errors)
    updated = parse_time(meta.get("updated_at"), "updated_at", errors)
    if created and updated and updated < created:
        errors.append("updated_at predates created_at")
    platforms = meta.get("platforms")
    if not isinstance(platforms, list) or len(set(platforms)) != len(platforms):
        errors.append("platforms must be a unique array")
        platforms = []
    if set(platforms) - {"ascend910b", "agnostic"}:
        errors.append("unregistered platform")
    if "agnostic" in platforms and len(platforms) != 1:
        errors.append("agnostic cannot be mixed with a concrete platform")
    if status != "draft" and not platforms:
        errors.append("non-draft card needs a declared platform")
    for field in ("cann_versions", "aliases"):
        value = meta.get(field)
        if field in meta and (not isinstance(value, list) or not value or len(set(value)) != len(value)):
            errors.append(f"{field} must be a non-empty unique array when present")
    for alias in meta.get("aliases", []):
        if alias in aliases:
            errors.append(f"alias {alias} also used by {aliases[alias]}")
        else:
            aliases[alias] = card.concept
    replaced_by = meta.get("replaced_by")
    if status == "deprecated":
        if not replaced_by:
            errors.append("deprecated card needs replaced_by")
        elif replaced_by not in concepts or replaced_by == card.concept:
            errors.append("replaced_by must reference another existing Concept")
    elif replaced_by is not None:
        errors.append("replaced_by is only valid on deprecated cards")
    verified = meta.get("verified")
    if verified is not None:
        events = verified if isinstance(verified, list) else [verified]
        for event in events:
            if not isinstance(event, dict) or set(event) != {"by", "at"}:
                errors.append("verified event must contain by and at")
                continue
            if not isinstance(event["by"], str) or not event["by"]:
                errors.append("verified.by must be non-empty")
            parse_time(event["at"], "verified.at", errors)
    for target in LINK_RE.findall(card.body):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        raw = target.split("#", 1)[0]
        if not raw:
            continue
        if Path(raw).is_absolute() or "\\" in raw:
            errors.append(f"unsafe local link: {target}")
            continue
        resolved = (KNOWLEDGE_ROOT / raw.lstrip("/")) if raw.startswith("/") else (card.path.parent / raw)
        resolved = resolved.resolve()
        try:
            resolved.relative_to(KNOWLEDGE_ROOT.resolve())
        except ValueError:
            errors.append(f"link leaves knowledge bundle: {target}")
            continue
        if not resolved.is_file():
            errors.append(f"missing local link: {target}")
    return [f"{prefix}: {message}" for message in errors]


def validate_indexes(knowledge_root: Path = KNOWLEDGE_ROOT) -> list[str]:
    errors = []
    directories = sorted({path.parent for path in knowledge_root.rglob("*.md")} | {knowledge_root})
    for directory in directories:
        index = directory / "index.md"
        if not index.is_file():
            errors.append(f"missing index: {index.relative_to(knowledge_root)}")
            continue
        text = index.read_text(encoding="utf-8")
        targets = LINK_RE.findall(text)
        actual = []
        for target in targets:
            raw = target.split("#", 1)[0]
            if not raw or raw.startswith(("https://", "http://")):
                continue
            actual.append((directory / raw).resolve())
        expected = []
        expected.extend(path.resolve() for path in directory.glob("*.md") if path.name != "index.md")
        for child in directory.iterdir():
            if child.is_dir() and any(child.rglob("*.md")):
                expected.append((child / "index.md").resolve())
        for path in expected:
            if actual.count(path) != 1:
                errors.append(f"{index.relative_to(knowledge_root)} must link {path.name} exactly once")
        for path in actual:
            if path not in expected:
                errors.append(f"{index.relative_to(knowledge_root)} links non-direct or unknown item: {path}")
    return errors


def validate_bundle(knowledge_root: Path = KNOWLEDGE_ROOT) -> tuple[list[Card], list[str]]:
    cards = load_cards(knowledge_root)
    concepts = {card.concept for card in cards}
    if len(concepts) != len(cards):
        raise ValueError("duplicate Concept ID")
    errors = []
    aliases = {}
    for card in cards:
        errors.extend(validate_card(card, concepts, aliases))
    errors.extend(validate_indexes(knowledge_root))
    return cards, errors


def search_cards(cards: list[Card], query: str, filters: dict | None = None) -> list[dict]:
    filters = filters or {}
    status = filters.get("status", "stable")
    results = []
    terms = [term.lower() for term in re.split(r"\s+", query.strip()) if term]
    for card in cards:
        if filters.get("type") and card.concept.split("/")[0] != filters["type"]:
            continue
        if status != "all" and card.meta["status"] != status:
            continue
        platform = filters.get("platform")
        if platform and platform not in card.meta["platforms"] and "agnostic" not in card.meta["platforms"]:
            continue
        title = card.meta["title"].lower()
        description = card.meta["description"].lower()
        tags = " ".join(card.meta["tags"]).lower()
        aliases = " ".join(card.meta.get("aliases", [])).lower()
        body = card.body.lower()
        concept = card.concept.lower()
        score = 0
        for term in terms:
            if term == title:
                score += 100
            elif term in title:
                score += 30
            if term in aliases:
                score += 40
            if term in tags:
                score += 20
            if term in description:
                score += 15
            if term in concept:
                score += 8
            if term in body:
                score += 5
        if score:
            results.append({"concept": card.concept, "title": card.meta["title"], "score": score})
    results.sort(key=lambda item: (-item["score"], item["concept"]))
    return results[:filters.get("k", 5)]
