
import matplotlib.pyplot as plt
import numpy as np

from solarhouse.thermal_element import ThermalElement
from solarhouse.thermal_model import ThermalModel


alpha_out = 1/0.04
alpha_windows = 1 / 0.52

mass = ThermalElement(
    name='mass',
    temp0=20,
    density=997,
    heat_capacity=4183,
    volume=0.001
)

outside = ThermalElement(
    name='outside',
    temp0=18,
    area_inside=0.06,
    input_alpha=alpha_out
)

mass.branches_loss =[outside]

mass_model = ThermalModel(name='power_to_mass')
mass_model.elements = {
    'mass': mass,
    'outside': outside
}
mass_model.start_element = mass
mass_model.outside_elements = [outside]
mass_model.initial_conditions = {
    'mass': 20,

}
mass_model.plots = [mass]
power = 50
seconds = 60 * 60
dt = 10
count = int(seconds / dt)

mass_model.start(count, dt, power, t_out=15)

print(mass.temp)

