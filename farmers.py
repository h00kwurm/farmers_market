#!/usr/bin/python3

import csv
import itertools
import pygal
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
    return None
  else:
    return xyless

def plot_percentages_of_items(percentages, outputfile):
  bar_chart = pygal.Bar(style=pygal.style.LightSolarizedStyle, show_legend=False, x_label_rotation=20)
  bar_chart.title = "What chance do I have of finding _ at my Farmer's market?"
  bar_chart.x_labels = [name for (name, percent) in percentages]
  bar_chart.add('', [round(100*percent, 1) for (name, percent) in percentages])
  bar_chart.render_to_file(outputfile)

def percentages_of_items(items, markets):
  count = [0]*len(items)
  for market in markets:
    for index, item in enumerate(items):
      if market.get(item) == 'Y':
        count[index] += 1
  return [(items[index], count[index]/len(markets)) for index in range(len(items))]

def average_number_of_items(items, markets):
  item_count_average = 0
  for market_index, market in enumerate(markets):
    current_item_count = 0
    for item in items:
      if market.get(item) == 'Y':
        current_item_count += 1
    item_count_average = (item_count_average * market_index + current_item_count) / (market_index + 1)
  print('average number of items: ', item_count_average)

def array_add(array_one, array_two):
  if len(array_one) != len(array_two):
    raise Exception('invalid sizing')
  output = []*len(array_one)
  return [(array_one[index] + array_two[index]) for index in range(len(array_one))]

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
          probability_map[(item_a, item_b)] = array_add(probability_map[(item_a, item_b)], [1, 1])
        else:
          probability_map[(item_a, item_b)] = array_add(probability_map[(item_a, item_b)], [0, 1])
      probability_map[(item_a, item_b)] = pair_map_to_probability(probability_map[(item_a, item_b)])
  return probability_map

# i was curious about independence
# max(P(A|B), P(B|A))
# again, could be faster because duplicates dist(x, y) == dist(y, x)
# i'll choose memory over speed here (dont need to keep 'seen' list)
# or i could just regenerate all the combinations using itertools...
def find_largest_disparity(probabilities):
  max_disparity = ["", "", 0]
  for (item_a, item_b) in probabilities.keys():
    distance = abs(probabilities[(item_a, item_b)] - probabilities[(item_b, item_a)])
    if distance > max_disparity[2]:
      max_disparity = [item_a, item_b, distance]
  return max_disparity

def main():

  data_file_path = find_local_datafile()
  if data_file_path is None:
    return fail('couldnt find the data file in this directory')

  markets, legend = parse_datafile(data_file_path)
  if len(markets) == 0:
    return fail('found no markets in datafile')

  xyless = do_they_all_have_xy(markets)
  if xyless is not None:
    print(xyless)

  items = ['bakedgoods', 'cheese', 'crafts', 'flowers', 'eggs', 'seafood', 'herbs', 'vegetables', 'honey', 'jams', 'maple', 'meat', 'nursery', 'nuts', 'plants', 'poultry', 'prepared', 'soap', 'trees', 'wine']

  # average_number_of_items(items, markets)
  item_percents = percentages_of_items(items, markets)
  plot_percentages_of_items(item_percents, 'graphs/percentages.svg')
  
  # probabilities = generate_pairwise_conditional_probabilities(items, markets)
  
  # disparity = find_largest_disparity(probabilities)
  # print("max disparity between P(a|b) and P(b|a)")
  # print(disparity)
  # print(probabilities[(disparity[0], disparity[1])], probabilities[(disparity[1], disparity[0])])
  return EXIT_SUCCESS

if __name__ == '__main__':
  exit(main())