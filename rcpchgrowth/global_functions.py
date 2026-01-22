import json
import math
import scipy.stats as stats
from scipy.interpolate import interp1d
from .uk_who import uk_who_lms_array_for_measurement_and_sex
from .turner import turner_lms_array_for_measurement_and_sex
from .trisomy_21 import trisomy_21_lms_array_for_measurement_and_sex
from .cdc import cdc_lms_array_for_measurement_and_sex
from .trisomy_21_aap import trisomy_21_aap_lms_array_for_measurement_and_sex
from .who import who_lms_array_for_measurement_and_sex, who_csv_reference_data_for_age_and_sex
from .constants import *
from importlib import resources
from pathlib import Path
import pandas as pd

# from scipy import interpolate  #see below, comment back in if swapping interpolation method
# from scipy.interpolate import CubicSpline #see below, comment back in if swapping interpolation method
from .constants.reference_constants import (
    UK_WHO, TURNERS, 
    TRISOMY_21, 
    BMI, CDC, WEIGHT, HEIGHT, HEAD_CIRCUMFERENCE,
    TRISOMY_21_AAP, 
    WHO, 
    UK90_PRETERM,
    UK_WHO_INFANT, 
    UK_WHO_CHILD,
    UK90_CHILD,
    WHO_2006_INFANT,
    WHO_2006_CHILD,
    WHO_2007_CHILD,
    CDC_INFANT,
    CDC_CHILD,
    FENTON, 
    TRISOMY_21_AAP_INFANT, 
    TRISOMY_21_AAP_CHILD,
    UK_90_PRETERM_AGES,
    WHO_2006_UNDER_TWOS_AGES,
    UK_WHO_2006_OVER_TWOS_AGES,
    WHO_2006_OVER_TWOS_AGES,
    WHO_2007_AGES,
    UK90_AGES,
    CDC_TO_TWO_AGE,
    CDC_TO_THREE_AGE,
    CDC_TWO_TWENTY,
    TURNER_AGES,
    TRISOMY_21_AGES,
    TRISOMY_21_AAP_INFANT_AGES,
    TRISOMY_21_AAP_CHILD_AGES
    )

"""Public functions"""


def measurement_from_sds(
    reference: str,
    requested_sds: float,
    measurement_method: str,
    sex: str,
    age: float,
    default_youngest_reference: bool = False,
) -> float | None:

    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            age=age,
            measurement_method=measurement_method,
            sex=sex,
            default_youngest_reference=default_youngest_reference,
        )
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match, interpolate if none
    lms = fetch_lms(
        age=age, lms_value_array_for_measurement=lms_value_array_for_measurement
    )
    l = lms["l"]
    m = lms["m"]
    s = lms["s"]
    
    observation_value = None

    if reference == CDC and measurement_method == BMI:
        # CDC BMI references require a different method to calculate the centile
        # This is because the centile is calculated from the z-score using the cumulative distribution function
        # if the centile is below 95% (or the inverse if the centile is above 95%)
        # It takes the sigma value from the reference data and applies the cdf to the z-score
       
        sigma = lms["sigma"]
        if requested_sds <= 1.645: # 95th centile
            observation_value = m * (1 + l * s * requested_sds)**(1/l)
        else:
            # inverse of the cdf applied to the bmi percentile - 90 / 10,
            # then multiplied by the sigma value and added to the 95th centile
            p95 = m * (1 + l * s * 1.645)**(1/l) # 95th centile measurement
            centile = stats.norm.cdf(requested_sds) * 100 # convert z-score to centile
            observation_value = stats.norm.ppf((centile - 90)/10) * sigma + p95
    # elif reference == WHO and measurement_method == 'bmi':
    #     # WHO BMI references require a different method to calculate the measurement if the requested SDS is below -3 or above +3 SDS
    #     # This involves calculating the measurement first to determine if it is below -3 or above +3 SDS
    #     is_beyond_three_sds = abs(requested_sds) > 3
    #     if is_beyond_three_sds:
    #         if requested_sds > 3:
    #             sd3pos = measurement_for_z(z=3, l=l, m=m, s=s)
    #             sd2pos = measurement_for_z(z=2, l=l, m=m, s=s)
    #             observation_value = sd3pos + (requested_sds - 3) * (sd3pos - sd2pos)
    #         elif requested_sds < -3:
    #             sd3neg = measurement_for_z(z=-3, l=l, m=m, s=s)
    #             sd2neg = measurement_for_z(z=-2, l=l, m=m, s=s)
    #             observation_value = sd3neg + (requested_sds + 3) * (sd2neg - sd3neg)
    #     else:
    #         try:
    #             observation_value = measurement_for_z(z=requested_sds, l=l, m=m, s=s)
    #         except Exception as e:
    #             print(f"measurement_from_sds exception {e} - age: {age}, l: {l}, m: {m}, s: {s}, requested_sds: {requested_sds} lms: {lms}")
    #             return None
    else:
        # all other references use the standard method
        try:
            observation_value = measurement_for_z(z=requested_sds, l=l, m=m, s=s)
        except Exception as e:
            print(f"measurement_from_sds exception {e} - age: {age}, l: {l}, m: {m}, s: {s}, requested_sds: {requested_sds} lms: {lms}")
            return None
    
    if observation_value is not None:
        observation_value = round(observation_value, 4)
    
    return observation_value


