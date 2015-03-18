#!/usr/bin/python3

import csv
import itertools
from os import listdir
from os.path import isfile, join, dirname

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def fail(message):
  if message is not None:
    print(message)
  return EXIT_FAILURE

def find_local_datafile():
  data_file_path = None
  for item in listdir('/home/anatraj/Code/python/farmers_market/'):
    if isfile(item) and 'csv' in item:
      data_file_path = item
      break
  return data_file_path

def parse_datafile(data_file_path):
  all_the_markets = []
  legend = []
  with open(data_file_path, 'rt') as csvfile:
    legend = [item.lower() for item in csvfile.readline().strip().split(',')]
    data_reader = csv.reader(csvfile)
    counter = 1
    for line in data_reader:
      newMarket = Market(line, legend)
      all_the_markets.append(newMarket)
  return all_the_markets, legend

class Market(object):
  def __init__(self, line, legend):
    self.market_map = {}
    if len(line) != len(legend):
      raise Exception('broken mapping')
    for index, value in enumerate(line):
      self.market_map[legend[index]] = value

  def get(self, property_name):
    if property_name in self.market_map:
      return self.market_map[property_name]
    return None 

  def __str__(self):
    return str(self.market_map)

def do_they_all_have_xy(markets):
  xyless = []
  for market in markets:
    if market.get('x') is None or market.get('y') is None:
      xyless.append(market)
  if len(xyless) == 0:
    return (True, None)
  else:
    return (False, xyless)

def percentages_of_items(items, markets):
  count = [0]*len(items)
  for market in markets:
    for index, item in enumerate(items):
      if market.get(item) == 'Y':
        count[index] += 1
  print("total markets: ", len(markets))
  for index, item in enumerate(items):
    print(item, count[index]/len(markets)) 

def average_number_of_items(items, markets):
  item_count_average = 0
  for market_index, market in enumerate(markets):
    current_item_count = 0
    for item in items:
      if market.get(item) == 'Y':
        current_item_count += 1
    item_count_average = (item_count_average * market_index + current_item_count) / (market_index + 1)
  print("average number of items: ", item_count_average)

def pair_array_add(array_one, array_two):
  return [array_one[0] + array_two[0], array_one[1] + array_two[1]]

def pair_map_to_probability(pair):
  return (pair[0] / float(pair[1]))

# this could be more efficient using bayes theorem to not have to do both P(A|B) and P(B|A)
def generate_pairwise_conditional_probabilities(items, markets):
  probability_map = {}
  for (item_a, item_b) in itertools.permutations(items, 2):
    if item_a != item_b:
      probability_map[(item_a, item_b)] = [0, 0]
      for market in markets:
        if market.get(item_b) == 'N':
          continue
        if market.get(item_b) == 'Y' and market.get(item_a) == 'Y':
          probability_map[(item_a, item_b)] = pair_array_add(probability_map[(item_a, item_b)], [1, 1])
        else:
          probability_map[(item_a, item_b)] = pair_array_add(probability_map[(item_a, item_b)], [0, 1])
      probability_map[(item_a, item_b)] = pair_map_to_probability(probability_map[(item_a, item_b)])
  return probability_map

def main():

  data_file_path = find_local_datafile()
  if data_file_path is None:
    return fail("couldnt find the data file in this directory")

  markets, legend = parse_datafile(data_file_path)
  if len(markets) == 0:
    return fail("found no markets in datafile")

  all_xy, xyless = do_they_all_have_xy(markets)
  if not all_xy:
    print(xyless)

  items = ['bakedgoods', 'cheese', 'crafts', 'flowers', 'eggs', 'seafood', 'herbs', 'vegetables', 'honey', 'jams', 'maple', 'meat', 'nursery', 'nuts', 'plants', 'poultry', 'prepared', 'soap', 'trees', 'wine']

  average_number_of_items(items, markets)
  percentages_of_items(items, markets)
  # probabilities = generate_pairwise_conditional_probabilities(items, markets)

  return EXIT_SUCCESS

if __name__ == '__main__':
  exit(main())