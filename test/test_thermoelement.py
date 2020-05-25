from solarhouse.thermal_element import ThermalElement


def test_cube_water():
    """
    Test cube water as a thermal point.
    Result of test calculated manually.
    """
    e = ThermalElement(name="cube_water", temp0=0, density=997, heat_capacity=4180, volume=1)
    assert e.count_layers == 1
    e.compute(1000, 3600)
    assert round(e.temp, 3) == 0.864


def test_wall_birch():
    """
    Example calculate of wall from birch with dx = 0.01
    meter and 1 kW power coming to inside area of element.
    All result for test calculated manually.
    In this test made two circle of calculation of all 20 point of wall.
    """
    e = ThermalElement(
        name="birch_wall",
        temp0=20.0,
        density=700.0,
        heat_capacity=1250.0,
        dx=0.01,
        thickness=0.20,
        kappa=0.15,
        area_inside=1.0,
        area_outside=1.1,
    )
    assert e.count_layers == 20
    assert e.dTx_list == [
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
        20.0,
    ]
    assert e.get_loss_dx(0) == 0.0
    e.compute(1000, 1)
    assert round(e.dTx_list[0], 3) == 20.109
    assert round(e.dTx_list[1], 3) == 20.0
    assert round(e.get_loss_dx(0), 3) == 1.714
    e.compute(1000, 1)
    assert round(e.dTx_list[0], 3) == 20.218
    assert round(e.dTx_list[1], 4) == 20.0002


def test_thin_layer():
    """Example element which implementing  thin layer between two areas."""
    e = ThermalElement(name="glass", temp0=20.0, area_inside=1.0, input_alpha=23,)
    assert e.calc_loss_input_q(25.0) == 115.0
