# core imports
from datetime import date, timedelta
import random
import math

# rcpchgrowth imports
from rcpchgrowth.global_functions import measurement_from_sds
from rcpchgrowth.measurement import Measurement

def generate_fictional_child_data(
    measurement_method: str,
    sex: str,
    start_chronological_age: float = 0.0,
    end_age: float = 20.0,
    gestation_weeks = 40,
    gestation_days = 0,
    measurement_interval_type = "days",
    measurement_interval_number: int = 20,
    start_sds = 0,
    drift = False,
    drift_range = -0.05,
    noise = False,
    noise_range = 0.01,
    reference = "uk-who"
):
  """
  This function generates an array of meassurement objects based on the params:
  measurement_method: ['height', 'weight', 'ofc', 'bmi']
  sex: ['male', 'female']
  gestation_weeks
  gestation_days,
  interval_type: ['days', 'd', 'day', 'years', 'year', 'y', 'months', 'month', 'm']
  start_sds: the starting SDS
  drift: a boolean value
  drift_range: implemented if drift is true. This is an SDS value and represents the SDS of the final plot, relative to starting SDS.
  noise: a boolean to simulate measurement accuracy
  noise_range: 0-1 - always positive. A typical acceptable error is 1% in measurement accuracy, so supplied as 0.01
  """

  # set the variables

  """
  This is an unnecessary piece of growth chart trivia included for entertainment. The first published 
  growth chart is that of the son of Count Philibert de Montbeillard (1720-1785), François Guéneau de Montbeillard.
  The date of birth used here is that of Francois.
  Acknowledgement:
  The development of growth references and growth charts, T J Cole, Ann Hum Biol. 2012 Sep; 39(5): 382–394.
  Wikipedia: https://en.wikipedia.org/wiki/Philippe_Gu%C3%A9neau_de_Montbeillard
  """
  birth_date = date(1759, 4, 11)  # YYYY m d
  observation_date = birth_date + timedelta(days=start_chronological_age*365.25)
  
  # set the counters
  cycle_age = start_chronological_age
  cycle_sds = start_sds 

  interval_in_years = end_age-start_chronological_age
  annualized_interval = 0 # interval between data points

  if measurement_interval_type in ['d', 'day', 'days']:
    annualized_interval = (measurement_interval_number/365.25)
  elif measurement_interval_type in ['w', 'week', 'weeks']:
    annualized_interval = (measurement_interval_number/52)
  elif measurement_interval_type in ['m', 'month', 'months']:
    annualized_interval = (measurement_interval_number/12)
  elif measurement_interval_type in ['y', 'year', 'years']:
      annualized_interval = measurement_interval_number
  else:
      raise ValueError(
          "parameters must be one of 'd', 'day', 'days', 'w', 'week', 'weeks', 'm', 'month', 'months', 'y', 'year' or 'years'")

  cycle_number = math.floor(interval_in_years/annualized_interval) # number of iterations

  drift_amount = 0.0
  if drift:
    drift_amount = drift_range / cycle_number

  measurements_array=[]

  while cycle_age < end_age:

    rawMeasurement = None

    try:
      rawMeasurement = measurement_from_sds(
        reference=reference,
        requested_sds=cycle_sds,
        measurement_method=measurement_method,
        sex=sex,
        age=cycle_age
      )
    except Exception as e:
      print(e)

    if noise and rawMeasurement is not None:
      # add measurement inaccuracy based on percentage supplied
      degree_error = rawMeasurement * noise_range
      rawMeasurement += random.uniform(-degree_error, degree_error)
    
    if rawMeasurement is not None:
      rawMeasurement = round(rawMeasurement, 1)

      measurement = Measurement(
        birth_date=birth_date,
        observation_date=observation_date,
        observation_value=rawMeasurement,
        measurement_method=measurement_method,
        reference=reference,
        sex=sex,
        gestation_weeks=gestation_weeks,
        gestation_days=gestation_days
      ).measurement

      measurements_array.append(measurement)
    
    # create drift
    if drift:
      cycle_sds += drift_amount
      # round the result
      cycle_sds=round(cycle_sds,3)
    

    # increment age
    cycle_age += annualized_interval
    observation_date = observation_date + timedelta(days=annualized_interval*365.25)
    
  return measurements_array

    