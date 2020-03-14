import matplotlib.pyplot as plt

from solarhouse.thermoelement import Element

power = 7000
seconds = 60 * 60
wall = Element(name='wall',
            temp0=20,
            density=1450,
            heat_capacity=880,
            volume=None,
            thickness=0.3,
            dx=0.005,
            kappa=0.7,
            area_inside=150,
            area_outside=160
             )
outside = Element(
            name='outside',
            temp0=-5,
            area_inside=160
                 )
wall.branches_loss = [{'alpha': 23, 'el':outside}]
for t in range(1, seconds):
    print('SECOND: ', t)
    wall.start_calc(power)
    print(wall.temp)
    print(wall.dTx_list)
plt.plot(range(0,len(wall.dTx_list)), wall.dTx_list, lw=2)
#plt.ylim(19, 21)
plt.xlabel('t')
plt.ylabel('v')
plt.show()