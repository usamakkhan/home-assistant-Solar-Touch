"""Check labels stay distinct when several inverters are configured."""

import importlib
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys
import unittest


component = Path(__file__).resolve().parents[1] / "custom_components" / "cloud_inverter"
package = sys.modules.setdefault("cloud_inverter", ModuleType("cloud_inverter"))
package.__path__ = [str(component)]
naming = importlib.import_module("cloud_inverter.device_naming")


def entry(entry_id, label=None):
    data = {} if label is None else {"device_label": label}
    return SimpleNamespace(entry_id=entry_id, data=data)


class DeviceNamingTests(unittest.TestCase):
    def test_existing_entries_get_stable_short_labels(self):
        entries = [entry("second"), entry("first")]
        self.assertEqual(naming.device_labels(entries), {
            "first": "ST 1", "second": "ST 2"
        })
        self.assertEqual(naming.next_device_label(entries), "ST 3")

    def test_persisted_labels_do_not_change_after_new_entry(self):
        entries = [entry("second"), entry("first", "ST 1")]
        self.assertEqual(naming.device_labels(entries)["second"], "ST 2")
        self.assertEqual(naming.next_device_label(entries), "ST 3")

    def test_old_generated_names_migrate_without_changing_custom_names(self):
        entries = [entry("first", "Solar Touch 1"), entry("second", "Roof inverter")]
        self.assertEqual(naming.device_labels(entries), {
            "first": "ST 1", "second": "Roof inverter"
        })
        self.assertEqual(naming.next_device_label(entries), "ST 2")


if __name__ == "__main__":
    unittest.main()
