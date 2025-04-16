#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import pathlib
import ops

import workload


class MyCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.tracing = ops.tracing.Tracing(self, "charm-tracing", ca_relation_name="receive-ca-cert")
        self.framework.observe(self.on.workload_pebble_ready, self._on_pebble_ready)

    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        container = self.unit.get_container("workload")

        container.exec(["apt-get", "update"], environment={"DEBIAN_FRONTEND": "noninteractive"}).wait()
        container.exec(["apt-get", "install", "-y", "python3"], environment={"DEBIAN_FRONTEND": "noninteractive"}).wait()
        script = pathlib.Path(workload.__file__).read_text()
        container.push("/tmp/workload.py", script, make_dirs=True, permissions=0o755)

        layer = {
            "summary": "Showcase hot to tail workload logs",
            "description": "Showcase hot to tail workload logs",
            "services": {
                "workload": {
                    "override": "replace",
                    "summary": "A workload",
                    "command": "/tmp/workload.py",
                    "startup": "enabled",
                    "requires": ["workload-access-log", "workload-error-log", "workload-audit-log"],
                },
                "workload-access-log": {
                    "override": "replace",
                    "summary": "Tail access log",
                    "command": "tail -F /tmp/access.log",
                    "startup": "enabled",
                },
                "workload-error-log": {
                    "override": "replace",
                    "summary": "Tail error log",
                    "command": "tail -F /tmp/error.log",
                    "startup": "enabled",
                },
                "workload-audit-log": {
                    "override": "replace",
                    "summary": "Tail audit log",
                    "command": "tail -F /tmp/audit.log",
                    "startup": "enabled",
                },
            },
        }
        container.add_layer("workload-layer", layer, combine=True)  # type: ignore
        container.autostart()

if __name__ == "__main__":
    ops.main(MyCharm)
