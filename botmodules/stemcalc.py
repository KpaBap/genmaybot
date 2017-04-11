import re
import math as notmath


def call_stemcalc(self, e):
    calculator = StemCalc(e.input)
    e.output = e.nick + ', ' + calculator.solve()
    return e
call_stemcalc.command = "!stemcalc"


class StemCalc:
    headtube = 72.5
    stem_height = 40

    parameter_meta_data = {
        'first_stem': {
            'name': 'First Stem',
            'examples': ['100/-6/20', '110/6/10', '100/-17/0/42']
        },
        'second_stem': {
            'name': 'Second Stem',
            'examples': ['length/angle/stack[/stem height = 40]']
        },
        'headtube': {
            'name': 'Head Tube',
            'examples': ['72.5', '73']
        }
    }

    def __init__(self, calc_string):
        self.tokens = self.tokenize(calc_string)
        self.first_stem = self.find_stem(0)
        self.second_stem = self.find_stem(1)
        self.headtube = self.find_headtube()

    def get_parameter_meta_data(self, parameter, data_type):
        return self.parameter_meta_data[parameter][data_type]

    def get_list_meta_data_from_parameters(self, parameters, data_type):
        return_list = []
        for parameter in parameters:
            value = self.get_parameter_meta_data(parameter, data_type)
            if value is not None:
                if type(value) is list:
                    for item in value:
                        return_list.append(item)
                else:
                    return_list.append(value)
        return return_list

    @staticmethod
    def tokenize(calc_string):
        return re.split('\s', calc_string)

    def solve(self):
        if self.first_stem and self.second_stem:
            reach_change = self.compare_reach(self.first_stem, self.second_stem)
            text = ''
            if reach_change > 0:
                text += str(abs(reach_change)) + 'mm more reach'
            elif reach_change < 0:
                text += str(abs(reach_change)) + 'mm less reach'
            else:
                text += 'No change in reach'
            text += ' and '
            stack_change = self.compare_stack(self.first_stem, self.second_stem)
            if stack_change > 0:
                text += str(abs(stack_change)) + 'mm more stack'
            elif stack_change < 0:
                text += str(abs(stack_change)) + 'mm less stack'
            else:
                text += 'no change in stack'
            return text
        else:
            text = "I need more information try some of the following: "
            text += ', '.join(str(v) for v in self.get_list_meta_data_from_parameters(
                self.find_missing_parameters(),
                'name'
            ))
            text += ' '
            text += 'Eg.) '
            text += ', '.join(str(v) for v in self.get_list_meta_data_from_parameters(
                self.find_missing_parameters(),
                'examples'
            ))
            return text

    def find_missing_parameter(self):
        missing_parameters = self.find_missing_parameters()
        if missing_parameters:
            return missing_parameters.pop(0)

    def find_missing_parameters(self):
        missing_parameters = []
        object_values = vars(self)
        for key in object_values:
            if object_values[key] is None and key != 'metric':
                missing_parameters.append(key)
        return missing_parameters

    def find_headtube(self):
        for token in self.tokens:
            try:
                return float(token)
            except ValueError:
                continue
        return self.headtube

    def find_stem(self, offset):
        stems = []
        for token in self.tokens:
            m = re.match(r"^(\d+)/([+-]?\d+)/(\d+)/?(\d+)?$", token)
            if m:
                stem = {
                    'length': int(m.group(1)),
                    'angle': float(m.group(2)),
                    'spacers': int(m.group(3))
                }
                if m.group(4):
                    stem['stem_height'] = int(m.group(4))
                else:
                    stem['stem_height'] = int(self.stem_height)
                stems.append(stem)
        try:
            return stems[offset]
        except IndexError:
            return None

    def compare_reach(self, stem1, stem2):
        return round(self.calculate_reach(stem2) - self.calculate_reach(stem1), 1)

    def compare_stack(self, stem1, stem2):
        return round(self.calculate_stack(stem2) - self.calculate_stack(stem1), 1)

    def calculate_reach(self, stem):
        stem_radians = self.calculate_stem_radians(stem)
        reach = stem['length'] * notmath.cos(stem_radians)
        return reach + self.calculate_spacer_reach_adjustment(stem)

    def calculate_stack(self, stem):
        stem_radians = self.calculate_stem_radians(stem)
        stack = stem['length'] * notmath.sin(stem_radians)
        return stack + self.calculate_spacer_stack_adjustment(stem)

    def calculate_stem_radians(self, stem):
        stem_degrees = float(90) - self.headtube + stem['angle']
        stem_radians = notmath.radians(stem_degrees)
        return stem_radians

    def calculate_spacer_reach_adjustment(self, stem):
        if stem['spacers']:
            spacer_stem = {
                'length': stem['spacers'] + (stem['stem_height'] / 2),
                'angle': 90.0 - self.headtube,
                'spacers': 0
            }
            spacer_stem_adjustment = self.calculate_stack(spacer_stem)
            return -1 * spacer_stem_adjustment
        else:
            return 0

    def calculate_spacer_stack_adjustment(self, stem):
        if stem['spacers']:
            spacer_stem = {
                'length': stem['spacers'] + (stem['stem_height'] / 2),
                'angle': 90.0 - self.headtube,
                'spacers': 0
            }
            spacer_stem_adjustment = self.calculate_reach(spacer_stem)
            return spacer_stem_adjustment
        else:
            return 0
