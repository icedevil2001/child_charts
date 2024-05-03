

class Weight:
    def __init__(self, weight, unit):
        self.weight = weight
        self.unit = unit
    
    def to_kilograms(self):
        if self.unit == 'kg':
            return self.weight
        elif self.unit == 'lbs':
            return self.weight * 0.453592
        elif self.unit == 'lbs.oz':
            lb, oz = self.weight.split('.',1)
            return (int(lb) * 0.453592) + (int(oz) * 0.0283495)
        elif self.unit == 'g':
            return self.weight / 1000
        elif self.unit == 'oz':
            return self.weight * 0.0283495
        else:   
            return None
    
    def to_pounds(self):
        if self.unit == 'lbs':
            return self.weight
        elif self.unit == 'lbs.oz':
            lb, oz = self.weight.split('.',1)
            return int(lb) + (int(oz) * 0.0625)
        elif self.unit == 'kg':
            return self.weight * 2.20462
        elif self.unit == 'g':
            return self.weight * 0.00220462
        elif self.unit == 'oz':
            return self.weight * 0.0625
        else:
            return None
    
class Length:
    def __init__(self, height, unit):
        self.height = height
        self.unit = unit

    def to_cm(self):
        if self.unit == 'cm':
            return self.height
        elif self.unit == 'm':
            return self.height * 100
        elif self.unit == 'in':
            return self.height * 2.54
        elif self.unit == 'ft':
            return self.height * 30.48
        else:
            return None
        
    def to_ft(self):
        if self.unit == 'ft':
            return self.height
        elif self.unit == 'in':
            return self.height * (1/12)
        elif self.unit == 'm':
            return self.height * 3.28084
        elif self.unit == 'cm':
            return self.height * 0.0328084
        else:
            return None
