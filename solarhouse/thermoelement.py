import math
import numpy as np


class Element:
    """
    Implements thermal element for thermal calculations.
    It represents as a point with heat capacity.
    Change of temperature of this point depend of summ of input and
    output energy and heat capacity. Output energy are negative.
    The several elements can be connected to the chain of elements.
    Output energy depends of temperature current element and temperature
    next element in chain and thermal resistance between each other.
    The element can have several elements of output enegry.
    Non first elements must have area of input face (square meters)
    and input coefficient of transcalency on input face.

    Also element may be represented like a wall with a variable area
    and with variable thermal resistance on each dx.
    Calculation realized on one direction dx.
    All calculations makes for dt.
    """

    def __init__(
            self,
            name,
            temp0=None,
            density=None,
            heat_capacity=None,
            volume=None,
            **kwargs):
        """Initialize object of class Element"""
        self.name = name
        self.temp = temp0
        self.round = 5
        self.density = density
        self.heat_capacity = heat_capacity
        self.volume = volume
        self.thickness = kwargs.get('thickness', None)
        self.kappa = kwargs.get('kappa', 0.04)
        self.layers = kwargs.get('layers', {})
        self.dx = kwargs.get('dx',None)
        self.area_inside = kwargs.get('area_inside', None)
        self.area_outside = kwargs.get('area_outside', None)
        self.input_alpha = kwargs.get('input_alpha', None)

        self.branches_loss = []
        self.counter = 0
        self.n = 1
        self.dTx_list = [self.temp]
        if self.thickness and self.dx:
            self.n = int(self.thickness/self.dx)
            self.dTx_list = list(np.ones(self.n) * self.temp)
        self.k_area = None
        if (self.area_inside
                and self.area_outside
                and self.area_outside > self.area_inside):
            self.k_area = ((self.area_outside - self.area_inside)
                 /self.thickness)

    def init_conditions(self, val):
        """Reduction to initial conditions"""
        new_list = []
        for t in self.dTx_list:
            new_list.append(val)
        self.dTx_list = new_list
        self.temp = self.dTx_list[0]
        return

    def __get_area_dx(self, iterator):
        """
        Calculates area of loss power for current dx.
        Returns
        :param iterator: number of dx
        :return:
            Float value of area
        """
        if self.k_area:
            return (self.area_inside
                    + iterator * self.dx * self.k_area)

    def __get_kappa_dx(self, iterator):
        """
        Calculate the kappa if it depends of dx
        :param iterator: number of dx
        :return:
            Float value of thermal resistance of dx layer.
        """
        if self.kappa:
            return self.kappa

    def __get_cm_dx(self, iterator):
        """
        Calculates heat capacity of mass on current dx
        :param iterator: number of dx
        :return:
            Float value of heat capacity
        """
        a = self.density * self.heat_capacity
        if self.n == 1:
            return self.volume * a
        return self.dx * self.__get_area_dx(iterator) * a

    def calc_loss_input_q(self, t_in: float) -> float:
        """Calculates loss energy between current and previous elements"""
        return (
                self.input_alpha
                * self.area_inside
                * round((t_in - self.temp), self.round)
            )

    def get_loss_dx(self, iterator):
        """
        Defines loss energy from current element on dx or from all
        element if it represent in calculation as a point.
        q_loss = alpha*area_branch*(T_current - T_branch)
        :param iterator: number of dx, 0 if element as a point
        :return:
            Float value of all loss power
        """
        temp1 = round(self.dTx_list[iterator], self.round)
        temp2 = round(self.dTx_list[iterator + 1], self.round)
        if temp1 == temp2:
            return 0
        area = self.__get_area_dx(iterator)
        kappa = self.__get_kappa_dx(iterator)
        q_loss = (area * (temp1 - temp2)) / (self.dx / kappa)
        """if abs(q_loss) > 5000:
            print('name: ', self.name)
            print('area: ', area)
            print('kappa: ', kappa)
            print('self.dx: ', self.dx)
            print('temp1: ', temp1)
            print('temp2: ', temp2)
            print('(self.dx / kappa): ', (self.dx / kappa))
            print('(area * (temp1 - temp2)): ', (area * (temp1 - temp2)))
            print('q_loss: ', q_loss)
            exit(0)
        if math.isnan(q_loss):
            print('IS NAN!')
            exit(0)"""
        return q_loss

    def calc_temp(self, q_enter, q_loss, iterator):
        """
        Calculates the dT on dt of current point (dx) of element.
        If element represent as a point then calculates.
        Tdx = Tdx0 + (q_enter - q_loss)/cmdx
        :param q_enter: enter power from previouse element or
            source of power
        :param q_loss: total power loss from current point dx
        :param iterator: number of current dx
        :return:
            Nothing returns but change temperature in list of
            temperatures by dx in the current point
        """
        cm_dx = self.__get_cm_dx(iterator)
        qcm = q_enter - q_loss
        dTdt = qcm / cm_dx
        if dTdt > 100.0:
            print('EXIT ', self.name, ' dTdt: ', dTdt)
            exit(0)
        if dTdt:
            self.dTx_list[iterator] = round(
                self.dTx_list[iterator]
                + dTdt, self.round)
        return

    def start_calc(self, q_enter):
        """
        Start of calculate temperature of element if
        it represent as a point or calculate of all
        temperatures by dx if element has the dx parameter.
        :param q_enter: input power
        :return:
            change self.temp parameter in the end of calculation
        """
        if not self.heat_capacity or not self.density:
            return
        for i in range(0, self.n):
            q_loss = 0
            if (i + 1) == self.n:
                if self.name == 'mass':
                    print('self.dTx_list[i]:', self.dTx_list[i])
                for branch in self.branches_loss:
                    q = branch.calc_loss_input_q(self.dTx_list[i])
                    if self.name == 'mass':
                        print('   ', branch.name, ': ', q)
                    branch.start_calc(q)
                    q_loss += q
            else:
                q_loss = self.get_loss_dx(i)
            self.calc_temp(q_enter, q_loss, i)
            q_enter = q_loss

        self.temp = self.dTx_list[0]