def sds_for_measurement(
    reference: str,
    age: float,
    measurement_method: str,
    observation_value: float,
    sex: str,
) -> float:

    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            age=age,
            measurement_method=measurement_method,
            sex=sex,
            default_youngest_reference=False,  # The oldest child reference should always be selected for SDS calculation
        )
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match.
    # There will always be an age match in the under 5s WHO, or under 4s UK-WHO and therefore no interpolation is required
    # However, for WHO references above 5 years, interpolation will be linear, whereas for all others interpolation will be cubic
    lms = fetch_lms(
        age=age, lms_value_array_for_measurement=lms_value_array_for_measurement, interpolation_override=reference==WHO
    )
    l = lms["l"]
    m = lms["m"]
    s = lms["s"]

    # this calculation is different for CDC BMI references and uses the
    # cumulative distribution function to calculate the z-score
    # (if the centile is below 95% (or the inverse if the centile is above 95%)
    if reference == CDC and measurement_method == BMI:
        sigma = lms["sigma"]
        if observation_value > m * (1 + l * s * 1.645)**(1/l):
            # above 95th centile
            p95 = m * (1 + l * s * 1.645)**(1/l)
            centile = stats.norm.cdf((observation_value - p95) / sigma)*10 + 90
            z = stats.norm.ppf(centile/100)
            return z
    if reference == WHO and measurement_method == 'bmi':
        # WHO BMI references require a different method to calculate the z-score if the measurement is below -3 or above +3 SDS
        # This involves calculating the z score first to determine if it is below -3 or above +3 SDS
        z = z_score(l=l, m=m, s=s, observation=observation_value)
        is_beyond_three_sds = abs(z) > 3
        if is_beyond_three_sds:
            # if the z score is below -3 or above +3 SDS, the calculation is different
            # see WHO Website: https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf?sfvrsn=c2ff6a95_4
            if z > 3:
                sd3pos = m * (1 + l * s * 3)**(1/l)
                sd2pos = m * (1 + l * s * 2)**(1/l)
                z= 3 + ((observation_value - sd3pos) / (sd3pos - sd2pos))
            elif z < -3:
                sd3neg = m * (1 + l * s * -3)**(1/l)
                sd2neg = m * (1 + l * s * -2)**(1/l)
                z= -3 + ((observation_value - sd3neg) / (sd2neg - sd3neg))
        return z

    return z_score(l=l, m=m, s=s, observation=observation_value)


def percentage_median_bmi(
    reference: str, age: float, actual_bmi: float, sex: str
) -> float | None:
    """
    public method
    This returns a child"s BMI expressed as a percentage of the median value for age and sex.
    It is used widely in the assessment of malnutrition particularly in children and young people with eating disorders.
    It accepts the reference ('uk-who', 'turners-syndrome' or 'trisomy-21')
    """

    # fetch the LMS values for the requested measurement
    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            measurement_method=BMI,
            sex=sex,
            age=age,
            default_youngest_reference=False,
        )  # The oldest reference should always be chosen for this calculation
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match, interpolate if none
    try:
        lms = fetch_lms(
            age=age, lms_value_array_for_measurement=lms_value_array_for_measurement
        )
    except LookupError as err:
        print(f"percentage median BMI lookup exception: {err}")
        return None

    m = lms["m"]  # this is the median BMI

    percent_median_bmi = (actual_bmi / m) * 100.0
    return percent_median_bmi


