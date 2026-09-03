"""Public import and call contracts used by digital-growth-charts-server."""

from datetime import date
from importlib import import_module
from inspect import Parameter, signature

import pytest

import rcpchgrowth
from rcpchgrowth import chart_functions, constants

PUBLIC_SYMBOL_MODULES = {
    "Measurement": "rcpchgrowth.measurement",
    "centile": "rcpchgrowth.global_functions",
    "chronological_calendar_age": "rcpchgrowth.date_calculations",
    "corrected_decimal_age": "rcpchgrowth.date_calculations",
    "create_chart": "rcpchgrowth.chart_functions",
    "generate_fictional_child_data": "rcpchgrowth.fictional_child",
    "lower_and_upper_limits_of_expected_height_z": "rcpchgrowth.mid_parental_height",
    "measurement_from_sds": "rcpchgrowth.global_functions",
    "mid_parental_height_z": "rcpchgrowth.mid_parental_height",
    "sds_for_measurement": "rcpchgrowth.global_functions",
}

PARAMETER_CONTRACTS = {
    "Measurement": (
        "birth_date",
        "measurement_method",
        "observation_date",
        "observation_value",
        "reference",
        "sex",
        "gestation_days",
        "gestation_weeks",
        "events_text",
        "bone_age",
        "bone_age_type",
        "bone_age_sds",
        "bone_age_centile",
        "bone_age_text",
    ),
    "centile": ("z_score",),
    "chronological_calendar_age": ("birth_date", "observation_date"),
    "corrected_decimal_age": (
        "birth_date",
        "observation_date",
        "gestation_weeks",
        "gestation_days",
    ),
    "create_chart": (
        "reference",
        "centile_format",
        "measurement_method",
        "sex",
        "is_sds",
    ),
    "generate_fictional_child_data": (
        "measurement_method",
        "sex",
        "start_chronological_age",
        "end_age",
        "gestation_weeks",
        "gestation_days",
        "measurement_interval_type",
        "measurement_interval_number",
        "start_sds",
        "drift",
        "drift_range",
        "noise",
        "noise_range",
        "reference",
        "start_chronological_age_interval_type",
        "end_age_interval_type",
    ),
    "lower_and_upper_limits_of_expected_height_z": ("mid_parental_height_z",),
    "measurement_from_sds": (
        "reference",
        "requested_sds",
        "measurement_method",
        "sex",
        "age",
        "default_youngest_reference",
    ),
    "mid_parental_height_z": ("maternal_height", "paternal_height", "reference"),
    "sds_for_measurement": (
        "reference",
        "age",
        "measurement_method",
        "observation_value",
        "sex",
    ),
}

DEFAULT_CONTRACTS = {
    "Measurement": {
        "gestation_days": 0,
        "gestation_weeks": 0,
        "events_text": None,
        "bone_age": None,
        "bone_age_type": None,
        "bone_age_sds": None,
        "bone_age_centile": None,
        "bone_age_text": None,
    },
    "centile": {},
    "chronological_calendar_age": {},
    "corrected_decimal_age": {},
    "create_chart": {
        "centile_format": "cole-nine-centiles",
        "measurement_method": "height",
        "sex": "female",
        "is_sds": False,
    },
    "generate_fictional_child_data": {
        "start_chronological_age": 0.0,
        "end_age": 20.0,
        "gestation_weeks": 40,
        "gestation_days": 0,
        "measurement_interval_type": "days",
        "measurement_interval_number": 20,
        "start_sds": 0,
        "drift": False,
        "drift_range": -0.05,
        "noise": False,
        "noise_range": 0.01,
        "reference": "uk-who",
        "start_chronological_age_interval_type": "years",
        "end_age_interval_type": "years",
    },
    "lower_and_upper_limits_of_expected_height_z": {},
    "measurement_from_sds": {"default_youngest_reference": False},
    "mid_parental_height_z": {"reference": "uk-who"},
    "sds_for_measurement": {},
}

SERVER_MODULE_IMPORTS = (
    "rcpchgrowth.chart_functions",
    "rcpchgrowth.constants",
    "rcpchgrowth.constants.reference_constants",
    "rcpchgrowth.constants.validation_constants",
    "rcpchgrowth.date_calculations",
    "rcpchgrowth.global_functions",
)


@pytest.mark.parametrize("name,module_name", PUBLIC_SYMBOL_MODULES.items())
def test_server_root_imports_resolve_to_their_defining_modules(name, module_name):
    assert getattr(rcpchgrowth, name) is getattr(import_module(module_name), name)


@pytest.mark.parametrize("name,parameter_names", PARAMETER_CONTRACTS.items())
def test_server_callable_parameter_names_and_order_are_stable(name, parameter_names):
    assert tuple(signature(getattr(rcpchgrowth, name)).parameters) == parameter_names


@pytest.mark.parametrize("name,defaults", DEFAULT_CONTRACTS.items())
def test_server_callable_defaults_are_stable(name, defaults):
    parameters = signature(getattr(rcpchgrowth, name)).parameters

    assert {
        name: parameter.default
        for name, parameter in parameters.items()
        if parameter.default is not Parameter.empty
    } == defaults


def test_server_module_imports_are_available_from_the_package_root():
    assert chart_functions is import_module("rcpchgrowth.chart_functions")
    assert constants is import_module("rcpchgrowth.constants")


@pytest.mark.parametrize("module_name", SERVER_MODULE_IMPORTS)
def test_server_direct_module_imports_remain_available(module_name):
    assert import_module(module_name).__name__ == module_name


def test_server_constant_imports_retain_their_public_values():
    expected = {
        "CDC": "cdc",
        "MAXIMUM_BMI_ERROR_SDS": 15,
        "MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS": 8,
        "MINIMUM_BMI_ERROR_SDS": -15,
        "MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS": -8,
        "TRISOMY_21": "trisomy-21",
        "TRISOMY_21_AAP": "trisomy-21-aap",
        "TURNERS": "turners-syndrome",
        "UK_WHO": "uk-who",
        "WHO": "who",
    }

    assert {name: getattr(rcpchgrowth, name) for name in expected} == expected


def test_representative_root_import_invocations_remain_usable():
    assert rcpchgrowth.centile(0.0) == pytest.approx(50.0)
    assert (
        rcpchgrowth.chronological_calendar_age(date(2020, 1, 1), date(2021, 1, 1))
        == "1 year"
    )
    assert rcpchgrowth.lower_and_upper_limits_of_expected_height_z(
        0.5
    ) == pytest.approx((-0.9, 1.9))
