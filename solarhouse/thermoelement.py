import numpy as np


class Element:
    """
    Implements thermal element for thermal calculations.
    It is may be represents as a point with heat capacity.
    Also it may be represented like a walls with a variable area
    and with variable thermal resistance.
    Calculation realized on one direction dx.
    All calculations makes for dt.
    """

    def __init__(
            self,
            name,
            temp0,
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
        #if self.area_inside:
        #    return self.area_inside
        #sreturn self.area_outside

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

    def get_loss_dx(self, iterator):
        """
        Defines loss energy from current element on dx or from all
        element if it represent in calculation as a point.
        q_loss = alpha*area_branch*(T_current - T_branch)
        :param iterator: number of dx, 0 if element as a point
        :return:
            Float value of all loss power
        """
        q_loss = 0
        if (iterator + 1) == self.n:
            for branch in self.branches_loss:
                #if (self.dTx_list[iterator]
                #    - branch['el'].temp):
                q = (
                        branch['alpha']
                        * branch['el'].area_inside
                        * round((self.dTx_list[iterator]
                                 - branch['el'].temp), self.round)
                    )
                if self.name == 'mass':
                    print('q_loss ',branch['el'].name, ': ', q)
                q_loss += q
            return q_loss

        temp1 = round(self.dTx_list[iterator], self.round)
        temp2 = round(self.dTx_list[iterator + 1], self.round)
        if temp1 == temp2:
            return 0
        area = self.__get_area_dx(iterator)
        kappa = self.__get_kappa_dx(iterator)
        return area * (temp1 - temp2) / (self.dx / kappa)

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
        if self.name == 'mass':
            print('dTdt: ', dTdt)
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
            q_loss = self.get_loss_dx(i)
            self.calc_temp(q_enter, q_loss, i)
            for branch in self.branches_loss:
                branch['el'].start_calc(q_loss)
            q_enter = q_loss
        self.temp = self.dTx_list[0]


