def get_epley(weight: float, repetitions: int, rir: int=0):
    epley = round ( weight * ( 1 + ( (repetitions + rir) / 30 ) ) , 2 )
    return epley

def get_brzycki(weight: float, repetitions: int, rir: int=0):
    brzycki = round ( weight * ( 36 / ( 37 - ( repetitions + rir ) ) ), 2 )
    return brzycki