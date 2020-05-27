About project py-solarhouse
=====================================

.. meta::
   :keywords: solarpower
   :keywords lang=en: python, solar energy, ecology, eco-house, energy efficiency.
   :keywords lang=ru: солнечная энергетика, энергоэффективность, экологичное жилье.


This projects allows you to calculate how many solar energy you can collect on faces of you house and it changes heating season.

For make it you need to load mesh file (.stl or .obj) which represents form of your house and specify some parameters of the house.
After that just start calculation and get plots of temperatures of elements inside house.

For calculate solar power on each face of house with different tilt and azimuth in py-solarhouse uses `PVLIB <https://pvlib-python.readthedocs.io/en/stable/>`_
This library makes it possible to take the weather into account when calculating power.

All thermal processes in the house calculated by models. These models are described here: `Thermal theory <thermal_theory.html>`_

Substituting different parameters of the house, you can carry out the calculation for each configuration and choose the best combination of parameters to save energy for heating.


