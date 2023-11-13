from dataclasses import dataclass


@dataclass
class TwoPlatesWithConduction:
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
    # view factor between plates
    F_left_to_right = 1

    step = 0

    # equations
    def rate_p1_solar_input_left(self, store):
        return self.A_plate * self.F_left_sun * self.s_boltzmann * (
            self.T_sun ** 4 - store['T1_left'] ** 4
        )

    def rate_p1_loss_to_space_left(self, store):
        return self.A_plate * (1 - self.F_left_sun) * self.s_boltzmann * (
            store['T1_left'] ** 4 - self.T_space ** 4
        )

    def rate_p1_conduction_left_to_right(self, store):
        if self.step % 100000 == 0:
            print("cond left right:", self.A_plate, self.k_plate, store['T1_left'], store['T1_right'], self.L_plate)
        return self.A_plate * self.k_plate * (
            store['T1_left'] - store['T1_right']
        ) / self.L_plate

    def rate_p1_radiate_to_p2_left(self, store):
        return self.A_plate * self.F_left_to_right * self.s_boltzmann * (
            store['T1_right'] ** 4 - store['T2_left'] ** 4
        )

    def rate_p2_conduct_to_right(self, store):
        return self.A_plate * self.k_plate * (
            store['T2_left'] - store['T2_right']
        ) / self.L_plate

    def rate_p2_loss_to_space_right(self, store):
        return self.A_plate * self.F_right_space * self.s_boltzmann * (
            store['T2_right'] ** 4 - self.T_space ** 4
        )

    def balance_p1_left(self, store):
        inp_left = self.rate_p1_solar_input_left(store)
        loss_left = self.rate_p1_loss_to_space_left(store) + self.rate_p1_conduction_left_to_right(store)
        return inp_left - loss_left

    def balance_p1_right(self, store):
        inp_right = self.rate_p1_conduction_left_to_right(store)
        loss_right = self.rate_p1_radiate_to_p2_left(store)
        return inp_right - loss_right

    def balance_p2_left(self, store):
        inp = self.rate_p1_radiate_to_p2_left(store)
        loss = self.rate_p2_conduct_to_right(store)
        return inp - loss

    def balance_p2_right(self, store):
        inp = self.rate_p2_conduct_to_right(store)
        loss = self.rate_p2_loss_to_space_right(store)
        return inp - loss

    def solve(self):
        store = {
            'T1_left': 3,
            'T1_right': 3,
            'T2_left': 3,
            'T2_right': 3,
        }
        self.step = 0
        while True:
            joules_gain_p1_left = self.balance_p1_left(store)
            joules_gain_p1_right = self.balance_p1_right(store)
            joules_gain_p2_left = self.balance_p2_left(store)
            joules_gain_p2_right = self.balance_p2_right(store)

            self.step += 1
            if self.step % 100000 == 0:
                print("Solar input left: ", self.rate_p1_solar_input_left(store))
                print("Loss space left: ", self.rate_p1_loss_to_space_left(store))
                print("Conduction left to right: ", self.rate_p1_conduction_left_to_right(store))
                print("Balance p1 left:", self.balance_p1_left(store))

                # print("Conduction left to right: ", self.rate_conduction_left_to_right(store))
                # print("Loss space right: ", self.rate_loss_to_space_right(store))
                # print("Gain left: ", joules_gain_left)
                # print("Gain right: ", joules_gain_right)
                print(store)

            new_store = {
                'T1_left': store['T1_left'] + joules_gain_p1_left / 1000 / 1000,
                'T1_right': store['T1_right'] + joules_gain_p1_right / 1000 / 1000,
                'T2_left': store['T2_left'] + joules_gain_p2_left / 1000 / 1000,
                'T2_right': store['T2_right'] + joules_gain_p2_right / 1000 / 1000
            }
            store = new_store


env = TwoPlatesWithConduction()

env.L_plate = 0.01
env.k_plate = 400

env.solve()
