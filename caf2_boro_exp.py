import math
import time
from dataclasses import dataclass
import tabulate


@dataclass
class CaF2BoroExp:
    # constants
    s_boltzmann = 5.67e-8

    # simulation params
    outsideair__temp__K = 27 + 273.15

    # Caf2 props
    caf2__specheat__J_kg_K = 887.6  # https://www.sciencedirect.com/topics/chemical-engineering/calcium-fluoride
    caf2__density__g_cm3 = 3.18     # https://www.sciencedirect.com/topics/chemical-engineering/calcium-fluoride
    caf2__thermcond__W_mK = 9.71    # https://www.sciencedirect.com/topics/chemical-engineering/calcium-fluoride

    # absorption coefficients: https://lightmachinery.com/media/1542/h0607_caf2_product_sheet.pdf

    # borosilicate
    boro__specheat__J_kg_K = 830   # https://www.makeitfrom.com/material-properties/Borosilicate-Glass
    boro__density__g_cm3 = 2.23    # https://www.azom.com/article.aspx?ArticleID=4765
    boro__thermcond__W_mk = 1.13   # https://www.azom.com/article.aspx?ArticleID=4765

    # cork
    cork__specheat__J_kg_K = 2000   # https://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html
    cork__thermcond__W_mK = 0.0385  # https://www.corkstore24.co.uk/properties-of-cork-material/
    cork__density__g_cm3 = 0.24     # https://kg-m3.com/material/cork

    # air
    air__specheat__J_kg_K = 1007    # isobaric @ 50ºC, https://www.engineeringtoolbox.com/air-specific-heat-capacity-d_705.html
    air__thermcond__W_mk = 2808     # @ 50ºC, https://www.engineeringtoolbox.com/air-properties-viscosity-conductivity-heat-capacity-d_1509.html
    air__density__g_cm3 = 0.001093  # @ 50ºC, https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html

    # the experiment consists of layers
    # - = cork
    # * = glass (either borosilicate or caf2)
    # each ascii row = 1mm

    #               v  sun  v
    # ------                         ------
    # --------                     --------
    #       ************************* -----
    #       ************************* -----
    # --------                     --------
    # ----- *************************
    # ----- *************************
    # --------                     --------
    #       ************************* -----
    #       ************************* -----
    # --------                     --------
    # ----- *************************
    # ----- *************************
    # --------                     --------
    # ------------------T------------------
    # -------------------------------------
    # -------------------------------------
    # ------------------T------------------
    #
    #                outside

    # glasses are 50mm diameter, 2mm thick
    # 1mm air gaps in between

    # simplify like this:
    #                   v  sun  v
    # ----------                         ----------
    # ----------                         ----------
    # ----------*************************----------  glass4
    # ----------*************************----------  glass4
    # ----------                         ----------  gap4
    # ----------*************************----------  glass3
    # ----------*************************----------  glass3
    # ----------                         ----------  gap3
    # ----------*************************----------  glass2
    # ----------*************************----------  glass2
    # ----------                         ----------  gap2
    # ----------*************************----------  glass1
    # ----------*************************----------  glass1
    # ----------                         ----------  gap1
    # ----------------------T----------------------  blackcork
    # ---------------------------------------------  cork2
    # ---------------------------------------------  cork3
    # ---------------------------------------------  cork4
    # ---------------------------------------------  cork5
    # ----------------------T----------------------  cork6
    #
    #                    outside

    # glassees are 50mm, cork is 90mm
    # each dash = 2mm, each line = 1mm

    # consider losses to the sides as negligible
    # (not far off as when i packed first version tightly, it did not
    #  get much hotter at all)

    # non-radiative heat flows are then:

    # blackcork -> outside: conduction through cork cylinder 90mm diameter x 6mm tall
    # blackcork -> glass1:  convection through 1mm air
    # glass

    # radiative heat flows are:
    # sun -> blackcork:     consider as heat generation
    # blackcork emits as graybody, absorbs from glass1, glass2, glass3, glass4, and sky
    # glass1 emits as graybody, absorbs from blackcork, glass2, glass3, glass4, and sky
    # etc ...


    # geometry
    glass__diameter__mm = 50
    glass__thickness__mm = 2
    airgap__thickness__mm = 1
    fullcork__diameter__mm = 90

    # computed props
    @property
    def glass__volume__cm3(self):
        return math.pi * (self.glass__diameter__mm / 10 / 2) ** 2 * (self.glass__thickness__mm / 10)

    @property
    def airgap__volume__cm3(self):
        return math.pi * (self.glass__diameter__mm / 10 / 2) ** 2 * (self.airgap__thickness__mm / 10)

    @property
    def caf2__weight__g(self):
        return self.caf2__density__g_cm3 * self.glass__volume__cm3

    @property
    def caf2__heatcap__J_K(self):
        return self.caf2__specheat__J_kg_K * (self.caf2__weight__g / 1000)

    @property
    def boro__weight__g(self):
        return self.boro__density__g_cm3 * self.glass__volume__cm3

    @property
    def boro__heatcap__J_K(self):
        return self.boro__specheat__J_kg_K * (self.boro__weight__g / 1000)

    @property
    def airgap__weight__g(self):
        return self.air__density__g_cm3 * self.airgap__volume__cm3

    @property
    def airgap__heatcap__J_K(self):
        return self.air__specheat__J_kg_K * (self.airgap__weight__g / 1000)

    def run_noglass(self):
        # run with just sun hitting the black cork bottom
        # initial conditions, all at air temp
        temps__K = {
            'blackcork': self.outsideair__temp__K,
            'corkbottom': self.outsideair__temp__K,

            # 'corkbottom': 50 + 273.15,  # FIX IT
        }

        # aiming to get black cork to 61C and bottom to 51C or so

        h_conv_up__W_m2_K = 15
        h_conv_down__W_m2_K = 3
        insolation__W_m2 = 881  # direct to black bottom
        cork__thickness__mm = 6
        fullcork__surfarea__m2 = math.pi * (self.fullcork__diameter__mm / 1000 / 2) ** 2

        # one cork piece heat cap...
        cork__volume__1mmpiece__cm3 = math.pi * (self.fullcork__diameter__mm / 10 / 2) ** 2 * (1 / 10)
        cork__weight__1mmpiece__g = self.cork__density__g_cm3 * cork__volume__1mmpiece__cm3
        cork__heatcap__1mmpiece__J_K = self.cork__specheat__J_kg_K * (cork__weight__1mmpiece__g / 1000)

        # it gets sun directly through glass diameter
        insolation_area_m2 = math.pi * (self.glass__diameter__mm / 1000 / 2) ** 2

        # TODO: calc conduction each layer through cork upwards, do radiative transfer
        #       calcs for each one, and with the sky (need to calc view factor)

        step = 0
        time_step__s = 0.001  # 1ms each step
        historical_temps__C = {key: [] for key in temps__K}
        while True:
            # loses conductively to the bottom
            blackcork_cond_to_bottom__W = (
                # conductivity
                self.cork__thermcond__W_mK
                # * (area / thickness) of conduction
                * (fullcork__surfarea__m2 / (cork__thickness__mm / 1000))
                # * temp gradient
                * (temps__K['blackcork'] - temps__K['corkbottom'])
            )
            blackcork_conv_to_air__W = (
                # conv coeff
                h_conv_up__W_m2_K
                # conv area which is same as insolation area
                * insolation_area_m2
                # temp gradient vs outside air
                * (temps__K['blackcork'] - self.outsideair__temp__K)
            )


            blackcork_W = (
                # gains from sun
                + (insolation__W_m2 * insolation_area_m2)
                - blackcork_cond_to_bottom__W
                - blackcork_conv_to_air__W
            )

            bottom_conv_to_air__W = (
                h_conv_down__W_m2_K
                # conv area which is same as fullcork
                * fullcork__surfarea__m2
                # temp gradient vs outside air
                * (temps__K['corkbottom'] - self.outsideair__temp__K)
            )
            bottom_W = (
                # gains from blackcork
                + blackcork_cond_to_bottom__W
                # loses to outside air
                - bottom_conv_to_air__W
            )

            if step % 1000 == 0:
                for key in temps__K:
                    historical_temps__C[key].append(temps__K[key] - 273.15)

            if step % 30_000 == 0:
                rows = [
                    ('minutes into sim', '%.2f' % (step * time_step__s / 60)),
                    ('insolation (W/m^2)', insolation__W_m2),
                    ('blackcork insolation (W)', insolation_area_m2 * insolation__W_m2),
                    ('blackcork cond to bottom (W)', blackcork_cond_to_bottom__W),
                    ('blackcork conv to air (W)', blackcork_conv_to_air__W),
                    ('bottom conv to air (W)', bottom_conv_to_air__W),
                    ('cork weight 1mm piece (g)', cork__weight__1mmpiece__g),
                    ('cork heatcap 1mm piece (J/K)', cork__heatcap__1mmpiece__J_K),
                ]

                for temp_key, temp__K in temps__K.items():
                    rows.append(('%s (ºC)' % temp_key, temp__K - 273.15))
                print(tabulate.tabulate(rows))
                # time.sleep(1)

            # Watts * time = joules gain, * heat capacity = temp change
            # for the cork top, consider a 1mm thick piece as what is gaining / losing
            temps__K['blackcork'] += (blackcork_W * time_step__s) / cork__heatcap__1mmpiece__J_K
            # for the bottom it has to 'go through' all 6mm so consider all those
            temps__K['corkbottom'] += (bottom_W * time_step__s) / (cork__heatcap__1mmpiece__J_K*5)
            step += 1

            # if 20 mins passed, break
            mins_passed = step * time_step__s / 60
            if mins_passed >= 30:
                break

        import matplotlib.pyplot as plt
        plt.plot(historical_temps__C['blackcork'])
        plt.plot(historical_temps__C['corkbottom'])
        plt.show()


env = CaF2BoroExp()

# rows = [
#     ('glass volume (cm3)', env.glass__volume__cm3),
#     ('caf2 weight (g)', env.caf2__weight__g),
#     ('caf2 heat capacity (J/K)', env.caf2__heatcap__J_K),
#     ('boro weight (g)', env.boro__weight__g),
#     ('boro heat capacity (J/K)', env.boro__heatcap__J_K),
#     ('airgap volume (cm3)', env.airgap__volume__cm3),
#     ('airgap weight (g)', env.airgap__weight__g),
#     ('airgap heat capacity (J/K)', env.airgap__heatcap__J_K),
# ]
# import tabulate
# print(tabulate.tabulate(rows))
# print("--------------")
env.run_noglass()

