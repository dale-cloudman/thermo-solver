from dataclasses import dataclass


@dataclass
class OnePlateWithConduction:
    # constants
    s_boltzmann = 5.67e-8
    A_plate = 1
    L_plate = 0.01
    T_sun = 5700
    T_space = 3
    # view factor, scale to receive 1360 W/m^2
    F_left_sun = 1360 / (s_boltzmann * (T_sun ** 4))
    F_right_space = 1
    # conductivity of plate
    k_plate = 400  # copper

    # equations
    def rate_solar_input_left(self, store):
        return self.A_plate * self.F_left_sun * self.s_boltzmann * (
            self.T_sun ** 4 - store['T_left'] ** 4
        )

    def rate_loss_to_space_left(self, store):
        return self.A_plate * (1 - self.F_left_sun) * self.s_boltzmann * (
            store['T_left'] ** 4 - self.T_space ** 4
        )

    def rate_conduction_left_to_right(self, store):
        return self.A_plate * self.k_plate * (
            store['T_left'] - store['T_right']
        ) / self.L_plate

    def rate_loss_to_space_right(self, store):
        return self.A_plate * self.F_right_space * self.s_boltzmann * (
            store['T_right'] ** 4 - self.T_space ** 4
        )

    def balance_left(self, store):
        inp_left = self.rate_solar_input_left(store)
        loss_left = self.rate_loss_to_space_left(store) + self.rate_conduction_left_to_right(store)
        return inp_left - loss_left

    def balance_right(self, store):
        inp_right = self.rate_conduction_left_to_right(store)
        loss_right = self.rate_loss_to_space_right(store)
        return inp_right - loss_right

    def solve(self):
        store = {
            'T_left': 3,
            'T_right': 3,
        }
        step = 0
        while True:
            joules_gain_left = self.balance_left(store)
            joules_gain_right = self.balance_right(store)

            temp_gain_left = joules_gain_left / 1000 / 1000
            temp_gain_right = joules_gain_right / 1000 / 1000

            step += 1
            if step % 100000 == 0:
                # print("Solar input left: ", self.rate_solar_input_left(store))
                # print("Loss space left: ", self.rate_loss_to_space_left(store))
                # print("Conduction left to right: ", self.rate_conduction_left_to_right(store))
                # print("Loss space right: ", self.rate_loss_to_space_right(store))
                # print("Gain left: ", joules_gain_left)
                # print("Gain right: ", joules_gain_right)
                print(store)

            new_store = {
                'T_left': store['T_left'] + temp_gain_left,
                'T_right': store['T_right'] + temp_gain_right,
            }
            store = new_store


env = OnePlateWithConduction()

env.L_plate = 1
env.k_plate = 0.035

env.solve()
