from dataclasses import dataclass


@dataclass
class Solvemer:
    # constants
    s_boltzmann = 5.67e-8
    A_wire_to_box = 0.000634
    E_circuit_in = 0.46
    A_box_emits = 0.006134
    E_chamber_to_box = 0.24315

    em_box = 0.1
    refl_box = 0.9
    pct_reflect_absorbed_wire = 0.11

    # equations
    def rate_wire_out(self, store):
        return (
            self.s_boltzmann * self.A_wire_to_box * store['T_wire'] ** 4
        )

    def rate_wire_in(self, store):
        return (
            self.E_circuit_in
            + self.s_boltzmann * self.em_box * self.A_wire_to_box * store['T_box'] ** 4
            + self.pct_reflect_absorbed_wire * self.refl_box * self.s_boltzmann * self.A_wire_to_box * store['T_wire'] ** 4
        )

    def rate_box_out(self, store):
        return (
            self.s_boltzmann * self.em_box * self.A_box_emits * store['T_box'] ** 4
        )

    def rate_box_in(self, store):
        return (
            self.E_chamber_to_box
            + self.s_boltzmann * self.em_box * self.A_wire_to_box * store['T_wire'] ** 4
        )

    def balance_wire(self, store):
        inp_left = self.rate_wire_in(store)
        loss_left = self.rate_wire_out(store)
        return inp_left - loss_left

    def balance_box(self, store):
        inp_right = self.rate_box_in(store)
        loss_right = self.rate_box_out(store)
        return inp_right - loss_right

    def solve(self):
        store = {
            'T_wire': 297,
            'T_box': 297,
        }
        step = 0
        while True:
            joules_gain_wire = self.balance_wire(store)
            joules_gain_box = self.balance_box(store)

            temp_gain_wire = joules_gain_wire / 1000 / 10
            temp_gain_box = joules_gain_box / 1000 / 10

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
                'T_wire': store['T_wire'] + temp_gain_wire,
                'T_box': store['T_box'] + temp_gain_box,
            }
            store = new_store


env = Solvemer()

env.solve()
