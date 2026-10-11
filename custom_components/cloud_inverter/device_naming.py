"""Short, stable, privacy-safe names for configured inverters."""

from __future__ import annotations

from collections.abc import Iterable

from .const import CONF_DEVICE_LABEL


def device_labels(entries: Iterable[object]) -> dict[str, str]:
    """Assign missing labels deterministically without exposing device IDs."""
    ordered = sorted(entries, key=lambda entry: entry.entry_id)
    labels = {
        entry.entry_id: entry.data[CONF_DEVICE_LABEL]
        for entry in ordered
        if entry.data.get(CONF_DEVICE_LABEL)
    }
    used = set(labels.values())
    number = 1
    for entry in ordered:
        if entry.entry_id in labels:
            continue
        while f"Solar Touch {number}" in used:
            number += 1
        label = f"Solar Touch {number}"
        labels[entry.entry_id] = label
        used.add(label)
    return labels


def next_device_label(entries: Iterable[object]) -> str:
    """Choose a label for a newly configured inverter."""
    used = set(device_labels(entries).values())
    number = 1
    while f"Solar Touch {number}" in used:
        number += 1
    return f"Solar Touch {number}"
