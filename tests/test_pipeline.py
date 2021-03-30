from unittest import TestCase

import numpy as np
import pandas as pd
from infrastrategy.kats.consts import TimeSeriesData
from infrastrategy.kats.utils.cupik import Pipeline
from infrastrategy.kats.detectors.trend_mk import MKDetector
from infrastrategy.kats.models.theta import ThetaParams, ThetaModel

DATA = pd.read_csv("infrastrategy/kats/data/air_passengers.csv")
DATA.columns = ["time", "y"]
TSData = TimeSeriesData(DATA)


class cupikTest(TestCase):
    def test_mkdetector(self):

        # We will be using 2 different scenarios to test if the results
        # are the same between a directly called MKDetector and one that
        # is called via CuPiK

        # Scene 1: window_size = 7, direction = 'up'
        pipe = Pipeline(
            [
                ("trend_detector", MKDetector()),
            ]
        )
        pipe.fit(
            TSData, params={"trend_detector": {"window_size": 7, "direction": "up"}}
        )

        self.assertEqual(len(pipe.metadata["trend_detector"][0]), 50)
        self.assertEqual(
            len(pipe.metadata["trend_detector"][0]),
            len(MKDetector(data=TSData).detector(window_size=7, direction="up")),
        )

        # Scene 2: Default parameters of MKDetector
        pipe = Pipeline(
            [
                ("trend_detector", MKDetector()),
            ]
        )
        pipe.fit(TSData)

        self.assertEqual(len(pipe.metadata["trend_detector"][0]), 2)
        self.assertEqual(
            len(pipe.metadata["trend_detector"][0]),
            len(MKDetector(data=TSData).detector()),
        )

    def test_thetamodel(self):
        pipe = Pipeline([("theta_model", ThetaModel(params = ThetaParams()))])
        fitted = pipe.fit(TSData)
        bools = (
            ThetaModel(TSData, ThetaParams()).fit().fitted_values.values
            == fitted.fitted_values.values
        )
        self.assertEqual(np.sum(bools), 144)
        self.assertEqual(fitted.predict(1).fcst.values[0], 433.328591954023)


        # test if the model can be built on the output from the detector
        pipe = Pipeline(
            [
                ("trend_detector", MKDetector()),
                ("theta_model", ThetaModel(params = ThetaParams())),
            ]
        )
        fitted = pipe.fit(TSData)
        self.assertEqual(len(pipe.metadata['trend_detector'][0]), 2)
        self.assertEqual(fitted.predict(1).fcst.values[0], 433.328591954023)
