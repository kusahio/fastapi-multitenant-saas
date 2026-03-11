from enum import Enum

class BusinessType(str, Enum):
  STORE = "store"           # almacén, kiosco
  FOOD = "food"             # rotisería, take away
  RESTAURANT = "restaurant" # con mesas