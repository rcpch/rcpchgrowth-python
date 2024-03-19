# standard imports
import json
from typing import Literal
import os
import math

# from scipy.interpolate import UnivariateSpline
# import matplotlib.pyplot as plt
# TODO #21 - do the above lines need to be commented out?

# rcpchgrowth local imports
from rcpchgrowth.constants.reference_constants import FEMALE, MALE, UK_WHO, WEIGHT
from rcpchgrowth.global_functions import measurement_from_sds, sds_for_centile, z_score, linear_interpolation

"""
These functions are experimental
Height, weight, BMI or OFC in terms of SDS / Centile are snapshots in time and tell
us actually very little about growth, which is a dynamic measure. In order to make
predictions, we need to look at change in parameter measured over time (velocity)
which requires 2 measurements over a known time interval, or change in velocity (acceleration/deceleration)
which requires three measurements.

From these measurements predictions can be made about speed of growth, or rate of slowing (catch down)
or acceleration (catch up). The normative data against which to compare the index child are
thrive lines, generated here.

"""


def velocity(parameter: str, measurements_array):
    """
    This is an experimental function and not to be used clinically because velocity is not constant
    and is age dependent.
    Velocity needs at least 2 measurements from 2 consecutive time points.
    This takes an array of Measurement objects of the same child, removes the last 2 values of the same
    measurement and calculates the velocity in units/y.
    """
    parameter_list = []
    if len(measurements_array) < 2:
        return 'Not enough data'
    else:
        for measurement in measurements_array:
            if measurement:
                if parameter == measurement['child_observation_value']['measurement_method']:
                    parameter_list.append(measurement)
        if len(parameter_list) < 2:
            return f"There are not enough {parameter} values to calculate a velocity."
        else:
            last = parameter_list[-1]
            penultimate = parameter_list[-2]
            time_elapsed = last['measurement_dates']['chronological_decimal_age'] - \
                penultimate['measurement_dates']['chronological_decimal_age']
            parameter_difference = 0.0
            parameter_difference = last['child_observation_value']['observation_value'] - \
                penultimate['child_observation_value']['observation_value']
            return parameter_difference / time_elapsed


def acceleration(parameter: str, measurements_array):
    """
    This is an experimental function and not to be used clinically because acceleration is not constant
    and is age dependent.
    Accelaration needs at least 3 measurements over 3 consecutive time points in order to compare the velocity
    change between the first pair and the last pair.
    This takes an array of Measurement objects of the same child, removes the last 3 values of the same
    measurement and calculates the acceleration.
    The parameter in question is one of 'height', 'weight', 'bmi', 'ofc'
    """
    parameter_list = []
    if len(measurements_array) < 3:
        return 'Not enough data'
    else:
        for measurement in measurements_array:
            if measurement:
                if parameter == measurement['child_observation_value']['measurement_method']:
                    parameter_list.append(measurement)
        if len(parameter_list) < 3:
            return f"There are not enough {parameter} values to calculate acceleration."
        else:
            last = parameter_list[-1]
            penultimate = parameter_list[-2]
            antepentultimate = parameter_list[-3]
            first_parameter_pair_time_elapsed = penultimate['measurement_dates']['chronological_decimal_age'] - \
                antepentultimate['measurement_dates']['chronological_decimal_age']
            last_parameter_pair_time_elapsed = last['measurement_dates']['chronological_decimal_age'] - \
                penultimate['measurement_dates']['chronological_decimal_age']
            first_parameter_pair_difference = 0.0
            last_parameter_pair_difference = 0.0

            last_parameter_pair_difference = last['child_observation_value']['observation_value'] - \
                penultimate['child_observation_value']['observation_value']
            first_parameter_pair_difference = penultimate['child_observation_value']['observation_value'] - \
                antepentultimate['child_observation_value']['observation_value']

            latest_velocity = last_parameter_pair_difference / last_parameter_pair_time_elapsed
            penultimate_velocity = first_parameter_pair_difference / \
                first_parameter_pair_time_elapsed
            acceleration = (latest_velocity - penultimate_velocity) / \
                last_parameter_pair_time_elapsed
            return acceleration

