import pytest

from rcpchgrowth.constants import MALE, FEMALE, UK_WHO, CDC, MINIMUM_PARENTAL_HEIGHT_CM, MAXIMUM_PARENTAL_HEIGHT_CM
from rcpchgrowth.mid_parental_height import mid_parental_height, mid_parental_height_z, expected_height_z_from_mid_parental_height_z

maternal_height = 151
paternal_height = 167
ACCURACY = 1e-3


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
    """Test that heights below minimum raise appropriate errors"""
    too_short = MINIMUM_PARENTAL_HEIGHT_CM - 1
    
    with pytest.raises(ValueError, match=f"Maternal height of {too_short} cm is below the minimum"):
        mid_parental_height(maternal_height=too_short, paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match=f"Paternal height of {too_short} cm is below the minimum"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=too_short, sex=MALE)
    
    with pytest.raises(ValueError, match=f"Maternal height of {too_short} cm is below the minimum"):
        mid_parental_height_z(maternal_height=too_short, paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match=f"Paternal height of {too_short} cm is below the minimum"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=too_short, reference=UK_WHO)


def test_midparental_height_validation_above_maximum():
    """Test that heights above maximum raise appropriate errors"""
    too_tall = MAXIMUM_PARENTAL_HEIGHT_CM + 1
    
    with pytest.raises(ValueError, match=f"Maternal height of {too_tall} cm is above the maximum"):
        mid_parental_height(maternal_height=too_tall, paternal_height=paternal_height, sex=MALE)
    
    with pytest.raises(ValueError, match=f"Paternal height of {too_tall} cm is above the maximum"):
        mid_parental_height(maternal_height=maternal_height, paternal_height=too_tall, sex=MALE)
    
    with pytest.raises(ValueError, match=f"Maternal height of {too_tall} cm is above the maximum"):
        mid_parental_height_z(maternal_height=too_tall, paternal_height=paternal_height, reference=UK_WHO)
    
    with pytest.raises(ValueError, match=f"Paternal height of {too_tall} cm is above the maximum"):
        mid_parental_height_z(maternal_height=maternal_height, paternal_height=too_tall, reference=UK_WHO)


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
    """Test that boundary values (minimum and maximum) are accepted"""
    # Test minimum boundary
    assert mid_parental_height(maternal_height=MINIMUM_PARENTAL_HEIGHT_CM, paternal_height=MINIMUM_PARENTAL_HEIGHT_CM, sex=MALE) == (MINIMUM_PARENTAL_HEIGHT_CM + MINIMUM_PARENTAL_HEIGHT_CM + 13) / 2
    
    # Test maximum boundary
    assert mid_parental_height(maternal_height=MAXIMUM_PARENTAL_HEIGHT_CM, paternal_height=MAXIMUM_PARENTAL_HEIGHT_CM, sex=FEMALE) == (MAXIMUM_PARENTAL_HEIGHT_CM + MAXIMUM_PARENTAL_HEIGHT_CM - 13) / 2
    
    # Test that z-score calculation works with boundary values
    result = mid_parental_height_z(maternal_height=MINIMUM_PARENTAL_HEIGHT_CM, paternal_height=MINIMUM_PARENTAL_HEIGHT_CM, reference=UK_WHO)
    assert isinstance(result, float)
    
    result = mid_parental_height_z(maternal_height=MAXIMUM_PARENTAL_HEIGHT_CM, paternal_height=MAXIMUM_PARENTAL_HEIGHT_CM, reference=UK_WHO)
    assert isinstance(result, float)