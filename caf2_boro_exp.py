import math
from dataclasses import dataclass


@dataclass
class CaF2BoroExp:
    # constants
    s_boltzmann = 5.67e-8

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

    # common props
    glass__radius__mm = 50
    glass__thickness__mm = 2
    air__thickness__mm = 1

    # computed props
    @property
    def glass__volume__cm3(self):
        return math.pi * (self.glass__radius__mm / 10 / 2) ** 2 * self.glass__thickness__mm

    @property
    def air__volume__cm3(self):
        return math.pi * (self.glass__radius__mm / 10 / 2) ** 2 * self.air__thickness__mm


env = CaF2BoroExp

print(env.glass__volume__cm3)
print(env.air__volume__cm3)