def create_pairs(measurements_array: list = []):
    # test data
    """
    measurements = [{'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 25 Apr 1759 00:00:00 GMT', 'chronological_decimal_age': 0.038329911019849415, 'corrected_decimal_age': 0.038329911019849415, 'chronological_calendar_age': '2 weeks', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 4.111224921050807, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.0020115566532506, 'weight_centile': 84.18309943393204, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 09 May 1759 00:00:00 GMT', 'chronological_decimal_age': 0.07665982203969883, 'corrected_decimal_age': 0.07665982203969883, 'chronological_calendar_age': '4 weeks', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 4.699038339425533, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.002339620693291, 'weight_centile': 84.19102035307033, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 23 May 1759 00:00:00 GMT', 'chronological_decimal_age': 0.11498973305954825, 'corrected_decimal_age': 0.11498973305954825, 'chronological_calendar_age': '1 month, 1 week and 5 days', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 5.232213641808542, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.0045936184500082, 'weight_centile': 84.24537143099158, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 06 Jun 1759 00:00:00 GMT', 'chronological_decimal_age': 0.15331964407939766, 'corrected_decimal_age': 0.15331964407939766, 'chronological_calendar_age': '1 month, 3 weeks and 5 days', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 5.692927141647227, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.004963324529577, 'weight_centile': 84.25427448883711, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 20 Jun 1759 00:00:00 GMT', 'chronological_decimal_age': 0.19164955509924708, 'corrected_decimal_age': 0.19164955509924708, 'chronological_calendar_age': '2 months, 1 week and 2 days', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 6.099306464415924, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.007109988748447, 'weight_centile': 84.30590392040097, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 04 Jul 1759 00:00:00 GMT', 'chronological_decimal_age': 0.2299794661190965, 'corrected_decimal_age': 0.2299794661190965, 'chronological_calendar_age': '2 months, 3 weeks and 2 days', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 6.461379695081464, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.007475030461087, 'weight_centile': 84.31467244800477, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 18 Jul 1759 00:00:00 GMT', 'chronological_decimal_age': 0.2683093771389459, 'corrected_decimal_age': 0.2683093771389459, 'chronological_calendar_age': '3 months and 1 week', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 6.789203770743711, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.009650708766674, 'weight_centile': 84.36686671210703, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 01 Aug 1759 00:00:00 GMT', 'chronological_decimal_age': 0.3066392881587953, 'corrected_decimal_age': 0.3066392881587953, 'chronological_calendar_age': '3 months and 3 weeks', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 7.088501064489439, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.0108086749449121, 'weight_centile': 84.39459948388198, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 15 Aug 1759 00:00:00 GMT', 'chronological_decimal_age': 0.34496919917864477, 'corrected_decimal_age': 0.34496919917864477, 'chronological_calendar_age': '4 months', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 7.363720070832382, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.0126387519444007, 'weight_centile': 84.4383628580822, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}, {'birth_data': {'birth_date': 'Wed, 11 Apr 1759 00:00:00 GMT', 'gestation_weeks': 0, 'gestation_days': 0, 'estimated_date_delivery': 'None', 'estimated_date_delivery_string': '', 'sex': 'female'}, 'measurement_dates': {'observation_date': 'Wed, 29 Aug 1759 00:00:00 GMT', 'chronological_decimal_age': 0.38329911019849416, 'corrected_decimal_age': 0.38329911019849416, 'chronological_calendar_age': '4 months, 2 weeks and 4 days', 'corrected_calendar_age': '', 'corrected_gestational_age': {'corrected_gestation_weeks': None, 'corrected_gestation_days': None}, 'clinician_decimal_age_comment': 'Correction for gestational age is nolonger necessary after two years of age.', 'lay_decimal_age_comment': 'Your child is now old enough nolonger to need to take their prematurity into account when considering their growth.'}, 'child_measurement_value': {'height': None, 'weight': 7.614522747033926, 'bmi': 'None', 'ofc': None}, 'measurement_calculated_values': {'height_sds': 'None', 'height_centile': 'None', 'clinician_height_comment': '', 'lay_height_comment': '', 'weight_sds': 1.0139857964039922, 'weight_centile': 84.47052350872625, 'clinician_weight_comment': '', 'lay_weight_comment': '', 'bmi_sds': 'None', 'bmi_centile': 'None', 'clinician_bmi_comment': '', 'lay_bmi_comment': '', 'ofc_sds': 'None', 'ofc_centile': 'None', 'clinician_ofc_comment': '', 'lay_ofc_comment': ''}}]
    """
    parameter_list = []
    if len(measurements_array) < 2:
        return 'Not enough data'
    else:
        for measurement in measurements_array:
            if measurement:
                if measurement['child_measurement_value']['weight'] is not None:
                    parameter_list.append(measurement)

        if len(parameter_list) < 2:
            return f"There are not enough weight values to calculate a velocity."
        else:
            last = parameter_list[-1]
            penultimate = parameter_list[-2]
            penultimate_weight_sds_value = penultimate['measurement_calculated_values']['weight_sds']
            penultimate_decimal_age = penultimate['measurement_dates']['chronological_decimal_age']
            last_weight_sds_value = last['measurement_calculated_values']['weight_sds']
            last_decimal_age = last['measurement_dates']['chronological_decimal_age']
            return {
                "penultimate_weight_sds_value": penultimate_weight_sds_value,
                "penultimate_decimal_age": penultimate_decimal_age,
                "last_weight_sds_value": last_weight_sds_value,
                "last_decimal_age": last_decimal_age
            }

