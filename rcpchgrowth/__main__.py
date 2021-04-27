from click.types import DateTime
from . import *
import click

@click.group()
def calculations():
    """
    Performs calculations on growth data using UK-WHO, Turner or Down's reference data.
    """

@click.option('-c','--corrected', help='Adjust for gestation')
@calculations.command()
def ages(birth_date: DateTime, observation_date: DateTime, adjust: bool=False, gestation_weeks=40, gestation_days=0):
    """
    Return a decimal age based on a birth date, observation_date and gestation
    """
    decimal_age=0
    if adjust:
        decimal_age=corrected_decimal_age(
            birth_date=birth_date, 
            observation_date=observation_date,
            gestation_weeks=gestation_weeks,
            gestation_days=gestation_days
        )
    else:
        decimal_age=chronological_decimal_age(
            birth_date=birth_date,
            observation_date=observation_date
        )
    print(f"{decimal_age} y")


def sds_centile():
    """
    Return an SDS for a measurement, sex, gestation and reference
    """


if __name__ == "__main__":
    ## run the functions ##
    print("these are functions called from the CLI")
    calculations(prog_name='calculations')