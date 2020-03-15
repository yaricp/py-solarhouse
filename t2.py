import matplotlib.pyplot as plt

from solarhouse.thermoelement import Element
from solarhouse.thermomodel import Model

power = 1000
seconds = 60 * 60
R = 4
V = (2 / 3) * 3.14 * (R ** 3)
S = 2 * 3.14 * (R ** 2)
area_floor = 3.13 * R ** 2

alpha_room = 1/0.13
alpha_out = 1/0.04
alpha_windows = 1 / 0.52

mass = Element(
    name='mass',
    temp0=20,
    density=997,
    heat_capacity=4183,
    volume=0.5
)

room = Element(
    name='room',
    temp0=20,
    density=1.27,
    heat_capacity=1007,
    volume=V,
    area_inside=area_floor,
    input_alpha=alpha_room
)
windows = Element(
    name='windows',
    temp0=-5,
    area_inside=10,
    input_alpha=alpha_windows
)
floor = Element(
    name='floor',
    temp0=18,
    area_inside=area_floor,
    area_outside=area_floor+20,
    dx=0.005,
    thickness=0.3,
    kappa=0.7,
    density=1450,
    heat_capacity=880,
    input_alpha=alpha_room
)

walls = Element(
    name='walls',
    temp0=18,
    area_inside=S-50,
    area_outside=S,
    dx=0.005,
    thickness=0.3,
    kappa=0.7,
    density=1450,
    heat_capacity=880,
    input_alpha=alpha_room
)
outside = Element(
    name='outside',
    temp0=-5,
    area_inside=160,
    input_alpha=alpha_out
)
fl_outside = Element(
    name='fl_out',
    temp0=5,
    area_inside=area_floor+20,
    input_alpha=alpha_out
)

mass.branches_loss =[room, floor]
room.branches_loss = [windows, walls]
walls.branches_loss = [outside]
floor.branches_loss = [fl_outside]

mass_model = Model(name='power_to_mass')
mass_model.elements = {
    'mass': mass,
    'room': room,
    'wall': walls,
    'floor': floor,
    'windows': windows,
    'outside': outside,
    'fl_out': fl_outside
}
mass_model.start_element = mass
mass_model.outside_elements = [windows, outside]
mass_model.initial_conditions = {
    'mass': 20,
    'wall': 20,
    'room': 20,
    'floor': 20,
    'fl_out': 5
}
mass_model.plots = [mass, room, walls]

mass_model.start(seconds,power,t_out=-10)

plt.plot(range(0, len(walls.dTx_list)), walls.dTx_list, lw=2)
plt.xlabel('x')
plt.ylabel('T')
plt.show()
