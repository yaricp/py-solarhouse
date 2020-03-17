import matplotlib.pyplot as plt

class Model:
    """
    Class implements process of calculation of some model
    of thermal object which contains several thermal elements.
    As result you can take plots of temperatures of some thermal elements.
    """


    def __init__(self, name, **kwargs):
        """"""
        self.name = name
        self.elements = kwargs.get('elements', {})
        self.plots = kwargs.get('plots', [])
        self.initial_conditions = kwargs.get('initial_conditions', {})
        self.start_element = kwargs.get('start_element', None)
        self.outside_elements = kwargs.get('outside', [])

    def show_schema(self):
        """ Shows schema of chain. """
        text = '%s ->' % self.start_element.name
        print(text)
        return

    def start(
            self,
            count: int,
            dt: int,
            power: float,
            t_out: float) -> None:
        """

        :param count: count of calculation
        :param dt: time for calculation (seconds)
        :param power: input power in first thermal element (Watt)
        :param t_out: temperature of last element
        :return:
            - show plot of elements.
        """
        plots = {}
        for el, val in self.initial_conditions.items():
            self.elements[el].init_conditions(val)
        for el in self.plots:
            plots.update({el.name: [el.temp]})
        for el in self.outside_elements:
            el.temp = t_out
        for i in range(count):
            q_enter = power * dt
            self.start_element.start_calc(q_enter)
            for el in self.plots:
                plots[el.name].append(el.temp)
        for el in self.plots:
            plots[el.name].pop()
            plt.plot(range(count), plots[el.name], lw=2)
        if self.plots:
            plt.xlabel('t')
            plt.ylabel('T')
            plt.show()
