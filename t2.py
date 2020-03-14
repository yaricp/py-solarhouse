import matplotlib.pyplot as plt

from solarhouse.thermoelement import Element

power = 1000
seconds = 60 * 60
R = 4
V = (2 / 3) * 3.14 * (R ** 3)
S = 2 * 3.14 * (R ** 2)
area_floor = 3.13 * R ** 2

alpha_room = 1/0.13
alpha_out = 1/0.04

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
    area_inside=area_floor
)
windows = Element(
    name='windows',
    temp0=-5,
    area_inside=10
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
    heat_capacity=880
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
    heat_capacity=880
)
outside = Element(
    name='outside',
    temp0=-5,
    area_inside=160
)
fl_outside = Element(
    name='fl_out',
    temp0=5,
    area_inside=area_floor+20
)
alpha_windows = 1 / 0.52
mass.branches_loss =[
    {'alpha': alpha_room, 'el': room},
    {'alpha': alpha_room, 'el': floor}
]
room.branches_loss = [
    {'alpha': alpha_windows, 'el': windows},
    {'alpha': alpha_room, 'el': walls}
]
walls.branches_loss = [
    {'alpha': alpha_out, 'el': outside}
]
floor.branches_loss = [
    {'alpha': alpha_out, 'el': fl_outside}
]
mass_t_list = [mass.temp]
room_t_list = [room.temp]
wall_t_list = [walls.temp]
#Start calculation by the seconds and input power by Watt
for t in range(1, seconds):
    mass.start_calc(power)
    mass_t_list.append(mass.temp)
    room_t_list.append(room.temp)
    wall_t_list.append(walls.temp)
    print('---------------')
    print('Temp mass room : ')
    print(mass.temp, room.temp)
    print(' Twall[0]: ', walls.temp)
    print('---------------')
# shows results
plt.plot(range(0, seconds), mass_t_list, lw=2)
plt.plot(range(0, seconds), room_t_list, lw=2)
plt.plot(range(0, seconds), wall_t_list, lw=2)
#plt.ylim(19, 21)
plt.xlabel('t')
plt.ylabel('T room')
plt.show()
print(walls.dTx_list)
plt.plot(range(0, len(walls.dTx_list)), walls.dTx_list, lw=2)
#plt.ylim(19, 21)
plt.xlabel('x')
plt.ylabel('T')
plt.show()