def generate_centile(
    z: float,
    centile: float,
    measurement_method: str,
    sex: str,
    reference: str,
    reference_name: str,
    is_sds: bool = False,
) -> list:
    """
    Generates a centile curve for a given reference.
    Takes the z-score equivalent of the centile, the centile to be used as a label, the sex and measurement method.
    Accepts the LMS values for the measurement as a list of dictionaries.
    If the list is empty, the function will return an empty list.
    If default_youngest_reference is True, the youngest reference will be used for overlap values - for example infant and child data sets in the UK-WHO and CDC references have duplicate ages at disjunction ages - 
    this ensures that the centile line runs up to the disjunction.

    To keep the dataset as small as possible, the function will skip non-integer ages above 3 years, but will include all ages below 3 years that are in the LMS list. 
    Paradoxically, the fewer data points, the smoother the curve, though for periods of rapid growth, more data points are needed.
    """


    # if this is an sds line, the label reflects the sds value. The default is to reflect the centile
    label_value = centile
    if is_sds:
        label_value = round(z, 3)

    centile_measurements = []

    # iterate through ages from 23 weeks to 20 years

    if reference == UK_WHO:
        if reference_name == UK90_PRETERM:
            AGES = UK_90_PRETERM_AGES
        elif reference_name == UK_WHO_INFANT:
            AGES = WHO_2006_UNDER_TWOS_AGES
        elif reference_name ==  UK_WHO_CHILD:
            AGES = UK_WHO_2006_OVER_TWOS_AGES
        elif reference_name == UK90_CHILD:
            AGES = UK90_AGES
    
    elif reference == WHO:
        if reference_name ==WHO_2006_INFANT:
            AGES = WHO_2006_UNDER_TWOS_AGES
        elif reference_name == WHO_2006_CHILD:
            AGES = WHO_2006_OVER_TWOS_AGES
        elif reference_name == WHO_2007_CHILD:
            AGES = WHO_2007_AGES

    elif reference == CDC:
        if reference_name == CDC_INFANT:
            if measurement_method == HEAD_CIRCUMFERENCE:
                AGES = CDC_TO_THREE_AGE
            elif measurement_method == HEIGHT or measurement_method == WEIGHT:
                AGES = WHO_2006_UNDER_TWOS_AGES
            else:
                AGES = CDC_TO_TWO_AGE # should be redundant as no BMI data in CDC_INFANT
        elif reference_name == CDC_CHILD:
            AGES = CDC_TWO_TWENTY
        elif reference_name == FENTON:
            AGES = []
    
    elif reference == TURNERS:
         AGES = TURNER_AGES
    
    elif reference == TRISOMY_21:
        AGES = TRISOMY_21_AGES
    
    elif reference == TRISOMY_21_AAP:
        if reference_name==TRISOMY_21_AAP_INFANT:
            AGES = TRISOMY_21_AAP_INFANT_AGES
        elif reference_name==TRISOMY_21_AAP_CHILD:
            AGES = TRISOMY_21_AAP_CHILD_AGES
    
    def should_default_to_youngest_reference(age: float, reference_name: str):
        if reference_name == UK90_PRETERM:
            if age == 0.038329911:
                return True
        if reference_name == UK_WHO_INFANT:
            if age == 2:
                return True
        elif reference_name == CDC_INFANT:
            if age == 0.038329911:
                return True
            elif age == 2:
                return True
        elif reference_name == UK_WHO_CHILD:
            if age == 4:
                return True
        elif reference_name == WHO_2006_INFANT:
            if age == 0.038329911:
                return True
            if age == 2:
                return True
        elif reference_name == WHO_2006_CHILD:
            if age == 5:
                return True
        elif reference_name == TRISOMY_21_AAP_INFANT:
            if age == 3:
                return True
        return False

    for age in AGES:
        default_youngest_reference = False
        if should_default_to_youngest_reference(age, reference_name):
            default_youngest_reference = True

        try:
            measurement = measurement_from_sds(
                reference=reference,
                measurement_method=measurement_method,
                requested_sds=round(z, 4),
                sex=sex,
                age=age,
                default_youngest_reference=default_youngest_reference,
            )
        except Exception as err:
            print(err)
            measurement = None  #
            continue
        
        if measurement is not None:
            measurement = round(measurement, 4)

        value = create_data_point(
            age=age, measurement=measurement, label_value=label_value
        )
        centile_measurements.append(value)

    return centile_measurements

"""
*** PUBLIC FUNCTIONS THAT CONVERT BETWEEN CENTILE AND SDS
"""


def sds_for_centile(centile: float) -> float:
    """
    converts a centile (supplied as a percentage) using the scipy package to an SDS.
    """
    sds = stats.norm.ppf(centile / 100)
    return sds


def rounded_sds_for_centile(centile: float) -> float:
    """
    converts a centile (supplied as a percentage) using the scipy package to the nearest 2/3 SDS.
    """
    sds = stats.norm.ppf(centile / 100)
    if sds == 0:
        return sds
    else:
        rounded_to_nearest_two_thirds = round(sds / (2 / 3))
        return rounded_to_nearest_two_thirds * (2 / 3)


def centile(z_score: float):
    """
    Converts a Z Score to a p value (2-tailed) using the SciPy library, which it returns as a percentage
    """
    try:
        centile = stats.norm.cdf(z_score) * 100
        return centile
    except Exception as err:
        raise Exception(err)


