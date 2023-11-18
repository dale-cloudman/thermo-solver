import math
import numpy as np


class Constants:
    # synodic moon day: 29 days, 12 hours, 44 minutes, 3 seconds (wikipedia)
    moon_day__s = 2551443

    solar_constant__W_m2 = 1361
    earthshine__W_m2 = 0.10  # 5.67e-8 * 288^4 * ((6371 / 384400)^2)
    sb_constant__W_m2K4 = 5.670374419e-8

    # from https://the-moon.us/wiki/Albedo
    lunar_albedo = 0.07

    # soil conductivity is 1.4e-4 to 2.5e-4 W/cm K, put it in W/mK
    # from https://space.stackexchange.com/questions/19906/constant-lunar-sub-surface-temperature
    soil_thermal_conductivity__W_mK = 1.4e-2

    # from https://adsabs.harvard.edu/full/1973LPSC....4.2481H
    soil_specific_heat__J_kgK = 880

    # from https://curator.jsc.nasa.gov/lunar/letss/regolith.pdf
    # soil_density__g_cm3 = 1.5
    soil_density__kg_m3 = 1500


class MoonModel:
    def __init__(self):
        # start
        self.starting_conditions = {
            'solar_zenith_angle__deg': 0,

            # initial soil temp
            # this is set to be 0 joules of energy
            'soil_temp__K': 50,
        }

        self.vars_logs = {
            'insolation_W': [],
            # 'earthshine_W': [],
            'soil_radiation_W': [],
        }
        self.vars_logs_day_means = {
            'insolation_W': [],
            # 'earthshine_W': [],
            'soil_radiation_W': [],
        }

        # state
        self.soil_energy__J = 0
        self.soil_length__m = 1
        self.soil_width__m = 1
        self.soil_depth__m = 1
        self.soil_weight__kg = Constants.soil_density__kg_m3 * (
            self.soil_length__m *
            self.soil_width__m *
            self.soil_depth__m
        )

        self.sum_dt = 0
        self.steps = 0
        self.steps_day = 0

    @property
    def solar_zenith_angle__deg(self):
        """Get the solar zenith angle in degrees at this time step."""
        return self.starting_conditions['solar_zenith_angle__deg'] + self.sum_dt * 360 / Constants.moon_day__s

    @property
    def solar_input__W_m2(self):
        """Solar input at this time step."""
        insolation__W_m2 = Constants.solar_constant__W_m2 * math.cos(math.radians(self.solar_zenith_angle__deg))
        if insolation__W_m2 < 0:
            # no sunlight at night
            return 0

        return insolation__W_m2 * (1 - Constants.lunar_albedo)

    @property
    def soil_temp__K(self):
        """Get the soil temperature in Kelvin."""
        temp_change__K = self.soil_energy__J / (self.soil_weight__kg * Constants.soil_specific_heat__J_kgK)
        return self.starting_conditions['soil_temp__K'] + temp_change__K

    @property
    def soil_radiation__W(self):
        """Get the soil radiation in W."""
        soil_radiation__W_m2 = Constants.sb_constant__W_m2K4 * self.soil_temp__K**4
        return soil_radiation__W_m2 * (self.soil_width__m * self.soil_length__m)

    @property
    def elapsed__earth_days(self):
        return self.sum_dt / 3600 / 24

    @property
    def elapsed__moon_days(self):
        return self.sum_dt / Constants.moon_day__s

    def step(self, dt=1):
        """Step the model by dt seconds."""
        # this many joules of solar input
        solar_input__W = self.solar_input__W_m2 * (self.soil_width__m * self.soil_length__m)
        solar_input__J = solar_input__W * dt

        earthshine__W = Constants.earthshine__W_m2 * (self.soil_width__m * self.soil_length__m)
        earthshine_input__J = earthshine__W * dt

        self.vars_logs['insolation_W'].append(solar_input__W + earthshine__W)

        # soil radiates according to its temperature across its top surface area
        soil_radiation__J = self.soil_radiation__W * dt
        self.vars_logs['soil_radiation_W'].append(self.soil_radiation__W)

        # update variables
        self.soil_energy__J += solar_input__J + earthshine_input__J - soil_radiation__J

        # add to total time elapsed
        pre_days = int(self.elapsed__moon_days)
        self.sum_dt += dt
        self.steps += 1
        self.steps_day += 1
        post_days = int(self.elapsed__moon_days)

        if post_days > pre_days:
            for key, vals in self.vars_logs.items():
                self.vars_logs_day_means[key].append(int(sum(vals) / len(vals)))
                # clear vars logs
                self.vars_logs[key] = []

            self.steps_day = 0


class CmdLine:
    def run(self):
        soil_temps = []

        mm = MoonModel()
        while mm.elapsed__moon_days < 3:
            mm.step()
            soil_temps.append(mm.soil_temp__K)
            if mm.steps % 100000 == 0:
                print("{:.2f}d, soil temp: {:.2f} K, avg insolation: {}, {:.2f}W, avg radiated out: {}, {:.2f} W".format(
                    mm.elapsed__moon_days,
                    mm.soil_temp__K,
                    mm.vars_logs_day_means['insolation_W'],
                    sum(mm.vars_logs['insolation_W']) / (mm.steps_day + 1e-8),
                    mm.vars_logs_day_means['soil_radiation_W'],
                    sum(mm.vars_logs['soil_radiation_W']) / (mm.steps_day + 1e-8),
                ))

        # plot soil temps
        import matplotlib.pyplot as plt
        plt.plot(soil_temps)

        # y axis from 0 to 400
        plt.ylim(0, 400)

        plt.show()


if __name__ == '__main__':
    import fire
    fire.Fire(CmdLine)
