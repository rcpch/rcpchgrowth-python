from .constants import HEIGHT, MALE, FEMALE, UK_WHO, WHO, MINIMUM_PARENTAL_HEIGHT_CM, MAXIMUM_PARENTAL_HEIGHT_CM, REFERENCES, SEXES
from .global_functions import sds_for_measurement
"""
Functions to calculate mid-parental height

cf 
Tanner JM, Whitehouse RH, Takaishi M. Standards from birth to maturity for height, weight, height velocity, and weight velocity: British children, 1965. I. Arch Dis Child. 1966;41(219):454-471.
The strengths and limitations of parental heights as a predictor of attained height, Charlotte M Wright, Tim D Cheetham, Arch Dis Child 1999;81:257–260
"""

def mid_parental_height(maternal_height, paternal_height, sex):
    """
    Calculate mid-parental height
    
    maternal_height: Maternal height in cm (float)
    paternal_height: Paternal height in cm (float)
    sex: Sex of the child ('male' or 'female')
    return: Mid-parental height in cm (float)
    raises ValueError: If any input is invalid
    """
    # Validate sex
    if sex not in SEXES:
        raise ValueError(f"Sex must be '{MALE}' or '{FEMALE}', got '{sex}'")
    
    # Validate maternal_height
    if maternal_height is None:
        raise ValueError("Maternal height cannot be None. Please provide a height in cm.")
    if not isinstance(maternal_height, (int, float)):
        raise ValueError(f"Maternal height must be a number, got {type(maternal_height).__name__}")
    if maternal_height < MINIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Maternal height of {maternal_height} cm is below the minimum of {MINIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    if maternal_height > MAXIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Maternal height of {maternal_height} cm is above the maximum of {MAXIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    
    # Validate paternal_height
    if paternal_height is None:
        raise ValueError("Paternal height cannot be None. Please provide a height in cm.")
    if not isinstance(paternal_height, (int, float)):
        raise ValueError(f"Paternal height must be a number, got {type(paternal_height).__name__}")
    if paternal_height < MINIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Paternal height of {paternal_height} cm is below the minimum of {MINIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    if paternal_height > MAXIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Paternal height of {paternal_height} cm is above the maximum of {MAXIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    
    if sex == MALE:
        return (maternal_height + paternal_height + 13) / 2
    else:
        return (maternal_height + paternal_height - 13) / 2

def mid_parental_height_z(maternal_height, paternal_height, reference=UK_WHO):
    """
    Calculate mid-parental height standard deviation
    
    :param maternal_height: Maternal height in cm (float)
    :param paternal_height: Paternal height in cm (float)
    :param reference: Reference dataset to use (default: 'uk-who')
    :return: Mid-parental height z-score (float)
    :raises ValueError: If any input is invalid
    """
    # Validate reference
    if reference not in REFERENCES:
        raise ValueError(f"Reference must be one of {REFERENCES}, got '{reference}'")
    
    # Validate maternal_height
    if maternal_height is None:
        raise ValueError("Maternal height cannot be None. Please provide a height in cm.")
    if not isinstance(maternal_height, (int, float)):
        raise ValueError(f"Maternal height must be a number, got {type(maternal_height).__name__}")
    if maternal_height < MINIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Maternal height of {maternal_height} cm is below the minimum of {MINIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    if maternal_height > MAXIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Maternal height of {maternal_height} cm is above the maximum of {MAXIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    
    # Validate paternal_height
    if paternal_height is None:
        raise ValueError("Paternal height cannot be None. Please provide a height in cm.")
    if not isinstance(paternal_height, (int, float)):
        raise ValueError(f"Paternal height must be a number, got {type(paternal_height).__name__}")
    if paternal_height < MINIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Paternal height of {paternal_height} cm is below the minimum of {MINIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    if paternal_height > MAXIMUM_PARENTAL_HEIGHT_CM:
        raise ValueError(f"Paternal height of {paternal_height} cm is above the maximum of {MAXIMUM_PARENTAL_HEIGHT_CM} cm and is considered to be an error.")
    
    # convert parental heights to z-scores
    adult_age = 20.0
    if reference == WHO:
        adult_age = 19.0
    
    maternal_height_z = sds_for_measurement(reference=reference, age=adult_age, measurement_method=HEIGHT, observation_value=maternal_height, sex=FEMALE)
    paternal_height_z = sds_for_measurement(reference=reference, age=adult_age, measurement_method=HEIGHT, observation_value=paternal_height, sex=MALE)

    # take the means of the z-scores and apply the regression coefficient of 0.5 - simplifed: (MatHtz +PatHtz)/4
    mid_parental_height_z_score = (maternal_height_z + paternal_height_z) / 4.0

    return mid_parental_height_z_score

def expected_height_z_from_mid_parental_height_z(mid_parental_height_z):
    """
    Calculate expected height z score from mid-parental height z-score

    Ninety per cent of children had values within 1.4 SDS of their expected SDS (just over two
    centile spaces) and only 1% had values > 2 SDS (three centile spaces) below (cf Wright et al)
    """
    
    return mid_parental_height_z * 0.5

def lower_and_upper_limits_of_expected_height_z(mid_parental_height_z):
    """
    Calculate lower and upper limits of expected height z score from mid-parental height z-score
    Returns a tuple of (lower, upper) limits
    """
    
    return mid_parental_height_z - 1.4, mid_parental_height_z + 1.4