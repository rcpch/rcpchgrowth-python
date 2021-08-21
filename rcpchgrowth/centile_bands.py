# imports from rcpchgrowth
from .constants import BMI, HEAD_CIRCUMFERENCE,CENTILE_FORMATS,THREE_PERCENT_CENTILE_COLLECTION,COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION 
from .global_functions import rounded_sds_for_centile
from itertools import chain

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


def quarter_distances(centile):
    """
    return sds of points that are +/- 1/4 of centile space from the centile line
    """
    sds = rounded_sds_for_centile(centile)
    quarter_distance = 0.25 * 0.666
    return sds - quarter_distance, sds + quarter_distance


def generate_centile_band_ranges(centile_lines):
    """
    returns a list of tuples representing ranges
    """
    centile_ranges = []
    for centile in centile_lines:
        centile_ranges.extend(quarter_distances(centile))
    centile_bands = list(zip(centile_ranges[:-1],centile_ranges[1:]))

    return centile_bands


def centile_band_for_centile(sds: float, measurement_method: str, centile_pattern: str)->str:
    """
        this function returns a centile band into which the sds falls
    
        params: accepts a sds: float
        params: accepts a measurement_method as string
        params: accepts centile_pattern 6 or 9
    """
    #temporary; couldn't find the suffix function
    centile_band_9_suffix = ["th","nd","th","th","th","th","st","th","th"]
    centile_band_6_suffix = ["rd","th","th","th","th","th","th"]

    if centile_pattern == CENTILE_FORMATS[0]:
        centile_band = THREE_PERCENT_CENTILE_COLLECTION
        centile_band_suffix = centile_band_6_suffix
    elif centile_pattern == CENTILE_FORMATS[1]:
        centile_band = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION
        centile_band_suffix = centile_band_9_suffix

    centile_band_ranges = generate_centile_band_ranges(centile_band)    

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
                    suffix = centile_band_suffix[r//2]
                    return f"This {measurement_method} measurement is on or near the {centile:0.0f}{suffix} centile."
                else:
                    lower_centile = centile_band[(r-1)//2]
                    lower_suffix = centile_band_suffix[(r-1)//2]
                    upper_centile = centile_band[(r+1)//2]
                    upper_suffix = centile_band_suffix[(r+1)//2]
                    return f"This {measurement_method} measurement is between the {lower_centile:0.0f}{lower_suffix} and {upper_centile:0.0f}{upper_suffix} centiles."
    


