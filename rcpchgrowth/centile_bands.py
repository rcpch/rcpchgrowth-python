# imports from rcpchgrowth
from .constants import BMI, HEAD_CIRCUMFERENCE,CENTILE_FORMATS,THREE_PERCENT_CENTILE_COLLECTION,COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION 
from .global_functions import rounded_sds_for_centile


# Recommendations from Project board for reporting Centiles

# Lower limit	Upper limit	Centile band	Weight,  Height, Head	BMI
# 	<-6 		Probable error	Probable error
# -6.00	-2.84	Below 0.4th	Below normal range	Very thin
# -2.84	-2.50	0.4th 		Low BMI
# -2.50	-2.17	0.4th-2nd		Low BMI
# -2.17	-1.83	2nd		
# -1.83	-1.50	2nd -9th		
# -1.50	-1.16	9th		
# -1.16	-0.84	9th-25th		
# -0.84	-0.50	25th		
# -0.50	-0.17	25-50th 		
# -0.17	0.17	50th 		
# 0.17	0.50	50-75th 		
# 0.50	0.84	75th 		
# 0.84	1.16	75-91st 		
# 1.16	1.50	91st 		
# 1.50	1.83	91-98th 		Overweight
# 1.83	2.17	98th 		Overweight
# 2.17	2.50	98-99.6th 		Very overweight (obese)
# 2.50	2.84	99.6th 		Very overweight (obese)
# 2.84	6.00	Above 99.6th	Above normal range	Severely obese
# 	>6.00		Probable error	Probable error

<<<<<<< HEAD
=======

def create_suffix_for_cardinal_number(cardinal_number)->str:
    # Converts a cardinal number to an ordinal by adding a suffix 'st', 'nd', 'rd' or 'th'
    # Accepts decimals and negative numbers

    suffix="th" # this is the default

    # get the final and last 2 digits
    final_two_digits = cardinal_number%100
    final_digit = cardinal_number%10
    if final_digit == 1:
        suffix = "st"
    elif final_digit == 2:
        suffix = "nd"
    elif final_digit == 3:
        suffix = "rd"
    
    # 11, 12, 13 are special cases as they take 'th'
    if final_two_digits >= 11 or final_two_digits <= 13:
        suffix = "th"

    return f"{cardinal_number}{suffix}"
>>>>>>> a7ba1a2913d9c7dab4a2a0ed222316d88ade476f


def quarter_distances(centile):
    """
    return sds of points that are +/- 0.25*0.666 sds space from the centile line

    0.25 * 0.666 comes from the definition that a point within 0.25 centile space
     from the centile line in a UK growth chart is considered as on the centile
    this distance from centile line is used for all centile patterns, regardless of 
     whether the centile lines are equally spaced apart
    """
    sds = rounded_sds_for_centile(centile)
    quarter_distance = 0.25 * 0.666
    return sds - quarter_distance, sds + quarter_distance


def generate_centile_band_ranges(centile_format):
    """
    returns a list of tuples representing ranges of on centile line and between centiles
    """
    centile_ranges = []
    for centile_line in centile_format:
        centile_ranges.extend(quarter_distances(centile_line))
    centile_bands = list(zip(centile_ranges[:-1],centile_ranges[1:]))

    return centile_bands


def centile_band_for_centile(sds: float, measurement_method: str, centile_format: str)->str:
    """
        this function returns a centile band into which the sds falls
    
        params: accepts a sds: float
        params: accepts a measurement_method as string
        params: accepts array of centiles representing the centile lines
    """
    if centile_pattern == CENTILE_FORMATS[0]:
        centile_band = THREE_PERCENT_CENTILE_COLLECTION
    elif centile_pattern == CENTILE_FORMATS[1]:
        centile_band = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION

    centile_band_ranges = generate_centile_band_ranges(centile_format)    

    if measurement_method == BMI:
        measurement_method = "body mass index"
    elif measurement_method == HEAD_CIRCUMFERENCE:
        measurement_method = "head circumference"

    if sds <= -6:
        return f"This {measurement_method} measurement is well below the normal range. Please review its accuracy."
    elif sds > 6:
        return f"This {measurement_method} measurement is well above the normal range. Please review its accuracy."
    elif sds <= centile_band_ranges[0][0]:
        return f"This {measurement_method} measurement is below the normal range"
    elif sds > centile_band_ranges[-1][1]:
        return f"This {measurement_method} measurement is above the normal range"        
    else:
        #even indices of centile_bands list is always on centile
        #odd indices of cnetile_bands list is always between centil
        for r in range(len(centile_band_ranges)):
            if centile_band_ranges[r][0] <= sds < centile_band_ranges[r][1]:
                if r%2 == 0:
                    centile = centile_band[r//2]
                    return f"This {measurement_method} measurement is on or near the {centile} centile."
                else:
                    lower_centile = centile_band[(r-1)//2]
                    upper_centile = centile_band[(r+1)//2]
                    return f"This {measurement_method} measurement is between the {lower_centile} and {upper_centile} centiles."
    

