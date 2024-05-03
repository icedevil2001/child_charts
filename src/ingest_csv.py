# This file contains the parser for the huckleberry csv file
import pandas as pd
from src.unit_conversions import Weight, Length
from pathlib import Path
import re
from src.database import Child, get_growth_table
from src.calculations import ZscoreWeight, ZscoreHeight, interpolate_lms, calc_bmi
from typing import Dict



def cleanup_weight(weight: str) -> float:
    """Cleans up the weight string and returns the weight in kg"""
    if pd.isna(weight) or weight is None or weight == '':
        return pd.NA
    unit = re.search(r'\d+(kg|lbs\.oz|lbs)', weight)
    if unit:
        unit = unit.group(1)
        units = {
            'kg': 'kg',
            'lbs': 'lbs',
            'lbs.oz': 'lbs' ## Huckleebery uses lbs.oz, but it is actually lbs
        }
        return Weight(float(weight.split(unit)[0]), units[unit]).to_kilograms()
    else:
        return pd.NA
    
def cleanup_length(height: str) -> float:
    """Cleans up the height string and returns the height in cm"""
    if pd.isna(height) or height is None or height == '':
        return pd.NA
    unit = re.search(r'\d+(ft\.in|ft|cm|in)', height)
    if unit:
        unit = unit.group(1)
        
        units = {
            'ft': 'ft',
            'ft.in': 'ft', # This is a hack, but it works for now
            'cm': 'cm',
            'in': 'in'

        }
        return Length(float(height.split(unit)[0]), units[unit]).to_cm()
    else:
        raise ValueError(f'Invalid height: {height}: type: {type(height)}')

def process_huckleebery_df(df: pd.DataFrame, child: Child, growth_tables: Dict[str, Dict[str, Dict[str, pd.DataFrame]]]) -> pd.DataFrame:
    """Processes the huckleberry dataframe and returns a new dataframe with the weight, height, and head circumference 
    converted to kg, cm, and cm respectively"""
    df['date'] = pd.to_datetime(df['date'])
    df['months'] = df['date'].apply(lambda x: (x - child.dob).days / 30).round(2)
    df['weight_kg'] = df['weight'].apply(cleanup_weight)#.round(2)
    df['height_cm'] = df['height'].apply(cleanup_length)#.round(2)
    df['hc_cm'] = df['hc'].apply(cleanup_length)#.round(2)
    # df['bmi'] = df['weight_kg'] / ((df['height_cm'] / 100) ** 2)
    df['bmi'] = df.apply(lambda row: calc_bmi(row['weight_kg'], row['height_cm']), axis=1)
    df =  percentile(df, child, growth_tables)
    return df

def huckleberry_reader(file_path: Path, child: Child, growth_tables: Dict[str, Dict[str, Dict[str, pd.DataFrame]]]) -> pd.DataFrame:
    """Reads the huckleberry csv file and returns a dataframe with the weight, height, and head circumference 
    converted to kg, cm, and cm respectively"""
    df = (pd.read_csv(file_path)
        .query('Type  == "Growth"')
        .rename(columns={
            'Start': 'date', 
            'Start Condition': 'weight',
            "Start Location": 'height',
            'End Condition': 'hc'
            })
        .dropna(axis=1, how='all')
        
        )
    
    return process_huckleebery_df(df, child, growth_tables)


def standardize_reader(file_path: Path, child: Child, growth_tables: Dict[str, Dict[str, Dict[str, pd.DataFrame]]]) -> pd.DataFrame:
    """Reads the strandard csv file and returns a dataframe with the weight, height, and head circumference and there percentiles respectively"""
    df = (pd.read_csv(file_path)
        .dropna(axis=1, how='all')
        )
    df['date'] = pd.to_datetime(df['date'])
    df['months'] = df['date'].apply(lambda x: (x - child.dob).days / 30).round(2)
    # df['bmi'] = df['weight_kg'] / ((df['height_cm'] / 100) ** 2)
    df['bmi'] = df.apply(lambda row: calc_bmi(row['weight_kg'], row['height_cm']), axis=1)
    df = percentile(df, child, growth_tables)
    return df


def percentile(df: pd.DataFrame, child:Child, growth_tables: dict):
    df['weight_percentile'] = df.apply(lambda row: weight_percentile(row, child, growth_tables), axis=1).fillna(0).round(1)
    df['bmi_percentile'] = df.apply(lambda row: bmi_percentile(row, child, growth_tables), axis=1).fillna(0).round(1)
    df['height_percentile'] = df.apply(lambda row: height_percentile(row, child, growth_tables), axis=1).fillna(0).round(1)
    df['hc_percentile'] = df.apply(lambda row: hc_percentile(row, child, growth_tables), axis=1).fillna(0).round(1)
    return df

def weight_percentile(row,  child:Child, growth_tables: dict):
    if pd.isna(row['weight_kg']) or row['weight_kg'] == 0.0 or pd.isna(row['months']):
        return pd.NA
    else:
        growth_table = get_growth_table(growth_tables, 'wfa', child.gender, child.age) 

        try:
            return ZscoreWeight(*interpolate_lms(row['months'], growth_table), row['weight_kg']).z_score_to_percentile()
        except ZeroDivisionError:
            print("Error: Division by zero")
            return pd.NA
        except ValueError:
            print("Error: Invalid value")
            return pd.NA

def bmi_percentile(row,  child:Child, growth_tables: dict):
    # print(row['bmi'])
    if pd.isna(row['bmi']) or row['bmi'] == 0.0 or pd.isna(row['months']):
        return pd.NA
    else:
        growth_table = get_growth_table(growth_tables, 'bmi', child.gender, child.age) 

        try:
            return ZscoreWeight(*interpolate_lms(row['months'], growth_table), row['bmi']).z_score_to_percentile()
        except ZeroDivisionError:
            print("Error: Division by zero")
            return pd.NA
        except ValueError:
            print("Error: Invalid value")
            return pd.NA
        

def height_percentile(row, child:Child, growth_tables: dict):
    # print(row['bmi'])
    if pd.isna(row['height_cm']) or row['height_cm'] == 0.0 or pd.isna(row['months']):
        return pd.NA
    else:
        growth_table = get_growth_table(growth_tables, 'lhfa', child.gender, child.age) 

        try:
            return ZscoreHeight(*interpolate_lms(row['months'], growth_table), row['height_cm']).z_score_to_percentile()
        except ZeroDivisionError:
            print("Error: Division by zero")
            return pd.NA
        except ValueError:
            print("Error: Invalid value")
            return pd.NA
        

def hc_percentile(row, child:Child, growth_tables: dict):
    # print(row['bmi'])
    if pd.isna(row['hc_cm']) or row['hc_cm'] == 0.0 or pd.isna(row['months']):
        return pd.NA
    else:
        growth_table = get_growth_table(growth_tables, 'hcfa', child.gender, child.age) 

        try:
            return ZscoreHeight(*interpolate_lms(row['months'], growth_table), row['hc_cm']).z_score_to_percentile()
            # return ZscoreWeight(*interpolate_lms(row['months'], growth_table), row['hc_cm']).z_score_to_percentile()
        except ZeroDivisionError:
            print("Error: Division by zero")
            return pd.NA
        except ValueError:
            print("Error: Invalid value")
            return pd.NA
