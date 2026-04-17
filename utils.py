from enum import Enum
import random

class ESTADOS_UNIFILA(Enum):
    #analogía con patron de tolerancia a fallos circuit breaker
    NORMAL = 'NORMAL' #CLOSED
    SATURANDOSE = 'SATURANDOSE' #HALF_OPEN
    SATURADO = 'SATURADO' # OPEN


def probabilidad_atencion():
    return random.randint(1,15) / 10