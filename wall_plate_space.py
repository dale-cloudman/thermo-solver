from dataclasses import dataclass


@dataclass
class WallPlateSpace:
    # constants
    s_boltzmann = 5.67e-8
    A_plate = 1
    T_source = 205
    T_space = 3

    # plate params
    L_plate = 1    # thickness
    k_plate = 400  # conductivity

    # equations
    def rate_conduction_left_to_right(self, store):
        return self.A_plate * self.k_plate * (
            self.T_source - store['T_right']
        ) / self.L_plate

    def rate_loss_to_space_right(self, store):
        return self.A_plate * 1.0 * self.s_boltzmann * (
            store['T_right'] ** 4 - self.T_space ** 4
        )

    def balance_right(self, store):
        inp_right = self.rate_conduction_left_to_right(store)
        loss_right = self.rate_loss_to_space_right(store)
        return inp_right - loss_right

    def solve(self):
        store = {
            'T_right': 3,
        }
        step = 0
        while True:
            joules_gain_right = self.balance_right(store)

            temp_gain_right = joules_gain_right / 1000 / 100

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
                'T_right': store['T_right'] + temp_gain_right,
            }
            store = new_store


env = WallPlateSpace()

# # copper
# env.L_plate = 1
# env.k_plate = 400

# # styrofoam
# env.L_plate = 1
# env.k_plate = 0.035

# marble, matching radiative-equivalent
env.L_plate = 1.65
env.k_plate = 2.5

env.solve()
