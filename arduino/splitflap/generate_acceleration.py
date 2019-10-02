#!/usr/bin/env python
#   Copyright 2017 Scott Bezek and the splitflap contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os

import subprocess

MIN_PERIOD_MICROS = 1200
MAX_PERIOD_MICROS = 20000
ACCEL_TIME_MICROS = 200000
IDLE_PERIOD_MICROS = 1200

_TEMPLATE = """/*
   Copyright 2017 Scott Bezek and the splitflap contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

// NOTE: THIS FILE IS AUTOGENERATED! DO NOT MODIFY!
// To update, run `{script_path}`

#ifndef ACCELERATION
#define ACCELERATION

namespace Acceleration {{
    const PROGMEM uint16_t ACCEL_STEP_PERIODS[] = {{{periods_array}}};
    const uint8_t MAX_ACCEL_STEP = {max_accel_step};
}}
#endif
"""


def run(output_file_path):
    min_velocity = 1000000 / float(MAX_PERIOD_MICROS)
    max_velocity = 1000000 / float(MIN_PERIOD_MICROS)

    t = 0
    ramp_periods = [IDLE_PERIOD_MICROS]
    while t < ACCEL_TIME_MICROS:
        velocity = min_velocity + (max_velocity - min_velocity) * float(t) / ACCEL_TIME_MICROS
        if velocity > max_velocity:
            velocity = max_velocity

        period = int(1000000 / velocity)
        
        ramp_periods.append(period)
        t += period
    assert len(ramp_periods) <= 255, 'number of ramp periods would exceed a uint8_t'

    git_root = subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    ).strip()
    script_path = os.path.relpath(os.path.abspath(__file__), os.path.abspath(git_root))
    with open(output_file_path, 'wb') as f:
        f.write(_TEMPLATE.format(
            periods_array=', '.join([str(x) for x in ramp_periods]),
            max_accel_step=len(ramp_periods) - 1,
            script_path=script_path,
        ))


if __name__ == '__main__':
    output_file_path = os.path.join(os.path.dirname(__file__), 'acceleration.h')
    run(
        output_file_path,
    )
