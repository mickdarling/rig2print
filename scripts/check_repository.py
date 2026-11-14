"""Offline checks for tracked repository data; not Dollhouse server validation."""

import json
from pathlib import Path
import re


ROLES = {"primary", "support", "override", "monitor", "core"}


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"non-finite JSON constant: {value}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)



FOLDERS = {"personas": "persona", "skills": "skill", "templates": "template", "ensembles": "ensemble"}


def read_element(path):
    import yaml

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError(f"duplicate YAML key: {key}")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"{path}: missing Markdown YAML frontmatter")
    header, body = text[4:].split("\n---\n", 1)
    try:
        metadata = yaml.load(header, Loader=UniqueLoader)
    except (yaml.YAMLError, TypeError) as error:
        raise ValueError(f"{path}: invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict) or not body.strip():
        raise ValueError(f"{path}: metadata mapping and nonempty Markdown body required")
    return metadata, body


def validate_elements(documents):
    available = set()
    for relative, (metadata, body) in documents.items():
        path = Path(relative)
        kind = FOLDERS.get(path.parent.name)
        if kind is None or metadata.get("type") != kind:
            raise ValueError(f"{path}: type must match its portfolio folder")
        name = metadata.get("name")
        if not isinstance(name, str) or name != path.stem or not re.fullmatch(r"[a-z][a-z0-9-]{0,99}", name):
            raise ValueError(f"{path}: name must match its filename and use kebab-case")
        for field in ("description", "version"):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                raise ValueError(f"{path}: {field} is required")
        if metadata.get("format_version") != "v2":
            raise ValueError(f"{path}: native v2 format marker required")
        key = kind, name
        if key in available:
            raise ValueError(f"duplicate element: {key}")
        available.add(key)
        if kind == "skill" and (not isinstance(metadata.get("instructions"), str) or not metadata["instructions"].strip()):
            raise ValueError(f"{path}: skill instructions are required")
        if kind == "template":
            variables = metadata.get("variables")
            if not isinstance(variables, list) or not variables:
                raise ValueError(f"{path}: top-level template variables are required")
            names = []
            for variable in variables:
                if not isinstance(variable, dict) or not isinstance(variable.get("name"), str):
                    raise ValueError(f"{path}: invalid template variable")
                names.append(variable["name"])
            placeholders = set(re.findall(r"{{\s*([A-Za-z_]\w*)\s*}}", body))
            if len(set(names)) != len(names) or set(names) != placeholders:
                raise ValueError(f"{path}: template variables must match placeholders exactly")
    for relative, (metadata, _) in documents.items():
        if metadata["type"] != "ensemble":
            continue
        members = metadata.get("elements")
        if not isinstance(members, list) or not members:
            raise ValueError(f"{relative}: native top-level elements array required")
        seen = set()
        for member in members:
            if not isinstance(member, dict):
                raise ValueError(f"{relative}: invalid ensemble member")
            kind, name = member.get("element_type"), member.get("element_name")
            if not isinstance(kind, str) or not isinstance(name, str) or (kind, name) not in available:
                raise ValueError(f"{relative}: unresolved ensemble member: {kind!r}/{name!r}")
            if not isinstance(member.get("role"), str) or member["role"] not in ROLES:
                raise ValueError(f"{relative}: invalid ensemble role")
            if (kind, name) in seen:
                raise ValueError(f"{relative}: duplicate ensemble member")
            seen.add((kind, name))


def check_markdown_elements(root, paths):
    if (root / "dollhouse/bundle.json").exists():
        raise ValueError("Dollhouse elements must be separate native Markdown files, not bundle.json")
    documents = {path: read_element(root / path) for path in paths
                 if path.startswith("dollhouse/portfolio/") and path.endswith(".md")}
    if not documents:
        raise ValueError("native Dollhouse Markdown elements are missing")
    validate_elements(documents)
    return len(documents)


def check_json_files(root, paths):
    count = 0
    for relative in paths:
        path = Path(relative)
        if path.suffix == ".json":
            strict_json((root / path).read_text(encoding="utf-8"))
            count += 1
    return count