# centile creation

def nine_centiles(sex: str):
    t=[centile * 0.5 for centile in range(24)]
    requested_sd_scores=[-2.67, -2.0, -1.33, -0.67, 0, 0.67, 1.33, 2.0, 2.67]
    final_array=[]

    for index, requested_sd_score in enumerate(requested_sd_scores):
        return_ages_array=[]
        return_m_array=[]
        for index in range(len(t)-1):
            m=measurement_from_sds(
                reference=UK_WHO,
                requested_sds=requested_sd_score,
                measurement_method=WEIGHT,
                sex=sex,
                age=t[index]/12
            )
            return_m_array.append(m)
            return_ages_array.append(t[index]/12)
        final_array.append({
            "ages": return_ages_array,
            "observation_values": return_m_array
        })
    return final_array

# conditional weight gain functions

def conditional_weight_gain(z1, r, Z):
    """
    Weight velocity of the individual child cannot be predicted without comparison against reference data velocity since weight velocity is age dependent. This uses a correlation matrix to look up values against which to compare the rate at which the child is gaining or losing weight.
    The formula for conditional weight gain is: (z2 – r x z1) / √1-r^2
    Conditional reference charts to assess weight gain in British infants, T J Cole, Archives of Disease in Childhood 1995; 73: 8-16f
    """
    return z1 * r + Z * math.sqrt(1 - r**2)

# create a single thrive line

def create_thrive_line(t: list, z1: float, sex: str, target_centile: float = 5.0):
    # creates a single thrive line
    # accepts a list of ages against which the measurements are plotted
    # z1 refers to the starting SDS
    # target_centile refers to the velocity centile requested (defaults to 5th centile)

    zv=sds_for_centile(target_centile)
    observation_value=None

    observation_value=measurement_from_sds(
            reference=UK_WHO,
            requested_sds=z1,
            sex=sex,
            age=t[0]/12,
            measurement_method=WEIGHT
        )
    return_observation_values=[observation_value]
    cycle_sds=[z1]
    return_ages=[t[0]]
    z2=0.0

    for index in range(len(t)):
        observation_value=None
        # loop through the list of ages which are ordered and evenly spaced a month apart
        z_current = cycle_sds[index]

        if index < len(t)-1:
            t1, t2=t[index], t[index+1]
            # use the current and then next age in the list to look up the correlation r
            r=return_correlation(t1=t1, t2=t2, time_interval="months")
            # calculate the expected z, based on requested velocity centile (zv) for the next age in the list using r
            z2=conditional_weight_gain(z_current, r, zv)
        else:
            # this is the last item in the list
            t2 = t1
            z2=z_current

        # convert z2 to a measurement and add to the list against t2 in years
        observation_value = measurement_from_sds(
            reference=UK_WHO,
            requested_sds=z2,
            sex=sex,
            age=t2/12,
            measurement_method=WEIGHT
        )

        cycle_sds.append(z2)
        return_ages.append(t2/12)
        return_observation_values.append(observation_value)

    return {
        "zs": cycle_sds,
        "ages": return_ages,
        "observation_values": return_observation_values
    }