"""
Private Functions
These are essential to the public functions but are not needed outside this file
"""


def create_data_point(age: float, measurement: float, label_value: str):
    # creates a data point
    if measurement is not None:
        try:
            rounded = round(measurement, 4)
        except Exception as e:
            print(f"create datapoint error: {e} for {measurement}")
            return
    else:
        rounded = None
    value = {"l": label_value, "x": round(age, 4), "y": rounded}
    return value

def who_z_for_measurement(
    measurement_method: str, age_days: float, sex: str, observation_value: float):
    """
    This function calculates the z-score for a given observation value based on WHO reference data.
    It uses the WHO reference data for the specified age and imports  the reference data from a CSV file.
    It performs linear interpolation if the age is not found in the reference data.
    It returns the z-score for the observation value.
    If the age is below 1856 days (5 years), it uses the "Day" column for lookup.
    If the age is above 1856 days, it uses the "Month" column for lookup.
    If the age is not found in the reference data, it performs linear interpolation between the nearest months.
    """
    match = True
    
    who_data_df = who_csv_reference_data_for_age_and_sex(
        age_days=age_days, measurement_method=measurement_method, sex=sex)
    
    if age_days <= 1828:
        # there is an L, M and S value for each day in the first 5 years of life
        lookup_row = who_data_df.loc[who_data_df["Day"] == age_days]

    else:
        age_months = age_days / 30.4375  # convert days to months
        if who_data_df.loc[who_data_df["Month"] == age_months].empty:
            # If the month is not found, use the nearest month below
            match = False
            
            row_below_index = who_data_df.loc[who_data_df["Month"] < age_months, "Month"].idxmax()
            row_above_index = row_below_index + 1
            if row_below_index is None or row_above_index is None:
                raise LookupError(f"Age {int(age_days / 30.4375)} months not found in WHO data, no interpolation possible")
            
            l = linear_interpolation(age=age_months, age_one_below=who_data_df.loc[row_below_index, "Month"], age_one_above=who_data_df.loc[row_above_index, "Month"],
                                     parameter_one_below=who_data_df.loc[row_below_index, "L"],
                                     parameter_one_above=who_data_df.loc[row_above_index, "L"])
            m = linear_interpolation(age=age_months, age_one_below=who_data_df.loc[row_below_index, "Month"], age_one_above=who_data_df.loc[row_above_index, "Month"],
                                     parameter_one_below=who_data_df.loc[row_below_index, "M"],
                                     parameter_one_above=who_data_df.loc[row_above_index, "M"])
            s = linear_interpolation(age=age_months, age_one_below=who_data_df.loc[row_below_index, "Month"], age_one_above=who_data_df.loc[row_above_index, "Month"],
                                     parameter_one_below=who_data_df.loc[row_below_index, "S"],
                                     parameter_one_above=who_data_df.loc[row_above_index, "S"])
        else:
            # There is an exact match for the month in the reference data
            lookup_row = who_data_df.loc[who_data_df["Month"] == age_months]

    if match:
        l = lookup_row["L"].values[0]
        m = lookup_row["M"].values[0]
        s = lookup_row["S"].values[0]

    return z_score(l=l, m=m, s=s, observation=observation_value)


"""
***** INTERPOLATION FUNCTIONS *****
"""


def cubic_interpolation(
    age: float,
    age_one_below: float,
    age_two_below: float,
    age_one_above: float,
    age_two_above: float,
    parameter_two_below: float,
    parameter_one_below: float,
    parameter_one_above: float,
    parameter_two_above: float,
) -> float:
    """
    See sds function. This method tests if the age of the child (either corrected for prematurity or chronological) is at a threshold of the reference data
    This method is specific to the UK-WHO data set.
    """

    cubic_interpolated_value = 0.0

    t = 0.0  # actual age ///This commented function is Tim Cole"s used in LMSGrowth to perform cubic interpolation - 50000000 loops, best of 5: 7.37 nsec per loop
    tt0 = 0.0
    tt1 = 0.0
    tt2 = 0.0
    tt3 = 0.0

    t01 = 0.0
    t02 = 0.0
    t03 = 0.0
    t12 = 0.0
    t13 = 0.0
    t23 = 0.0

    t = age

    tt0 = t - age_two_below
    tt1 = t - age_one_below
    tt2 = t - age_one_above
    tt3 = t - age_two_above

    t01 = age_two_below - age_one_below
    t02 = age_two_below - age_one_above
    t03 = age_two_below - age_two_above

    t12 = age_one_below - age_one_above
    t13 = age_one_below - age_two_above
    t23 = age_one_above - age_two_above

    cubic_interpolated_value = (
        parameter_two_below * tt1 * tt2 * tt3 / t01 / t02 / t03
        - parameter_one_below * tt0 * tt2 * tt3 / t01 / t12 / t13
        + parameter_one_above * tt0 * tt1 * tt3 / t02 / t12 / t23
        - parameter_two_above * tt0 * tt1 * tt2 / t03 / t13 / t23
    )

    # prerequisite arrays for either of below functions
    # xpoints = [age_two_below, age_one_below, age_one_above, age_two_above]
    # ypoints = [parameter_two_below, parameter_one_below, parameter_one_above, parameter_two_above]

    # this is the scipy cubic spline interpolation function...
    # cs = CubicSpline(xpoints,ypoints,bc_type="natural")
    # cubic_interpolated_value = cs(age) # this also works, but not as accurate: 50000000 loops, best of 5: 7.42 nsec per loop

    # this is the scipy splrep function
    # tck = interpolate.splrep(xpoints, ypoints)
    # cubic_interpolated_value = interpolate.splev(age, tck)   #Matches Tim Cole"s for accuracy but slower: speed - 50000000 loops, best of 5: 7.62 nsec per loop

    return cubic_interpolated_value


