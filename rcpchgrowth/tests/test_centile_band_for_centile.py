from scipy.stats import norm
from ..centile_bands import centile_band_for_centile
from ..global_functions import sds_for_centile
from ..constants.reference_constants import HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI
from ..constants.reference_constants import THREE_PERCENT_CENTILES, FIVE_PERCENT_CENTILES, EIGHTY_FIVE_PERCENT_CENTILES, COLE_TWO_THIRDS_SDS_NINE_CENTILES

def test_centile_band_for_centile():

    answers = [
        {
            "sds": -6.1,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is well below the normal range. Please review its accuracy."
        },
        {
            "sds": 6.1,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is well above the normal range. Please review its accuracy."
        },
        {
            "sds": -6.1,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is well below the normal range. Please review its accuracy."
        },
        {
            "sds": 6.1,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is well above the normal range. Please review its accuracy."
        },
        {
            "sds": -6.1,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is well below the normal range. Please review its accuracy."
        },
        {
            "sds": 6.1,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is well above the normal range. Please review its accuracy."
        },
        {
            "sds": -6.1,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is well below the normal range. Please review its accuracy."
        },
        {
            "sds": 6.1,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is well above the normal range. Please review its accuracy."
        },
        {
            "sds": -3.0,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is below the normal range."
        },
        {
            "sds": 3.0,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is above the normal range."
        },
        {
            "sds": -3.0,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is below the normal range."
        },
        {
            "sds": 3.0,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is above the normal range."
        },
        {
            "sds": -3.0,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is below the normal range."
        },
        {
            "sds": 3.0,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is above the normal range."
        },
        {
            "sds": -3.0,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is below the normal range."
        },
        {
            "sds": 3.0,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is above the normal range."
        },
        {
            "sds": 2.66,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is on or near the 99.6th centile."
        },
        {
            "sds": 2.66,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is on or near the 99.6th centile."
        },
        {
            "sds": 2.66,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is on or near the 99.6th centile."
        },
        {
            "sds": 2.66,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is on or near the 99.6th centile."
        },
        {
            "sds": 2.66,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is on or near the 99.6th centile."
        },
        {
            "sds": 2.66,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is on or near the 99.6th centile."
        },
        {
            "sds": -2.65,
            "measurement_method": HEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This height measurement is on or near the 0.4th centile."
        },
        {
            "sds": -2.65,
            "measurement_method": WEIGHT,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This weight measurement is on or near the 0.4th centile."
        },
        {
            "sds": -2.65,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This head circumference measurement is on or near the 0.4th centile."
        },
        {
            "sds": -2.65,
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is on or near the 0.4th centile."
        },
        # # some tests for the three-percent-centiles collection. Equivalent SDS for 3rd centile is -1.88, 50th centile is 0.0, 97th centile is 1.88
        {
            "sds": -1.88,
            "measurement_method": HEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 3rd centile."
        },
        {
            "sds": -1.88,
            "measurement_method": WEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 3rd centile."
        },
        {
            "sds": -1.88,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 3rd centile."
        },
        {
            "sds": -1.88,
            "measurement_method": BMI,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 3rd centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": WEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": BMI,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 50th centile."
        },
        {
            "sds": 1.88,
            "measurement_method": HEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 97th centile."
        },
        {
            "sds": 1.88,
            "measurement_method": WEIGHT,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 97th centile."
        },
        {
            "sds": 1.88,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 97th centile."
        },
        # # some tests for the five-percent-centiles collection. Equivalent SDS for 5th centile is -1.645, 50th centile is 0.0, 95th centile is 1.645
        {
            "sds": -1.645,
            "measurement_method": HEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 5th centile."
        },
        {
            "sds": -1.645,
            "measurement_method": WEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 5th centile."
        },
        {
            "sds": -1.645,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 5th centile."
        },
        {
            "sds": -1.645,
            "measurement_method": BMI,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 5th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": WEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": BMI,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 50th centile."
        },
        {
            "sds": 1.645,
            "measurement_method": HEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 95th centile."
        },
        {
            "sds": 1.645,
            "measurement_method": WEIGHT,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 95th centile."
        },
        {
            "sds": 1.645,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 95th centile."
        },
        {
            "sds": 1.645,
            "measurement_method": BMI,
            "centile_format": FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 95th centile."
        },
        # some tests for the eighty-five-percent-centiles collection. Equivalent SDS for 5th centile is -1.44, 50th centile is 0.0, 95th centile is 1.44
        {
            "sds": -1.44,
            "measurement_method": HEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 10th centile."
        },
        {
            "sds": -1.44,
            "measurement_method": WEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 10th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": WEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is on or near the 50th centile."
        },
        {
            "sds": 0.0,
            "measurement_method": BMI,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 50th centile."
        },
        #  tests for the 3.1st centile
        {
            "sds": sds_for_centile(7.1),
            "measurement_method": HEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This height measurement is between the 5th and 10th centiles."
        },
        {
            "sds": sds_for_centile(7.1),
            "measurement_method": WEIGHT,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This weight measurement is between the 5th and 10th centiles."
        },
        {
            "sds": sds_for_centile(7.1),
            "measurement_method": HEAD_CIRCUMFERENCE,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This head circumference measurement is between the 5th and 10th centiles."
        },
        {
            "sds": sds_for_centile(7.1),
            "measurement_method": BMI,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is between the 5th and 10th centiles."
        },
        # tests for CDC centile format at 99.9th centile, 99.99th centile and UK WHO centile format at 99.6th centile and 0.4th centile for BMI
        {
            "sds": sds_for_centile(99.9),
            "measurement_method": BMI,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 99.9th centile."
        },
        {
            "sds": sds_for_centile(99.99),
            "measurement_method": BMI,
            "centile_format": EIGHTY_FIVE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 99.99th centile."
        },
        {
            "sds": sds_for_centile(99.6),
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is on or near the 99.6th centile."
        },
        {
            "sds": sds_for_centile(0.4),
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is on or near the 0.4th centile."
        },
        {
            "sds": sds_for_centile(99.9),
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is above the normal range."
        },
        {
            "sds": sds_for_centile(99.99),
            "measurement_method": BMI,
            "centile_format": COLE_TWO_THIRDS_SDS_NINE_CENTILES,
            "expected": "This body mass index measurement is above the normal range."
        },
        {
            "sds": sds_for_centile(5),
            "measurement_method": BMI,
            "centile_format": THREE_PERCENT_CENTILES,
            "expected": "This body mass index measurement is on or near the 5th centile."
        },
    ]
    
    for answer in answers:
        assert centile_band_for_centile(sds=answer["sds"], measurement_method=answer["measurement_method"], centile_format=answer["centile_format"]) == answer["expected"]