import pytest

from rcpchgrowth.constants import (
    MALE,
    FEMALE,
    UK_WHO,
    CDC,
    HEIGHT,
    MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS,
    MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS,
)
from rcpchgrowth.global_functions import measurement_from_sds
from rcpchgrowth.mid_parental_height import mid_parental_height, mid_parental_height_z, expected_height_z_from_mid_parental_height_z

maternal_height = 151
paternal_height = 167
ACCURACY = 1e-3


def _parental_height_for_sds(requested_sds, sex):
    return measurement_from_sds(
        reference=UK_WHO,
        age=20.0,
        measurement_method=HEIGHT,
        sex=sex,
        requested_sds=requested_sds,
    )


def test_midparental_height():
    assert mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex=MALE) == 165.5 
    assert mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex=FEMALE) == 152.5
    assert mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference=UK_WHO) == pytest.approx(-0.8943229, ACCURACY)
    assert mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference=CDC) == pytest.approx(-0.8177165233046019, ACCURACY)
    assert expected_height_z_from_mid_parental_height_z(mid_parental_height_z=-0.8943229) == pytest.approx(-0.44716145, ACCURACY)


def test_midparental_height_validation_none_values():
    """Test that None values raise appropriate errors"""
    with pytest.raises(ValueError, match="Maternal height cannot be None"):
        mid_parental_height(maternal_height=None, paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match="Paternal height cannot be None"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=None, sex=MALE)
    
    with pytest.raises(ValueError, match="Maternal height cannot be None"):
        mid_parental_height_z(maternal_height=None, paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match="Paternal height cannot be None"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=None, reference=UK_WHO)


def test_midparental_height_validation_non_numeric():
    """Test that non-numeric values raise appropriate errors"""
    with pytest.raises(ValueError, match="Maternal height must be a number"):
        mid_parental_height(maternal_height="151", paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match="Paternal height must be a number"):
        mid_parental_height(maternal_height=maternal_height, paternal_height="167", sex=MALE)
    
    with pytest.raises(ValueError, match="Maternal height must be a number"):
        mid_parental_height_z(maternal_height=[151], paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match="Paternal height must be a number"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height={"height": 167}, reference=UK_WHO)


def test_midparental_height_validation_below_minimum():
    """Test that heights below -8 SDS raise appropriate errors."""
    maternal_too_short = _parental_height_for_sds(MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS - 0.5, FEMALE)
    paternal_too_short = _parental_height_for_sds(MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS - 0.5, MALE)
    
    with pytest.raises(ValueError, match="The maternal height of .* is below -8 SD"):
        mid_parental_height(maternal_height=maternal_too_short, paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match="The paternal height of .* is below -8 SD"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_too_short, sex=MALE)
    
    with pytest.raises(ValueError, match="The maternal height of .* is below -8 SD"):
        mid_parental_height_z(maternal_height=maternal_too_short, paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match="The paternal height of .* is below -8 SD"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_too_short, reference=UK_WHO)


def test_midparental_height_validation_above_maximum():
    """Test that heights above +8 SDS raise appropriate errors."""
    maternal_too_tall = _parental_height_for_sds(MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS + 0.5, FEMALE)
    paternal_too_tall = _parental_height_for_sds(MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS + 0.5, MALE)
    
    with pytest.raises(ValueError, match=r"The maternal height of .* is above \+8 SD"):
        mid_parental_height(maternal_height=maternal_too_tall, paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match=r"The paternal height of .* is above \+8 SD"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_too_tall, sex=MALE)
    
    with pytest.raises(ValueError, match=r"The maternal height of .* is above \+8 SD"):
        mid_parental_height_z(maternal_height=maternal_too_tall, paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match=r"The paternal height of .* is above \+8 SD"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_too_tall, reference=UK_WHO)


def test_midparental_height_validation_invalid_sex():
    """Test that invalid sex values raise appropriate errors"""
    with pytest.raises(ValueError, match="Sex must be 'male' or 'female'"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex="invalid")
    
    with pytest.raises(ValueError, match="Sex must be 'male' or 'female'"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex="MALE")  # wrong case
    
    with pytest.raises(ValueError, match="Sex must be 'male' or 'female'"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex=None)


def test_midparental_height_z_validation_invalid_reference():
    """Test that invalid reference values raise appropriate errors"""
    with pytest.raises(ValueError, match="Reference must be one of"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference="invalid")
    
    with pytest.raises(ValueError, match="Reference must be one of"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference=None)


def test_midparental_height_validation_boundary_values():
    """Test that boundary SDS values (-8 and +8) are accepted."""
    maternal_at_min = _parental_height_for_sds(MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS, FEMALE)
    paternal_at_min = _parental_height_for_sds(MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS, MALE)
    maternal_at_max = _parental_height_for_sds(MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS, FEMALE)
    paternal_at_max = _parental_height_for_sds(MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS, MALE)

    assert mid_parental_height(
        maternal_height=maternal_at_min,
        paternal_height=paternal_at_min,
        sex=MALE,
    ) == pytest.approx((maternal_at_min + paternal_at_min + 13) / 2, ACCURACY)

    assert mid_parental_height(
        maternal_height=maternal_at_max,
        paternal_height=paternal_at_max,
        sex=FEMALE,
    ) == pytest.approx((maternal_at_max + paternal_at_max - 13) / 2, ACCURACY)

    assert mid_parental_height_z(
        maternal_height=maternal_at_min,
        paternal_height=paternal_at_min,
        reference=UK_WHO,
    ) == pytest.approx(-4.0, ACCURACY)

    assert mid_parental_height_z(
        maternal_height=maternal_at_max,
        paternal_height=paternal_at_max,
        reference=UK_WHO,
    ) == pytest.approx(4.0, ACCURACY)
