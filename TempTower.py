# -*- coding: utf-8 -*-

import json
import re

from ..Script import Script


class TempTower(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return json.dumps({
            'name': 'Temp Tower',
            'key': 'TempTower',
            'metadata': {},
            'version': 2,
            'settings': {
                'start_temperature': {
                    'label': 'Start Temperature',
                    'description': 'Initial nozzle temperature',
                    'unit': '°C',
                    'type': 'int',
                    'default_value': 265
                },
                'height_increment': {
                    'label': 'Height Increment',
                    'description': (
                        'Adjust temperature each time height param '
                        'changes by this much'
                    ),
                    'unit': 'mm',
                    'type': 'int',
                    'default_value': 10
                },
                'temperature_increment': {
                    'label': 'Temperature Increment',
                    'description': (
                        'Increase temperature by this much with each height increment. '
                        'Use negative values for towers that become gradually cooler.'
                    ),
                    'unit': '°C',
                    'type': 'int',
                    'default_value': -5
                },
                'start_height': {
                    'label': 'Start Height ',
                    'description': (
                        'Start the temperature tower at this height.'
                    ),
                    'unit': 'mm',
                    'type': 'float',
                    'default_value': 1.4
                }
            }
        })

    def execute(self, data):
        start_temp = self.getSettingValueByKey('start_temperature')
        height_inc = self.getSettingValueByKey('height_increment')
        temp_inc = self.getSettingValueByKey('temperature_increment')
        start_height = self.getSettingValueByKey('start_height')

        cmd_re = re.compile(
            r'G[0-9]+ '
            r'X[0-9]+\.?[0-9]* '
            r'Y[0-9]+\.?[0-9]* '
            r'Z(-?[0-9]+\.?[0-9]*)'
        )

        # Set initial state
        current_temp = 0
        started = False
        for i, layer in enumerate(data):
            lines = layer.split('\n')
            for j, line in enumerate(lines):
                # Before ;LAYER:0 arbitrary setup GCODE can be run.
                if line == ';LAYER:0':
                    started = True
                    continue

                # skip comments and startup lines
                if line.startswith(';') or not started:
                    continue

                # Find any X,Y,Z Line (ex. G0 X60.989 Y60.989 Z1.77)
                match = cmd_re.match(line)
                if match is None:
                    continue
                z = float(match.groups()[0])
				
                if z < start_height:
                    continue
				
                new_temp = start_temp + int((z - start_height) / height_inc) * temp_inc

                if new_temp != current_temp:
                    current_temp = new_temp
                    lines[j] += '\n;TYPE:CUSTOM\nM104 S%d' % new_temp
            data[i] = '\n'.join(lines)

        return data