def linear_interpolation(
    age: float,
    age_one_below: float,
    age_one_above: float,
    parameter_one_below: float,
    parameter_one_above: float,
) -> float:
    """
    See sds function. This method is to do linear interpolation of L, M and S values for children whose ages are at the threshold of the reference data, making cubic interpolation impossible
    """

    linear_interpolated_value = 0.0

    # linear_interpolated_value = parameter_one_above + (((decimal_age - age_below)*parameter_one_above-parameter_one_below))/(age_above-age_below)
    x_array = [age_one_below, age_one_above]
    y_array = [parameter_one_below, parameter_one_above]
    intermediate = interp1d(x_array, y_array)
    linear_interpolated_value = intermediate(age)
    return linear_interpolated_value


"""
***** DO THE CALCULATIONS *****
"""


def measurement_for_z(z: float, l: float, m: float, s: float) -> float:
    """
    Returns a measurement for a z score, L, M and S
    x = M (1 + L S z)^(1/L) where L is not 0
    Note, in some circumstances, 1 + l * s * z will be negative, and
    it will not be possible to calculate a power.
    In these circumstances, None is returned
    When L is 0, the calculation is x = M e^(S z)
    """
    measurement_value = 0.0
    if l != 0.0:
        first_step = 1 + (l * s * z)
        exponent = 1 / l
        if first_step < 0:
            return None
        try:
            measurement_value = (first_step**exponent) * m
        except Exception as e:
            print("measurement_for_z error: {e}")
            return
    else:
        measurement_value = math.exp(s * z) * m
    return measurement_value


def z_score(l: float, m: float, s: float, observation: float):
    """
    Converts the (age-specific) L, M and S parameters into a z-score
    """
    sds = 0.0
    if l != 0.0:
        sds = (((observation / m) ** l) - 1) / (l * s)
    else:
        sds = math.log(observation / m) / s
    return sds


"""
***** LOOKUP FUNCTIONS *****
"""


def nearest_lowest_index(lms_array: list, age: float) -> int:
    """
    loops through the array of LMS values and returns either
    the index of an exact match or the lowest nearest decimal age
    """
    lowest_index = 0
    for num, lms_element in enumerate(lms_array):
        reference_age = lms_element["decimal_age"]
        if round(reference_age, 4) == round(age, 4):
            lowest_index = num
            break
        else:
            if lms_element["decimal_age"] < age:
                lowest_index = num
    return lowest_index


