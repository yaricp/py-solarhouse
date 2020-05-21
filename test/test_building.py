def test_thickness(building):
    assert building.wall_thickness == 0.3


def test_area(building):
    assert building.mesh.area == 6.0


def test_inside_volume(building):
    assert round(building.mesh_inside.volume, 3) == 0.064


def test_center_mass(building):
    assert building.mesh.center_mass[0] == 0.0
    assert building.mesh.center_mass[1] == 0.0
    assert building.mesh.center_mass[2] == 0.5


def test_floor_area_outside(building):
    assert building.floor_area_outside == 1.0


def test_floor_area_inside(building):
    assert round(building.floor_area_inside, 3) == 0.16


def test_walls_area(building):
    assert building.walls_area_outside == 5.0
    assert round(building.walls_area_inside, 3) == 0.8


def test_windows_area(building):
    assert building.windows["area"] == 0.0
    building.windows["area"] = 0.5
    assert building.walls_area_outside == 4.5
    assert round(building.walls_area_inside, 3) == 0.3


def test_perimeter_floor(building):
    building.heat_accumulator["mass"] = 1
    building.heat_accumulator["density"] = 1000
    assert building.get_perimeter_floor("inside") == 1.6
    assert round(building.area_mass_walls_inside, 2) == 0.2
    assert round(building.volume_air_inside, 3) == 0.044
    assert building.get_perimeter_floor("outside") == 4.0
    assert round(building.area_mass_walls_outside, 3) == 1.7
