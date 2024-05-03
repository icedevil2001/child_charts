import math 
from scipy.stats import norm
from abc import ABC, abstractmethod
from src import logger


## reference documentation
## https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf?sfvrsn=c2ff6a95_4
## Tables: with LMS parameters
## https://www.who.int/tools/child-growth-standards/standards/weight-for-age


class Zscore(ABC):
    """Abstract class for Z-score calculation"""
    @abstractmethod
    def zscore(self):
        pass
    
    @abstractmethod
    def z_score_to_percentile(self):
        pass
    
    @abstractmethod
    def __repr__(self):
        pass

class ZscoreWeight(Zscore):
    """Z-score calculation for weight and BMI"""
    def __init__(self, L,M,S, y):
        self.L = L # co
        self.M = M # median
        self.S = S # standard deviation
        self.y = y # weight or BMI
        
    
    def _zind(self, y):
        return (((y/self.M)**self.L) - 1) / (self.S * self.L)
    
    def sdx(self, X):
        ## SDpos3 = M * (1 + L * S * 3)^(1/L)
        ## SDposX = M * (1 + L * S * X)^(1/L)
        return self.M * (1 + self.L * self.S * X)**(1/self.L)
    
    def sdpos23(self):
        return self.sdx(3) - self.sdx(2)
    
    def sdneg23(self):
        return self.sdx(-2) - self.sdx(-3)
    
    def zscore(self):
        """calculate zscore for given measurement"""
                #           |-------------------------------------
                #           |       Zind            if |Zind| <= 3
                #           | -----------------------------------
                #           |       y - SD3pos
                #   Zind* = | 3 + ( ----------- )   if Zind > 3
                #           |         SD23pos
                #           |------------------------------------
                #           |        y - SD3neg
                #           | -3 + ( ----------- )  if Zind < -3
                #           |          SD23neg
                #           |------------------------------------
        res =  self._zind(self.y)
        if res >= -3 and res <=3: #≥-3 and ≤3
            return res
        elif res > 3:
            return 3 + (self.y - self.sdx(3)) / self.sdpos23()
        elif res < -3:
            return -3 + (self.y - self.sdx(-3)) / self.sdneg23()
        else:
            raise ValueError(f"Zscore not in range (zscore <-3 | zscorer >3 ): {res} type<{type(res)}>")

    def z_score_to_percentile(self):
        """Calcaulte percentile from z_score"""
        return norm.cdf(self.zscore()) * 100

    def __repr__(self):
        return f"Zind(L={self.L}, M={self.M}, S={self.S}, y={self.y})"
    
    
class ZscoreHeight(Zscore):
    """Z-score calculation for height"""
        #              [y/M(t)]^L(t) - 1        y - M(t)
        #   Zind =  -----------------------  = -----------
        #               S(t)L(t)                 stDev(t)
    
    def __init__(self, L, M, S, y):
        self.L = L
        self.M = M
        self.S = S
        self.y = y
    
    def zscore(self):
        return ((self.y/self.M)**self.L - 1) / (self.S * self.L)
    
    def z_score_to_percentile(self):
        return norm.cdf(self.zscore()) * 100
    
    def __repr__(self): 
        return f"Zind(L={self.L}, M={self.M}, S={self.S}, y={self.y})"
    

def interpolate_lms(age, data):
    """
    Interpolate L, M, and S values for a given age using linear interpolation.
    
    Args:
        age (float): The age in months.
        data (pandas.DataFrame): The data frame containing L, M, and S values.
        
    Returns:
        tuple: A tuple containing the interpolated L, M, and S values.
    """
    # logger.debug(f"Interpolating LMS: {age=} {data.head()=}")
    if age <=1:
        # age_lower = data.index[data.index <= 1].max()
        age = round(age, 0)
        L = data.loc[age, 'L'] 
        M = data.loc[age, 'M'] 
        S = data.loc[age, 'S'] 
        return L, M, S
    
    age_lower = data.index[data.index <= age].max()
    age_upper = data.index[data.index >= age].min()
    
    age_diff = age_upper - age_lower
    age_frac = (age - age_lower) / age_diff
    
    L = data.loc[age_lower, 'L'] + age_frac * (data.loc[age_upper, 'L'] - data.loc[age_lower, 'L'])
    M = data.loc[age_lower, 'M'] + age_frac * (data.loc[age_upper, 'M'] - data.loc[age_lower, 'M'])
    S = data.loc[age_lower, 'S'] + age_frac * (data.loc[age_upper, 'S'] - data.loc[age_lower, 'S'])
    logger.debug(f"Interpolated LMS: {age=} {L=}, {M=}, {S=}")
    return L, M, S

def calc_bmi(weight, height):
    """Calculate BMI from weight and height"""
    return weight / ((height / 100) ** 2)