def fetch_lms(age: float, lms_value_array_for_measurement: list, interpolation_override: bool=False):
    """
    Returns the LMS for a given age, and sigma if present (CDC BMI references). If there is no exact match in the reference
    an interpolated LMS is returned. Cubic interpolation is used except at the fringes of the
    reference where linear interpolation is used.
    It accepts the age and a python list of the LMS values for that measurement_method and sex.
    """
    age_matched_index = nearest_lowest_index(
        lms_value_array_for_measurement, age
    )  # returns nearest LMS for age

    # test for exact match
    rounded_age = round(age, 4)
    matched_age = round(lms_value_array_for_measurement[age_matched_index]["decimal_age"],4)
    if  rounded_age == matched_age:
        # there is an exact match in the data with the requested age
        l = lms_value_array_for_measurement[age_matched_index]["L"]
        m = lms_value_array_for_measurement[age_matched_index]["M"]
        s = lms_value_array_for_measurement[age_matched_index]["S"]

        if "sigma" in lms_value_array_for_measurement[age_matched_index]:
            # CDC BMI references have an additional sigma value
            sigma = lms_value_array_for_measurement[age_matched_index]["sigma"]
            return {"l": l, "m": m, "s": s, "sigma": sigma}
    else:
        # there has not been an exact match in the reference data
        # Interpolation will be required.
        # The age_matched_index is one below the age supplied. There
        # needs to be a value below that, and two values above the supplied age,
        # for cubic interpolation to be possible.
        age_one_below = lms_value_array_for_measurement[age_matched_index][
            "decimal_age"
        ]
        age_one_above = lms_value_array_for_measurement[age_matched_index + 1][
            "decimal_age"
        ]
        parameter_one_below = lms_value_array_for_measurement[age_matched_index]
        parameter_one_above = lms_value_array_for_measurement[age_matched_index + 1]

        if (
            age_matched_index >= 1
            and age_matched_index < len(lms_value_array_for_measurement) - 2
            and "sigma" not in lms_value_array_for_measurement[age_matched_index] # CDC BMI references have an additional sigma value
            # and CDC only use linear interpolation
            and interpolation_override is False
        ):
            # cubic interpolation is possible
            age_two_below = lms_value_array_for_measurement[age_matched_index - 1][
                "decimal_age"
            ]
            age_two_above = lms_value_array_for_measurement[age_matched_index + 2][
                "decimal_age"
            ]
            parameter_two_below = lms_value_array_for_measurement[age_matched_index - 1]
            parameter_two_above = lms_value_array_for_measurement[age_matched_index + 2]

            l = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["L"],
                parameter_one_below=parameter_one_below["L"],
                parameter_one_above=parameter_one_above["L"],
                parameter_two_above=parameter_two_above["L"],
            )
            m = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["M"],
                parameter_one_below=parameter_one_below["M"],
                parameter_one_above=parameter_one_above["M"],
                parameter_two_above=parameter_two_above["M"],
            )
            s = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["S"],
                parameter_one_below=parameter_one_below["S"],
                parameter_one_above=parameter_one_above["S"],
                parameter_two_above=parameter_two_above["S"],
            )
            if "sigma" in lms_value_array_for_measurement[age_matched_index]:
                # CDC BMI references have an additional sigma value
                sigma = cubic_interpolation(
                    age=age,
                    age_one_below=age_one_below,
                    age_two_below=age_two_below,
                    age_one_above=age_one_above,
                    age_two_above=age_two_above,
                    parameter_two_below=parameter_two_below["sigma"],
                    parameter_one_below=parameter_one_below["sigma"],
                    parameter_one_above=parameter_one_above["sigma"],
                    parameter_two_above=parameter_two_above["sigma"],
                )
                return {"l": l, "m": m, "s": s, "sigma": sigma}
        else:
            # we are at the thresholds of this reference or are using CDC. Only linear interpolation is possible
            l = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["L"],
                parameter_one_above=parameter_one_above["L"],
            )
            m = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["M"],
                parameter_one_above=parameter_one_above["M"],
            )
            s = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["S"],
                parameter_one_above=parameter_one_above["S"],
            )
            if "sigma" in lms_value_array_for_measurement[age_matched_index]:
                # CDC BMI references have an additional sigma value
                sigma = linear_interpolation(
                    age=age,
                    age_one_below=age_one_below,
                    age_one_above=age_one_above,
                    parameter_one_below=parameter_one_below["sigma"],
                    parameter_one_above=parameter_one_above["sigma"],
                )
                return {"l": l, "m": m, "s": s, "sigma": sigma}
    
    return {"l": l, "m": m, "s": s}


