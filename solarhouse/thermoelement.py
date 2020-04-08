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
    Calculation realized on one direction dx (in meters).
    All calculations makes for dt.
    Example calculate temperature of mass of water volume 1 cubic meter in 1 hour and 1 kW power:
    >>> e = Element(\
            name='cube_water',\
            temp0=0,\
            density=997,\
            heat_capacity=4180,\
            volume=1\
            )
    >>> e.n
    1
    >>> e.start_calc(1000,3600)
    >>> round(e.temp, 3)
    0.864
    >>>
    Example calculate of wall from birch with dx = 0.01 meter and 1 kW power coming to inside area of element
    >>> e = Element(\
            name='birch_wall',\
            temp0=20.0,\
            density=700.0,\
            heat_capacity=1250.0,\
            dx=0.01,\
            thickness=0.20,\
            kappa=0.15,\
            area_inside=1.0,\
            area_outside=1.1\
            )
    >>> e.n
    20
    >>> e.dTx_list
    [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0,\
 20.0]
    >>> round(e.k_area, 3)
    0.5
    >>> e.get_loss_dx(0)
    0.0
    >>> e.start_calc(1000, 1)
    >>> round(e.dTx_list[0], 3)
    20.114
    >>> round(e.dTx_list[1], 3)
    20.0
    >>> round(e.get_loss_dx(0),3)
    1.723
    >>> e.start_calc(1000, 1)
    >>> round(e.dTx_list[0], 3)
    20.228
    >>> round(e.dTx_list[1], 4)
    20.0002
    >>>
    Example element which implementing  thin layer between two areas
    >>> e = Element(\
            name='glass',\
            temp0=20.0,\
            area_inside=1.0,\
            input_alpha=23,\
            )
    >>> e.calc_loss_input_q(25.0)
    115.0
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
        self.dx = kwargs.get('dx', None)
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
            self.k_area = (
                (self.area_outside - self.area_inside)
                / self.thickness
            )

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
                * (t_in - self.temp)
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
        temp1 = self.dTx_list[iterator]
        temp2 = self.dTx_list[iterator + 1]
        if temp1 == temp2:
            return 0.0
        area = self.__get_area_dx(iterator + 1)
        if area > self.area_outside:
            area = self.area_outside
        kappa = self.__get_kappa_dx(iterator)
        q_loss = (area * (temp1 - temp2)) / (self.dx / kappa)

        return q_loss

    def calc_temp(
            self,
            q_enter: float,
            q_loss: float,
            iterator: int,
            dt: float) -> None:
        """
        Calculates the dT on dt of current point (dx) of element.
        If element represent as a point then calculates.
        Tdx = Tdx0 + (q_enter - q_loss)/cmdx
        :param q_enter: enter power from previouse element or
            source of power
        :param q_loss: total power loss from current point dx
        :param iterator: number of current dx
        :param dt: range of time for calculate
        :return:
            Nothing returns but change temperature in list of
            temperatures by dx in the current point
        """
        cm_dx = self.__get_cm_dx(iterator)
        qcm = q_enter - q_loss
        dT = dt * qcm / cm_dx
        if dT:
            self.dTx_list[iterator] = self.dTx_list[iterator] + dT
        return

    def start_calc(self, q_enter: float, dt: float) -> None:
        """
        Start of calculate temperature of element if
        it represent as a point or calculate of all
        temperatures by dx if element has the dx parameter.
        :param q_enter: input power
        :param dt: range of time
        :return:
            change self.temp parameter in the end of calculation
        """
        if not self.heat_capacity or not self.density:
            return
        for i in range(0, self.n):
            q_loss = 0
            if (i + 1) == self.n:
                for branch in self.branches_loss:
                    q = branch.calc_loss_input_q(self.dTx_list[i])
                    branch.start_calc(q, dt)
                    q_loss += q
            else:
                q_loss = self.get_loss_dx(i)
            self.calc_temp(q_enter, q_loss, i, dt)
            q_enter = q_loss

        self.temp = round(self.dTx_list[0], self.round)


if __name__ == "__main__":
    import doctest
    doctest.testmod()