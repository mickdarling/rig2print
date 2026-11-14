"""Offline checks for tracked repository data; not Dollhouse server validation."""

import json
from pathlib import Path
import re


ELEMENT_TYPES = {"persona", "skill", "template", "agent", "memory", "ensemble"}
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


def identity(item):
    if not isinstance(item, dict):
        raise ValueError("element reference must be an object")
    kind, name = item.get("element_type"), item.get("element_name")
    if not isinstance(kind, str) or kind not in ELEMENT_TYPES:
        raise ValueError(f"unknown element type: {kind!r}")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("element_name must be a nonempty string")
    return kind, name


def validate_bundle(bundle):
    if not isinstance(bundle, dict) or bundle.get("format") != "rig2print-mcpaql-creation-manifest":
        raise ValueError("unexpected Dollhouse bundle format")
    if type(bundle.get("version")) is not int or bundle["version"] != 1:
        raise ValueError("unsupported Dollhouse bundle version")
    required, operations = bundle.get("requires"), bundle.get("operations")
    if not isinstance(required, list) or not isinstance(operations, list) or not operations:
        raise ValueError("bundle requires dependency and nonempty operation arrays")
    available = set()
    for item in required:
        key = identity(item)
        if key in available:
            raise ValueError(f"duplicate dependency: {key}")
        available.add(key)
    for operation in operations:
        if not isinstance(operation, dict) or operation.get("operation") != "create_element":
            raise ValueError("bundle permits only create_element operations")
        params = operation.get("params")
        if not isinstance(params, dict):
            raise ValueError("create_element requires params")
        key = identity({"element_type": operation.get("element_type"),
                        "element_name": params.get("element_name")})
        if key in available:
            raise ValueError(f"duplicate or dependency-overwriting definition: {key}")
        for field in ("description",):
            if not isinstance(params.get(field), str) or not params[field].strip():
                raise ValueError(f"{key}: {field} is required")
        kind = key[0]
        if kind in {"persona", "skill", "template", "agent"}:
            if not isinstance(params.get("instructions"), str) or not params["instructions"].strip():
                raise ValueError(f"{key}: instructions are required")
        if kind == "template":
            content, metadata = params.get("content"), params.get("metadata")
            if not isinstance(content, str) or not content.strip() or not isinstance(metadata, dict):
                raise ValueError(f"{key}: template content and metadata are required")
            variables = metadata.get("variables")
            if not isinstance(variables, list):
                raise ValueError(f"{key}: variables must be an array")
            names = []
            for variable in variables:
                if not isinstance(variable, dict) or not isinstance(variable.get("name"), str):
                    raise ValueError(f"{key}: variable requires a name")
                names.append(variable["name"])
            placeholders = set(re.findall(r"{{\s*([A-Za-z_]\w*)\s*}}", content))
            if len(set(names)) != len(names) or set(names) != placeholders:
                raise ValueError(f"{key}: template variables must match placeholders exactly")
        if kind == "ensemble":
            metadata = params.get("metadata")
            members = metadata.get("elements") if isinstance(metadata, dict) else None
            if not isinstance(members, list) or not members:
                raise ValueError(f"{key}: ensemble members are required")
            seen = set()
            for member in members:
                reference = identity(member)
                if reference not in available:
                    raise ValueError(f"{key}: unresolved or out-of-order member: {reference}")
                role = member.get("role")
                if not isinstance(role, str) or role not in ROLES:
                    raise ValueError(f"{key}: invalid ensemble role")
                if reference in seen:
                    raise ValueError(f"{key}: duplicate ensemble member: {reference}")
                seen.add(reference)
        available.add(key)


def check_json_files(root, paths):
    count = 0
    for relative in paths:
        path = Path(relative)
        if path.suffix != ".json":
            continue
        document = strict_json((root / path).read_text(encoding="utf-8"))
        if path.as_posix() == "dollhouse/bundle.json":
            validate_bundle(document)
        count += 1
    return count
