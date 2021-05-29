# core imports
from datetime import datetime
from datetime import timedelta
import random

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
    interval_days = 90,
    start_sds = 0,
    drift = False,
    drift_range = -0.05,
    noise = False,
    reference = "uk-who"
):
  """
  This function generates an array of meassurement objects based on the params:
  measurement_method: ['height', 'weight', 'ofc', 'bmi']
  sex: ['male', 'female']
  gestation_weeks
  gestation_days,
  interval: days,
  start_sds: the starting SDS
  drift: a boolean value
  drift_range: implemented if drift is true. The max range SDS a data point can drift from the previous
  noise: a boolean to simulate measurement accuracy
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
  birth_date = datetime(1759, 4, 11)  # YYYY m d
  observation_date = birth_date + timedelta(days=start_chronological_age*365.25)
  
  # set the counters
  cycle_age = start_chronological_age
  cycle_sds = start_sds 
  
  annualized_interval = interval_days/365.35 # interval between data points
  cycle_number = (start_chronological_age - end_age)/annualized_interval # number of iterations

  measurements_array=[]
  while cycle_age < end_age:

    if gestation_weeks < 40: # correct for gestational age
      cycle_age = cycle_age + ((gestation_weeks*7 + gestation_days)-280)/365.25
    


    rawMeasurement = measurement_from_sds(
      reference=reference,
      requested_sds=cycle_sds,
      measurement_method=measurement_method,
      sex=sex,
      age=cycle_age
    )

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
      cycle_sds += random.uniform(0, drift_range/cycle_number)
      # round the result
      cycle_sds=round(cycle_sds,3)
    
    # add measurement inaccuracy
    if noise:
      cycle_sds += random.uniform(-0.005, 0.005)

    # increment age
    cycle_age += annualized_interval
    observation_date = observation_date + timedelta(days=interval_days)
    
  return measurements_array

    