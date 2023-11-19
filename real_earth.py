import math
import numpy as np


class Constants:
    earth_day__s = 86400

    solar_constant__W_m2 = 1361
    sb_constant__W_m2K4 = 5.670374419e-8

    # from https://link.springer.com/article/10.1007/s00382-018-4413-y
    # 340 arrives TOA and 214 absorbed by surface
    earth_albedo = 0.47

    # sample from https://www.nature.com/articles/s41598-023-37413-5
    soil_thermal_conductivity__W_mK = 0.21

    # from https://acsess.onlinelibrary.wiley.com/doi/epdf/10.2136/sssaj1991.03615995005500010052x
    # Salkum soil
    soil_specific_heat__J_kgK = 900

    # from https://en.wikipedia.org/wiki/Soil#:~:text=Most%20soils%20have%20a%20dry,to%202.7%20g%2Fcm3.
    soil_density__kg_m3 = 1350


class EarthModel:
    def __init__(self):
        # start
        self.starting_conditions = {
            # start at horizon
            'solar_zenith_angle__deg': -90,

            # initial soil temp
            # this is set to be 0 joules of energy
            # we do many layers
            'soil_temp__K': 208,
        }

        self.vars_logs = {
            'radiative_input_W': np.zeros(Constants.earth_day__s),
            'soil_radiation_W': np.zeros(Constants.earth_day__s),
            'avg_soil_temp__K': np.zeros(Constants.earth_day__s),
        }
        self.vars_logs_day_means = {
            'radiative_input_W': [],
            'soil_radiation_W': [],
            'avg_soil_temp__K': [],
        }

        # state
        self.soil_layer_length__m = 1
        self.soil_layer_width__m = 1
        self.soil_layer_depth__m = 0.1
        self.soil_layer_weight__kg = Constants.soil_density__kg_m3 * (
            self.soil_layer_length__m *
            self.soil_layer_width__m *
            self.soil_layer_depth__m
        )
        self.soil_layers_energy__J = [0] * 20

        self.sum_dt = 0
        self.steps = 0
        self.steps_day = 0

    @property
    def solar_zenith_angle__deg(self):
        """Get the solar zenith angle in degrees at this time step."""
        return self.starting_conditions['solar_zenith_angle__deg'] + self.sum_dt * 360 / Constants.earth_day__s

    @property
    def solar_input__W_m2(self):
        """Solar input at this time step."""
        # insolation__W_m2 = Constants.solar_constant__W_m2 * math.cos(math.radians(self.solar_zenith_angle__deg))
        # if insolation__W_m2 < 0:
        #     # no sunlight at night
        #     return 0
        #
        # return insolation__W_m2 * (1 - Constants.earth_albedo)

        # averaged over this part of the Earth
        return Constants.solar_constant__W_m2 * (1 / math.pi) * (1 - Constants.earth_albedo)

    def soil_temp__K(self, layer):
        """Get the soil temperature in Kelvin."""
        temp_change__K = self.soil_layers_energy__J[layer] / (self.soil_layer_weight__kg * Constants.soil_specific_heat__J_kgK)
        return self.starting_conditions['soil_temp__K'] + temp_change__K

    @property
    def soil_radiation__W(self):
        """Get the soil radiation in W of topmost layer."""
        soil_radiation__W_m2 = Constants.sb_constant__W_m2K4 * self.soil_temp__K(layer=0)**4
        return soil_radiation__W_m2 * (self.soil_layer_width__m * self.soil_layer_length__m)

    @property
    def elapsed__planet_days(self):
        return self.sum_dt / Constants.earth_day__s

    def step(self, dt=1):
        """Step the model by dt seconds."""
        # this many joules of solar input
        solar_input__W = self.solar_input__W_m2 * (self.soil_layer_width__m * self.soil_layer_length__m)
        solar_input__J = solar_input__W * dt

        self.vars_logs['radiative_input_W'][self.steps_day] = solar_input__W

        # soil radiates according to its temperature across its top surface area
        soil_radiation__J = self.soil_radiation__W * dt
        self.vars_logs['soil_radiation_W'][self.steps_day] = self.soil_radiation__W

        # update variables
        # first layer gets the sunlight
        soil_layers__dJ = [0] * len(self.soil_layers_energy__J)
        soil_layers__dJ[0] = solar_input__J - soil_radiation__J
        # rest of layers conduct downward
        for layer_i in range(1, len(self.soil_layers_energy__J)):
            # energy conducted is the difference in temperature between this layer and the one below
            # multiplied by the thermal conductivity of the soil and the distance
            A = self.soil_layer_width__m * self.soil_layer_length__m
            dT = self.soil_temp__K(layer=layer_i - 1) - self.soil_temp__K(layer=layer_i)
            dx = self.soil_layer_depth__m
            conducted_down__J = Constants.soil_thermal_conductivity__W_mK * A * dT / dx
            # earlier layer loses
            soil_layers__dJ[layer_i - 1] -= conducted_down__J
            # this layer gains
            soil_layers__dJ[layer_i] += conducted_down__J

        # update the soil values
        for layer_i in range(len(self.soil_layers_energy__J)):
            self.soil_layers_energy__J[layer_i] += soil_layers__dJ[layer_i]

        self.vars_logs['avg_soil_temp__K'][self.steps_day] = self.soil_temp__K(layer=0)

        # add to total time elapsed
        pre_days = int(self.elapsed__planet_days)
        self.sum_dt += dt
        self.steps += 1
        self.steps_day += 1
        post_days = int(self.elapsed__planet_days)

        if post_days > pre_days:
            for key, vals in self.vars_logs.items():
                self.vars_logs_day_means[key].append(int(round(np.mean(vals))))
                # clear vars logs
                self.vars_logs[key] = np.zeros(len(vals))

            self.steps_day = 0


class CmdLine:
    def run(self):
        soil_temps = []

        mm = EarthModel()
        while True:
            pre_day = int(mm.elapsed__planet_days)
            mm.step()
            post_day = int(mm.elapsed__planet_days)

            if mm.steps % 100 == 0:
                soil_temps.append(mm.soil_temp__K(0))

            if mm.steps % 10000 == 0:
                print("{:.2f}d, dIns {:.0f}W, dROut {:.0f}W, soil T: [{}]K, daily avg tmps: {}K {}, avg insolation: {}, avg radiated out: {}".format(
                    mm.elapsed__planet_days,
                    mm.vars_logs['radiative_input_W'][mm.steps_day - 1],
                    mm.vars_logs['soil_radiation_W'][mm.steps_day - 1],
                    " ".join("%.0f" % mm.soil_temp__K(i) for i in range(len(mm.soil_layers_energy__J))),
                    "%.0f" % np.mean(mm.vars_logs['avg_soil_temp__K'][:mm.steps_day]),
                    mm.vars_logs_day_means['avg_soil_temp__K'][::-1][:10],
                    mm.vars_logs_day_means['radiative_input_W'][::-1][:10],
                    mm.vars_logs_day_means['soil_radiation_W'][::-1][:10],
                ))

            if pre_day != post_day and post_day % 20 == 0:
                # plot soil temps
                import matplotlib.pyplot as plt
                plt.plot(soil_temps)

                # y axis from 0 to 400
                plt.ylim(0, 400)

                # add ticks every
                plt.yticks(np.arange(0, 400, 20))

                plt.show()


if __name__ == '__main__':
    import fire
    fire.Fire(CmdLine)
