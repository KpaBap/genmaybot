import re
import math

def call_gearcalc(self, e):
	calculator = GearCalc(e.input)
	e.output = e.nick + ', ' + calculator.solve()
	return e
call_gearcalc.command = "!gearcalc"

class GearCalc:

	default_wheel_circumference = 2098
	mps_to_mph = 2.23694
	mps_to_kph = 3.6
	mps_constant = 0.000016674592
	mph_to_mps = 0.44704
	kph_to_mps = 0.27778
	parameter_meta_data = {
		'cadence': {
			'name': 'Cadence',
			'examples': ['90rpm']
		},
		'speed': {
			'name': 'Speed',
			'examples': ['20mph', '32kph', '9mps']
		},
		'front_teeth': {
			'name': 'Chainring Size',
			'examples': ['53x11', '50x?']
		},
		'rear_teeth': {
			'name': 'Cog Size',
			'examples': ['53x11', '?x11']
		}
	}

	def __init__(self, calc_string):
		self.tokens = self.tokenize(calc_string)
		self.cadence = self.find_cadence()
		self.speed = self.find_speed()
		self.front_teeth = self.find_front_teeth()
		self.rear_teeth = self.find_rear_teeth()
		self.wheel_circumference = self.find_erto()
		self.metric = self.find_metric()

	def get_parameter_meta_data(self, parameter, data_type):
		return self.parameter_meta_data[parameter][data_type]

	def get_list_metadata_from_parameters(self, parameters, data_type):
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
		if self.is_already_solved():
			return "You already know your answer, think about it."
		elif self.is_solvable():
			solution_parameter = self.find_missing_parameter()
			if solution_parameter == 'cadence':
				return self.solve_cadence()
			elif solution_parameter == 'speed':
				return self.solve_speed()
			elif solution_parameter == 'front_teeth':
				return self.solve_front_teeth()
			elif solution_parameter == 'rear_teeth':
				return self.solve_rear_teeth()
			else:
				return "Sorry I can't yet solve for " + self.get_parameter_meta_data(solution_parameter, 'name')
		else:
			return "I need more information try some of the following: " + ', '.join(str(v) for v in self.get_list_metadata_from_parameters(self.find_missing_parameters(), 'name')) + " Eg.) " + ', '.join(str(v) for v in self.get_list_metadata_from_parameters(self.find_missing_parameters(), 'examples'))

	def solve_cadence(self):
		try:
			return str(round(self.speed / (self.mps_constant * self.wheel_circumference * self.solve_gear_ratio()), 1)) + ' rpm'
		except ZeroDivisionError:
			return "nice try, trying to divide by zero are you?"

	def solve_speed(self):
		mps = self.mps_constant * self.wheel_circumference * self.solve_gear_ratio() * self.cadence
		if self.metric: 
			return str(round(mps * self.mps_to_kph, 1)) + ' kph'
		else:
			return str(round(mps * self.mps_to_mph, 1)) + ' mph'

	def solve_front_teeth(self):
		try:
			return str(int(round(self.speed / (self.mps_constant * self.wheel_circumference * self.cadence)) * (self.rear_teeth))) + ' tooth chainring'
		except ZeroDivisionError:
			return "nice try, trying to divide by zero are you?"


	def solve_rear_teeth(self):
		try:
			return str(int(round((self.mps_constant * self.wheel_circumference * self.cadence * self.front_teeth) / (self.speed)))) + ' tooth cog'
		except ZeroDivisionError:
			return "nice try, trying to divide by zero are you?"

	def solve_gear_ratio(self):
		try:
			return self.front_teeth / self.rear_teeth
		except ZeroDivisionError:
			return "nice try, trying to divide by zero are you?"

	def is_solvable(self):
		missing_parameters = self.find_missing_parameters()
		if len(missing_parameters) == 1:
			return True
		else:
			return False

	def is_already_solved(self):
		missing_parameters = self.find_missing_parameters()
		if len(missing_parameters) == 0:
			return True
		else:
			return False

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


	def find_cadence(self):
		for token in self.tokens:
			m = re.match(r"^(\d+)rpm$", token)
			if m:
				return int(m.group(1))

	def find_speed(self):
		for token in self.tokens:
			m = re.match(r"^([\d.]+)mph$", token)
			if m:
				return float(m.group(1)) * self.mph_to_mps
			m = re.match(r"^([\d.]+)kph$", token)
			if m:
				return float(m.group(1)) * self.kph_to_mps
			m = re.match(r"^([\d.]+)mps$", token)
			if m:
				return float(m.group(1))

	def find_front_teeth(self):
		for token in self.tokens:
			m = re.match(r"^([\d\?]+)x[\d\?]+$", token)
			if m and m.group(1) != '?':
				return int(m.group(1))

	def find_rear_teeth(self):
		for token in self.tokens:
			m = re.match(r"^[\d\?]+x([\d\?]+)$", token)
			if m and m.group(1) != '?':
				return int(m.group(1))

	def find_metric(self):
		for token in self.tokens:
			m = re.match(r"^metric$", token)
			if m:
				return True

	def find_erto(self):
		for token in self.tokens:
			m = re.match(r"^(\d{2})-(\d{3})$", token)
			if m:
				return self.calculate_ertro(int(m.group(1)), int(m.group(2)))
		return self.default_wheel_circumference

	@staticmethod
	def calculate_ertro(tire_width, rim_diameter):
		return int(round(float(rim_diameter + (tire_width * 2)) * math.pi))