def lms_value_array_for_measurement_for_reference(
    reference: str,
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False,
) -> list:
    """
    This is a private function which returns the LMS array for measurement_method and sex and reference
    It accepts the reference ('uk-who', 'turners-syndrome', 'trisomy-21', 'cdc')
    If the UK-WHO reference is requested, it is possible to be select the younger reference for overlap values,
    using the default_youngest_reference flag.
    """

    if reference == UK_WHO:
        try:
            lms_value_array_for_measurement = uk_who_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference,
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == WHO:
        try:
            lms_value_array_for_measurement = who_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference,
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TURNERS:
        try:
            lms_value_array_for_measurement = turner_lms_array_for_measurement_and_sex(
                measurement_method=measurement_method, sex=sex, age=age
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TRISOMY_21:
        try:
            lms_value_array_for_measurement = (
                trisomy_21_lms_array_for_measurement_and_sex(
                    measurement_method=measurement_method, sex=sex, age=age
                )
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == CDC:
        try:
            lms_value_array_for_measurement = cdc_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TRISOMY_21_AAP:
        try:
            lms_value_array_for_measurement = trisomy_21_aap_lms_array_for_measurement_and_sex(
                age=age, measurement_method=measurement_method, sex=sex, default_youngest_reference=default_youngest_reference)
        except LookupError as error:
            raise LookupError(error)
    else:
        raise ValueError("No or incorrect reference supplied")
    return lms_value_array_for_measurement

"""
WHO and UK-WHO parse as JSON from daily LMS values - One time use functions
"""

def create_daily_lms_tables_for_measurement_method_and_sex_uk_who_for_age_group(age_group):
    """
    Create daily LMS tables for all measurement methods and both sexes using the UK-WHO reference data.
    """
    from .constants import SEXES
    for sex in SEXES:
        for measurement_method in [WEIGHT, HEIGHT, HEAD_CIRCUMFERENCE, BMI]:
            create_daily_lms_values_for_uk_who(measurement_method=measurement_method, sex=sex, age_group=age_group)

def create_daily_lms_values_for_uk_who(measurement_method, sex, age_group, interpolation_override=False):
    """
    Function to test the LMS values for the UK-WHO reference data against the WHO standard for the ages 0-2 years.
    age group must be one of ['neonate', 'infant', 'preschool', 'child']
    """
    age=0
    if age_group not in ['neonate', 'infant', 'preschool', 'child']:
        raise ValueError(f"Invalid age group: {age_group}. Must be one of ['neonate', 'infant', 'preschool', 'child'].")
    if age_group == "neonate":
        age = -0.05
        start_age = TWENTY_THREE_WEEKS_GESTATION
        end_age = 0.038329911 # 14 days
        acknowledgement_text = "UK 1990 reference data, reanalysed 2009."
    elif age_group == "infant":
        acknowledgement_text = "World Health Organisation Multicentre Growth Reference Standards (WHO MGRS) (2006/2007)"
        age = 0.5
        start_age, end_age = 0.038329911, 2
    elif age_group == "preschool":
        acknowledgement_text = "World Health Organisation Multicentre Growth Reference Standards (WHO MGRS) (2006/2007)"
        age = 2.5
        start_age, end_age = 2, 4
    elif age_group == "child":
        acknowledgement_text = "UK 1990 reference data, reanalysed 2009."
        age = 4.5
        start_age, end_age = 4, 23

    # fetch the LMS values for the UK-WHO reference data for the specified measurement and sex
    try:
        lms_value_array = lms_value_array_for_measurement_for_reference(
            reference=UK_WHO,
            age=age,
            measurement_method=measurement_method,
            sex=sex,
            default_youngest_reference=True,  # The youngest reference should always be chosen for this calculation
        )
    except LookupError as err:
        print(f"Error: {err}")
        return

    # create an empty dataframe to store the results
    results_df = pd.DataFrame(columns=["age", "l", "m", "s"])
    data = []

    json_structure = {
        "acknowledgement": acknowledgement_text,
        "age_group": age_group,
        "start_age": start_age,
        "end_age": end_age,
        "measurement_method": measurement_method,
        "sex": sex,
        "data": []
    }
    
    age = start_age
    while age <= end_age:
        try:
            lms = fetch_lms(
                age=age,
                lms_value_array_for_measurement=lms_value_array, interpolation_override=interpolation_override
            )
            l = lms["l"]
            m = lms["m"]
            s = lms["s"]
            # append the results to the dataframe
            data.append({
                "decimal_age": float(age),
                "l": float(l),
                "m": float(m),
                "s": float(s)
            })
        except Exception as e:
            age += 1/365.25
            print(f"Error fetching LMS values for age {age*365.25} days - {measurement_method}")
            continue
        age += 1/365.25

    json_structure["data"] = data

    # save the results to a JSON file
    with open(Path(resources.files("rcpchgrowth") / f"data_tables/uk-who_resources/uk_who_{age_group}_{sex}_{measurement_method}_{'linear' if interpolation_override else 'cubic'}_daily_lms.json"), "w") as json_file:
        json.dump(json_structure, json_file)

    # save the results to a CSV file
    # results_df = pd.DataFrame(data)
    # results_df.to_csv(Path(resources.files("rcpchgrowth") / f"uk_who_{age_group}_{sex}_{measurement_method}_{'linear' if interpolation_override else 'cubic'}_daily_lms.csv"), index=False)

# ...existing imports...
from importlib import resources
from pathlib import Path
import json
import pandas as pd
# ...existing code...

def build_who_json(individual_files: bool = True):
    """
    Build WHO LMS JSON.

    - individual_files=True:
        Write per-file JSONs under rcpchgrowth/data_tables/who/:
          who_under_five_{sex}_{measurement}.json (from 2006 CSV)
          who_over_five_{sex}_{measurement}.json (from 2007 CSV, if available)

    - individual_files=False:
        Write three combined files under rcpchgrowth/data_tables/who/:
          who_infants.json        # decimal_age <= 2
          who_children.json       # 2 <= decimal_age <= 5
          who_2007_children.json  # decimal_age >= 5
    """
    WHO_ACK = "World Health Organisation Multicentre Growth Reference Standards (WHO MGRS) (2006/2007)"
    measurements = ["height", "weight", "bmi", "ofc"]

    data_root = resources.files("rcpchgrowth.data_tables")
    out_dir = Path(str(data_root.joinpath("who")))
    out_dir.mkdir(parents=True, exist_ok=True)

    def to_records(df: pd.DataFrame) -> list[dict]:
        return json.loads(df.to_json(orient="records"))

    def standardize(df: pd.DataFrame | None) -> pd.DataFrame | None:
        if df is None or df.empty:
            return None
        df = df.copy()
        if "Day" in df.columns:
            df = df.rename(columns={"Day": "decimal_age"})
            df["decimal_age"] = df["decimal_age"].astype(float) / 365.25
        elif "Month" in df.columns:
            df["decimal_age"] = df["Month"].astype(float) / 12.0
        cols = [c for c in ["decimal_age", "L", "M", "S"] if c in df.columns]
        return df[cols].astype(float)

    written = []

    if not individual_files:
        infants_payload = {"measurement": {"acknowledgement_text": WHO_ACK}}
        children_payload = {"measurement": {"acknowledgement_text": WHO_ACK}}
        who2007_payload = {"measurement": {"acknowledgement_text": WHO_ACK}}
        for m in measurements:
            infants_payload["measurement"][m] = {"male": [], "female": []}
            children_payload["measurement"][m] = {"male": [], "female": []}
            who2007_payload["measurement"][m] = {"male": [], "female": []}

    for measurement in measurements:
        for sex in SEXES:
            try:
                under_df = who_csv_reference_data_for_age_and_sex(age_days=0, sex=sex, measurement_method=measurement)
            except Exception:
                under_df = None
            try:
                # ensure WHO 2007 (>5y) is selected
                over_df = who_csv_reference_data_for_age_and_sex(age_days=1831, sex=sex, measurement_method=measurement)
            except Exception:
                over_df = None

            under_std = standardize(under_df)
            over_std = standardize(over_df)

            if individual_files:
                if under_std is not None:
                    out = {
                        "sex": sex,
                        "measurement_method": measurement,
                        "acknowledgement_text": WHO_ACK,
                        "data": to_records(under_std),
                    }
                    p = out_dir / f"who_under_five_{sex}_{measurement}.json"
                    with open(p, "w") as f:
                        json.dump(out, f, indent=2)
                    written.append(p)
                if over_std is not None:
                    out = {
                        "sex": sex,
                        "measurement_method": measurement,
                        "acknowledgement_text": WHO_ACK,
                        "data": to_records(over_std),
                    }
                    p = out_dir / f"who_over_five_{sex}_{measurement}.json"
                    with open(p, "w") as f:
                        json.dump(out, f, indent=2)
                    written.append(p)
            else:
                # Split: infants (<=2), children (2–5], >5 (WHO 2007 monthly only)
                if under_std is not None:
                    infants_part = under_std[under_std["decimal_age"] <= 2.0]
                    children_part = under_std[
                        (under_std["decimal_age"] >= 2.0) & (under_std["decimal_age"] <= 5.0)
                    ]
                else:
                    infants_part = pd.DataFrame(columns=["decimal_age", "L", "M", "S"])
                    children_part = pd.DataFrame(columns=["decimal_age", "L", "M", "S"])

                # Only take >= 5.0 from the monthly (WHO 2007) table to create overlap at 5.0 without extra daily rows
                if over_std is not None:
                    over5_part = over_std[over_std["decimal_age"] >= 5.0]
                else:
                    over5_part = pd.DataFrame(columns=["decimal_age", "L", "M", "S"])

                infants_payload["measurement"][measurement][sex] = to_records(
                    infants_part.sort_values("decimal_age", kind="stable")
                ) if not infants_part.empty else []

                children_payload["measurement"][measurement][sex] = to_records(
                    children_part.sort_values("decimal_age", kind="stable")
                ) if not children_part.empty else []

                who2007_payload["measurement"][measurement][sex] = to_records(
                    over5_part.sort_values("decimal_age", kind="stable")
                ) if not over5_part.empty else []

    if not individual_files:
        p1 = out_dir / "who_infants.json"
        p2 = out_dir / "who_children.json"
        p3 = out_dir / "who_2007_children.json"
        with open(p1, "w") as f:
            json.dump(infants_payload, f, indent=2)
        with open(p2, "w") as f:
            json.dump(children_payload, f, indent=2)
        with open(p3, "w") as f:
            json.dump(who2007_payload, f, indent=2)
        return {"infants": p1, "children": p2, "children_2007": p3}

    return written