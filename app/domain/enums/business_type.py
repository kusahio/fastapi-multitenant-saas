from enum import Enum

class BusinessType(str, Enum):
  STORE = "store"
  FOOD = "food"
  RESTAURANT = "restaurant"