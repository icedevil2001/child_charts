from pathlib import Path
from typing import Dict, Tuple, Literal, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd 
from collections import defaultdict
from src import logger



def build_growth_database() -> Dict[str, Dict[str, Dict[Tuple[int, int], pd.DataFrame]]]:
    """Return a dictionary of tables. The keys gender, metric, and age range (int,int). 
    The values are pandas DataFrames, indexed by 'Month' and columns 'L',  'M', 'S', 'P1', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99'
    """
    ## memory usage is approximately < 110 KB
    datapath = Path('data')
    tables = defaultdict(lambda: defaultdict(dict))  ## gender: {metric: {age_range: file}}
    for file in datapath.glob('*.xlsx'):
        df = pd.read_excel(file).set_index('Month')
        metric, gender, age_range, *_ = file.stem.split('.')
        min_age, max_age = map(int, age_range.split('_'))
        age_range = (min_age, max_age )
        if gender in tables:
            if metric in tables[gender]:
                tables[gender][metric][age_range]=  df
            else:
                tables[gender][metric] = {age_range: df}
        else:
            tables[gender] = {metric: {age_range: df}}
    if len(tables) == 0:
        logger.warning("No tables found, check the data directory")
        raise ValueError("No tables found, check the data directory")
    return tables

def get_growth_table(tables: Dict[str, Dict[str, Dict[Tuple[int, int], pd.DataFrame]]],
            metric: Literal['wfa','lhfa', 'hcfa', 'bmi'], gender: Literal['girls','boys'], age: int) -> pd.DataFrame:
    """Return the growth table for the given metric, gender, and age"""
    gender = gender.lower()
    if gender not in tables:
        raise ValueError(f"Gender not found in tables: {tables[metric].keys()}")
    if metric not in tables[gender]:
        raise ValueError(f"Metric {metric} not found in tables: {tables.keys()}")
    metric_tables = tables[gender][metric]
    for age_range, table in metric_tables.items():
        if age >= age_range[0] and age <= age_range[1]:
            return table
    raise ValueError(f"Age {age} not found in tables: {metric_tables.keys()}")


@dataclass
class Child():
    """Child class with name and date of birth attributes and a method to calculate age in months
        Args:
            name (str): Name of the child
            gender (Literal['M','F'])
            dob (str): Date of birth in the format 'YYYY-MM-DD'
    """
    name: str
    gender: Literal['M', 'F', 'girl', 'boy']
    dob: str | datetime


    def __post_init__(self):
        self.today = datetime.today()   
        self.dob = self.dob_validation()
        self.age = self.get_age()
        self.months = self.get_months()
        self.gender = self.get_gender()

    def dob_validation(self):
        """Date of birth cannot be in the future."""
        logger.debug(f"{self.today=} {self.dob=}")
        if isinstance(self.dob, str):
            self.dob = datetime.strptime(self.dob, '%Y-%m-%d')
        if self.dob>=self.today:
            raise ValueError('Date of birth cannot be in the future')
        else:
            return self.dob
    
    def get_age(self):
        """Number of years since birth"""
        age = self.today.year - self.dob.year - ((self.today.month, self.today.day) < (self.dob.month, self.dob.day))
        return age
    
    def get_months(self):    
        """Number of months since birth"""
        month = self.today.month - self.dob.month + 12 * (self.today.year - self.dob.year)
        return month
    
    def get_gender(self):
        gen = {
            'm': 'boys', 
            'f': 'girls', 
            'girl': 'girls',
            'boy': 'boys'
        }
        return gen[self.gender.lower()]
    

@dataclass
class Measurement:
    """Measurement class with date and value attributes.
    
    Args:
        child (Child): Child object
        date (str): Date of the measurement in the format 'YYYY-MM-DD'
        weight (float): Weight in kg
        height (float): Height in cm
        hc (float): Head circumference in cm
        
    """
    child: Child
    date: str
    weight: Optional[float] = None
    height: Optional[float] = None
    hc: Optional[float] = None
    
    def __post_init__(self):
        self.bmi = self.get_bmi()
        self.date = self.date_validation()
        
    def get_bmi(self):
        if self.weight and self.height:
            return self.weight / (self.height ** 2)
        
    def date_validation(self):
        """Measure date cannot be in the future."""
        today = datetime.today()
        date = datetime.strptime(self.date, '%Y-%m-%d')
        # print(today, date, date>today)
        if date>=today:
            raise ValueError('Date cannot be in the future')
        else:
            return date
        
    def __str__(self):
        return f'{self.child.name} was {self.weight} kg, {self.height} cm, and {self.hc} cm on {self.date}'
        
    