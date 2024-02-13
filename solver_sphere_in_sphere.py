import math
from dataclasses import dataclass


@dataclass
class SphereInSphere:
    # constants
    s_boltzmann = 5.67e-8

    A_ball = 1
    r_ball = math.sqrt(A_ball / 4 / math.pi)

    A_inner = 2
    L_shell = 0.01
    r_inner = math.sqrt(A_inner / 4 / math.pi)
    r_outer = r_inner + L_shell
    A_outer = 4 * math.pi * r_outer ** 2

    T_amb = 288
    Q_heatgen = 1000
    emissivity = 1
    k_ball = 45

    step = 0

    # equations
    def rate_ball_input(self, store):
        return self.Q_heatgen

    def rate_ball_to_inner(self, store):
        return self.s_boltzmann * self.emissivity * self.A_ball * (
            store['T_ball'] ** 4 - store['T_inner'] ** 4
        )

    def rate_inner_to_outer_conduction(self, store):
        return (store['T_inner'] - store['T_outer']) / (
            (self.r_outer - self.r_inner) / (
                4 * math.pi * self.r_inner * self.r_outer * self.k_ball
            )
        )

    def rate_outer_to_amb(self, store):
        return self.s_boltzmann * self.emissivity * self.A_outer * (
            store['T_outer'] ** 4 - self.T_amb ** 4
        )

    def balance_ball(self, store):
        inp = self.rate_ball_input(store)
        outp = self.rate_ball_to_inner(store)
        return inp - outp

    def balance_inner(self, store):
        inp = self.rate_ball_to_inner(store)
        outp = self.rate_inner_to_outer_conduction(store)
        return inp - outp

    def balance_outer(self, store):
        inp = self.rate_inner_to_outer_conduction(store)
        outp = self.rate_outer_to_amb(store)
        return inp - outp

    def solve(self):
        store = {
            'T_ball': 288,
            'T_inner': 288,
            'T_outer': 288,
        }
        self.step = 0
        while True:
            joules_gain_ball = self.balance_ball(store)
            joules_gain_inner = self.balance_inner(store)
            joules_gain_outer = self.balance_outer(store)

            self.step += 1
            if self.step % 100000 == 0:
                print(store)

            new_store = {
                'T_ball': store['T_ball'] + joules_gain_ball / 1000 / 1000,
                'T_inner': store['T_inner'] + joules_gain_inner / 1000 / 1000,
                'T_outer': store['T_outer'] + joules_gain_outer / 1000 / 1000
            }
            store = new_store


env = SphereInSphere()
env.solve()
