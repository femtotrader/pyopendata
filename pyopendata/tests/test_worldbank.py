# pylint: disable-msg=E1101,W0613,W0603

from pyopendata import WorldBankStore, WorldBankResource

import numpy as np
import pandas as pd
from pandas.compat import range
import pandas.util.testing as tm


class TestWorldBankTestSite(tm.TestCase):

    def setUp(self):
        self.store = WorldBankStore()

    def test_isvalid(self):
        self.assertTrue(self.store.is_valid())

    def test_get_gdp_per_capita(self):
        resource = self.store.get('NY.GDP.PCAP.CD')
        self.assertTrue(isinstance(resource, WorldBankResource))

        df = resource.read()

        jp = np.array([478.99534016, 563.58675984, 633.64031517, 717.86691523,
                       835.65725248, 919.77668818, 1058.50356091, 1228.9092104,
                       1450.61965234, 1669.09819991, 2003.64704736, 2234.26166585,
                       2917.65897572, 3931.30162742, 4281.35992841, 4581.57438948,
                       5111.29514922, 6230.33568811, 8675.01399673, 8953.59152028,
                       9307.83929459, 10212.3781359, 9428.87465037, 10213.95827931,
                       10786.78618095, 11465.72578163, 16882.27395207, 20355.60522244,
                       24592.77200535, 24505.76729587, 25123.63178621, 28540.7714826,
                       31013.64714836, 35451.29751157, 38814.89437898, 42522.06659061,
                       37421.67385771, 34294.89897666, 30967.28808909, 34998.80997175,
                       37291.70615804, 32716.41867489, 31235.58818439, 33690.93772972,
                       36441.50449394, 35781.16626514, 34102.11477775, 34095.02343297,
                       37972.0557387, 39473.36750954, 43117.82967369, 46203.69803728])

        us = np.array([2881.0997978, 2934.55277761, 3107.93741663, 3232.2080093,
                       3423.39628164, 3664.8018704, 3972.12308995, 4152.01983719,
                       4491.42430453, 4802.64248506, 5246.96174629, 5623.58844463,
                       6109.6924191, 6741.10113303, 7242.32420249, 7819.95897635,
                       8611.46146261, 9471.5286575, 10587.41604331, 11695.36335562,
                       12597.64550556, 13992.92269879, 14439.01512535, 15561.26813578,
                       17134.3157002, 18269.27926565, 19114.82386844, 20100.78872751,
                       21483.11445037, 22922.46545039, 23954.52342132, 24404.99484151,
                       25492.95555018, 26464.7832594, 27776.42650289, 28781.94969168,
                       30068.22720625, 31572.63521567, 32948.95125682, 34639.11983945,
                       36467.29542582, 37285.81592335, 38175.37638297, 39682.47224732,
                       41928.88613648, 44313.58524128, 46443.81019859, 48070.38468627,
                       48407.0769099, 46998.82041531, 48357.67356926, 49854.52266835])

        index = pd.DatetimeIndex(map(str, range(1960, 2012)), name='date')
        for label, values in [('Japan', jp), ('United States', us)]:
            expected = pd.Series(values, index=index)
            result = df['GDP per capita (current US$)'][label]['1960':'2011']
            tm.assert_series_equal(result, expected)

        raw_data = resource.read(raw=True)
        self.assertTrue(len(raw_data) > 0)

    def test_get_co2_emit(self):
        resource = self.store.get('EN.ATM.CO2E.PC')
        self.assertTrue(isinstance(resource, WorldBankResource))

        df = resource.read()

        jp = np.array([2.51653752, 2.98197939, 3.05973635, 3.35932078,
                       3.67303507, 3.91290553, 4.20626471, 4.86355785,
                       5.56659316, 6.33852317, 7.36808874, 7.54556103,
                       7.96146247, 8.47295875, 8.31387944, 7.77267069,
                       8.05971943, 8.21349644, 7.86685725, 8.24734789,
                       8.11401701, 7.90159205, 7.59990231, 7.41108575,
                       7.83324828, 7.5806754, 7.5340533, 7.41845835,
                       8.06669419, 8.3299481, 8.86239902, 8.88086258,
                       9.04436538, 8.90155004, 9.39514505, 9.43841991,
                       9.58652198, 9.52987839, 9.16909548, 9.45947022,
                       9.61290451, 9.45557013, 9.54726303, 9.68876079,
                       9.85946288, 9.69047361, 9.63791597, 9.79204079,
                       9.4508838, 8.62862707, 9.18565087])

        us = np.array([15.99977916, 15.68125552, 16.0139375, 16.48276215,
                       16.96811858, 17.45172525, 18.12107301, 18.59831788,
                       19.08938916, 19.85794566, 21.11125227, 20.98020348,
                       21.74864198, 22.51058213, 21.50293038, 20.40222407,
                       21.15761537, 21.53248401, 21.96514631, 21.77411499,
                       20.77751491, 19.7492974, 18.56395007, 18.54180517,
                       18.95611586, 18.85669719, 18.70287126, 19.33406449,
                       19.9946205, 20.0595756, 19.10135589, 19.07931196,
                       19.1887997, 19.35128717, 19.46428538, 19.36385544,
                       19.62199049, 19.87640503, 19.77891432, 19.82400911,
                       20.24918916, 19.65619321, 19.6469218, 19.58465737,
                       19.7768452, 19.7159606, 19.22922866, 19.34957722,
                       18.60227269, 17.31529716, 17.56415999])

        index = pd.DatetimeIndex(map(str, range(1960, 2011)), name='date')
        for label, values in [('Japan', jp), ('United States', us)]:
            expected = pd.Series(values, index=index)
            result = df['CO2 emissions (metric tons per capita)'][label]['1960':'2010']
            tm.assert_series_equal(result, expected)

        raw_data = resource.read(raw=True)
        self.assertTrue(len(raw_data) > 0)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'], exit=False)
