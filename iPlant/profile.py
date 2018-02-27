

class Profile:
    name = 'profile'

    def __init__(self, profile):
        self.light = profile[1]
        self.heatMin = profile[2]
        self.heatMax = profile[3]
        self.moistMin = profile[4]
        self.moistMax = profile[5]
        self.location = profile[6]
        self.fix_doors = profile[7]