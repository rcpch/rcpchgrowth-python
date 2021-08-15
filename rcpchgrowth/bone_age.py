class BoneAge:

    """
    The BoneAge class returns a bone age object
    Params
    `bone_age`: an estimated skeletal age calculated from xrays reported in decimal years
    `bone_age_sds`: an SDS for the bone age, based on references
    `bone_age_centile`: a centile for the bone age, based on references
    `bone_age_reference`: enum ['greulich-pyle', 'tanner-whitehouse-ii', 'tanner-whitehouse-iii', 'fels', 'bonexpert']
    """

    def __init__(
        self,
        decimal_age: float,
        bone_age: float,
        height: float,
        bone_age_type: str = None,
        bone_age_sds: float = None,
        bone_age_centile: float = None,
        bone_age_text: str = None,
        ):

        self.decimal_age = decimal_age
        self.bone_age = bone_age
        self.height=height
        self.bone_age_type = bone_age_type
        self.bone_age_sds = bone_age_sds
        self.bone_age_centile = bone_age_centile
        self.bone_age_text = bone_age_text

        return {
            "decimal_age": self.decimal_age,
            "bone_age": self.bone_age,
            "bone_age_type": self.bone_age_type,
            "bone_age_sds": self.bone_age_sds,
            "bone_age_centile": self.bone_age_centile,
            "bone_age_text": self.bone_age_text,
            "plottable_data": [
                {
                    "x": self.decimal_age,
                    "y": self.height
                },
                {
                    "x": self.decimal_age,
                    "y": self.bone_age
                }
            ]
        }