def create_thrive_lines(target_centile: float, sex: str):
    # Creates thrive lines for weights in the under 1s
    # Each thrive line requires a starting SDS and list of ages against
    # which the lines are plotted.
    # The centile_target refers to the velocity centile cut off at which
    # the line is drawn.

    time_blocks = [i for i in range(12)]

    centile_lines=nine_centiles(sex=sex)
    for index, centile_line in enumerate(centile_lines):
        # these are the 9 centile lines
        plt.plot(centile_line["ages"], centile_line["observation_values"], linestyle='--' if index % 2==0 else '-' , color="grey", linewidth=0.5)

    z=-25
    while z <= 25:
        thrive_line = create_thrive_line(
            t=time_blocks,
            z1=z,
            sex=sex,
            target_centile=target_centile)
        z+=0.67

        # loop through the zs and remove those outside the 99.6th and 0.4th centiles. Interpolate to generate those values on the lines
        ages, measurements = [], []
        counter=0
        while counter < len(thrive_line['zs'])-1:
            if (thrive_line['zs'][counter] >= 2.667 and thrive_line['zs'][counter+1] < 2.667):
                try:
                    interpolated_age=float(linear_interpolation(2.667, thrive_line['zs'][counter+1], thrive_line['zs'][counter], thrive_line['ages'][counter+1], thrive_line['ages'][counter]))
                    interpolated_measurement = measurement_from_sds(
                        reference=UK_WHO,
                        requested_sds=2.667,
                        measurement_method=WEIGHT,
                        sex=sex,
                        age=interpolated_age
                    )
                    measurements.append(interpolated_measurement)
                    ages.append(interpolated_age)
                except Exception:
                    print("exception")
                    pass
            elif (thrive_line['zs'][counter] >= -2.667 and thrive_line['zs'][counter+1] < -2.667):
                try:
                    interpolated_age=float(linear_interpolation(-2.667, thrive_line['zs'][counter+1], thrive_line['zs'][counter], thrive_line['ages'][counter+1], thrive_line['ages'][counter]))
                    interpolated_measurement = measurement_from_sds(
                        reference=UK_WHO,
                        requested_sds=-2.667,
                        measurement_method=WEIGHT,
                        sex=sex,
                        age=interpolated_age
                    )
                    measurements.append(interpolated_measurement)
                    ages.append(interpolated_age)
                except Exception:
                    print("another exception")
                    pass
            elif thrive_line['zs'][counter] > -2.667 and thrive_line['zs'][counter] < 2.667:
                measurements.append(thrive_line['observation_values'][counter])
                ages.append(thrive_line['ages'][counter])
            counter += 1

    #     x, y = ages, measurements
    #     # smoothed_measurements = UnivariateSpline(x,y) smoothed_measurements(x)
    #     if len(x) > 0 and len(y) > 0:
    #         plt.plot(x, y, color="green", linestyle='--', dashes=(15,2.5), linewidth=1.0)

    # plt.title('Thrive Lines', fontsize=16)
    # plt.show()

def return_correlation(t1, t2, time_interval: Literal["weeks", "months"]):
    # import the reference - the index of each row and column
    # relates to the number of weeks or months

    cwd = os.path.dirname(__file__)  # current location
    if time_interval == "weeks":
        if t1 > 53 or t2 > 53:
            return Exception("Data only available below 53 weeks of age")
        file_path = 'data_tables/uk_who_weight_correlation_matrices/weight_correlation_by_week.json'
    else:
        if t1 > 12 or t2 > 12:
            return Exception("Data only available below 12 months of age")
        file_path = 'data_tables/uk_who_weight_correlation_matrices/weight_correlation_by_month.json'

    final_file_path = os.path.join(cwd, file_path)
    with open(final_file_path, mode="r") as json_file:
        data=json.load(json_file)
        json_file.close()

    lowerIndexT1 = math.floor(t1)
    upperIndexT1 = lowerIndexT1+1
    lowerIndexT2 = math.floor(t2)
    upperIndexT2 = lowerIndexT2+1

    lowerT1lowerT2 = data[lowerIndexT1][str(lowerIndexT2)]
    lowerT1upperT2 = data[lowerIndexT1][str(upperIndexT2)]
    upperT1lowerT2 = data[upperIndexT1][str(lowerIndexT2)]
    upperT1upperT2 = data[upperIndexT1][str(upperIndexT2)]

    correlation = bilinear_interpolation(
            x=t1,
            y=t2,
            points=[
                (lowerIndexT1, lowerIndexT2, lowerT1lowerT2),
                (lowerIndexT1, upperIndexT2, lowerT1upperT2),
                (upperIndexT1, lowerIndexT2, upperT1lowerT2),
                (upperIndexT1, upperIndexT2, upperT1upperT2),
            ]
        )
    return correlation


def bilinear_interpolation(x, y, points):
    '''Interpolate (x,y) from values associated with four points.

    The four points are a list of four triplets:  (x, y, value).
    The four points can be in any order.  They should form a rectangle.

        >>> bilinear_interpolation(12, 5.5,
        ...                        [(10, 4, 100),
        ...                         (20, 4, 200),
        ...                         (10, 6, 150),
        ...                         (20, 6, 300)])
        165.0

    '''
    # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation
    # Thanks to Raymond Hettinger on Stack overflow for this solution: https://stackoverflow.com/questions/8661537/how-to-perform-bilinear-interpolation-in-python

    points = sorted(points)               # order points by x, then by y
    (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

    if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        raise ValueError('points do not form a rectangle')
    if not x1 <= x <= x2 or not y1 <= y <= y2:
        raise ValueError('(x, y) not within the rectangle')

    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)
