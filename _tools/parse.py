
import os
import re
import numpy as np
import json
import xpinyin

DATA_DIR = "_data"


CAP_NUMS = ["壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖", "拾"];
NUMS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"];

class Monster(object):
  def __init__(self, name):
    self.name = name
    self.xs_list = []

  def __repr__(self):
    my_str = "Name: %s" % self.name
    for xs in self.xs_list:
      my_str += "\n" + str(xs)
    return my_str


class XS(object):
  def __init__(self, place, amount, cost_challenge, cost_strength, typeid, level):
    self.place = place
    self.amount = amount
    self.cost_challenge = cost_challenge
    self.cost_strength = cost_strength
    self.typeid = typeid
    self.level = level

  def __str__(self):
    return "%s, %d, %d, %d, %d, %d" % (self.place, self.amount, self.cost_challenge, self.cost_strength, self.typeid, self.level)


# Old: (place_name, amount, cost_challenge, cost_strength)
# (place_name, amount, cost_challenge, cost_strength, typeid, level)
def extract_places_amounts_typeid_level(place_type, gq_name, place_and_amount):
  if place_type == "御魂":
    place_name = "%s/%s" % (place_type, gq_name)
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    amount = sum([int(x) for x in results])
    level = get_level(gq_name, NUMS)
    if level == None:
      level = 10
    return (place_name, amount, 0, 4, 0, level),
  elif place_type == "探索":
    results = re.findall("(.*?)\\(.*?\\*([0-9]*)\\)", place_and_amount)
    ans = []
    for result in results:
      place_name = "%s/%s/%s" % (place_type, gq_name, result[0])
      amount = int(result[1])
      level = 1 if "首领" in result[0] else 0
      ans.append((place_name, amount, 0, 3, 1, level))
    return ans
  elif place_type == "挑战":
    result = re.findall("(.*?)\\(.*?\\*([0-9]*)\\)", place_and_amount)
    assert len(result) == 1
    result = result[0]
    place_name = "%s/%s/%s" % (place_type, gq_name, result[0])
    amount = int(result[1])
    return (place_name, amount, 1, 0, 2, 0),
  elif place_type == "妖气":
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    place_name = "%s/%s" % (place_type, gq_name)
    amount = sum([int(r) for r in results])
    return (place_name, amount, 0, 3, 3, 0),
  elif place_type == "秘闻":
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    place_name = "%s/%s" % (place_type, gq_name)
    amount = sum([int(r) for r in results])
    level = get_level(place_name, CAP_NUMS)
    if level is None:
      level = 10
    return (place_name, amount, 0, 3, 4, level),
  else:
    raise NameError("Unknown place_type: %s" % place_type)

def get_level(place_name, arr):
  level = np.where([cn in place_name for cn in arr])[0]
  if (len(level) != 1):
    return None
  return level.item()

def main():

  monsters = []

  for fn in os.listdir(os.path.join(DATA_DIR, "monsters")):

    monster_name = os.path.splitext(fn)[0]
    monster = Monster(monster_name)

    with open(os.path.join(DATA_DIR, "monsters", fn)) as fp:
      print("Parsing %s" % fn)
      for line in fp.readlines():
        line = line.replace("\n", "")
        cols = line.split(",")
        assert len(cols) == 4
        place_type = cols[0].strip()
        gq = cols[1].strip()
        place_and_amount = cols[2].strip()
        cost = cols[3].strip()

        places_amounts_typeid_level = extract_places_amounts_typeid_level(place_type, gq, place_and_amount)

        #
        costs = cost.split("/")
        total_amount = int(costs[0])
        total_cost_strength = int(costs[1])

        assert total_amount == sum([am for _, am, _, _, _, _ in places_amounts_typeid_level])
        assert total_cost_strength == sum([cs for _, _, _, cs, _, _ in places_amounts_typeid_level])

        for place, amount, cost_challenge, cost_strength, typeid, level in places_amounts_typeid_level:
          xs = XS(place, amount, cost_challenge, cost_strength, typeid, level)
        monster.xs_list.append(xs)

    monsters.append(monster)

    print("\nBEGIN " + ">" * 74)
    print(monster)
    print("END " + "<" * 76 + "\n")

  places = []
  for monster in monsters:
    for xs in monster.xs_list:
      places.append(xs.place)
  print("len(all_places) = %d" % len(places))
  places = sorted(list(set(places)))
  print("len(all_places) = %d" % len(places))
  print("len(monsters) = %d" % len(monsters))

  n_places = len(places)
  n_monsters = len(monsters)

  mat_amount = np.zeros((n_places, n_monsters), dtype=np.int)
  mat_cost_challenge = np.zeros((n_places,), dtype=np.int)
  mat_cost_strength = np.zeros((n_places,), dtype=np.int)
  mat_typeid = np.zeros((n_places,), dtype=np.int)
  mat_level = np.zeros((n_places,), dtype=np.int)

  for m_ind, monster in enumerate(monsters):
    for xs in monster.xs_list:
      p_ind = np.where([p == xs.place for p in places])
      assert len(p_ind) == 1
      p_ind = p_ind[0]
      assert p_ind.shape[0] == 1
      p_ind = p_ind[0]
      mat_amount[p_ind, m_ind] = xs.amount
      mat_cost_challenge[p_ind] = xs.cost_challenge
      mat_cost_strength[p_ind] = xs.cost_strength
      mat_typeid[p_ind] = xs.typeid
      mat_level[p_ind] = xs.level

  pin = xpinyin.Pinyin()
  data = {
    "monsters": sorted([m.name for m in monsters], key=pin.get_pinyin),
    "places": places,
    "amounts": mat_amount.tolist(),
    "typeids": mat_typeid.tolist(),
    "levels": mat_level.tolist(),
    # "cost_challenge": mat_cost_challenge.tolist(),
    # "cost_strength": mat_cost_strength.tolist(),
    # "valid": mat_valid.tolist(),
    "num_monsters": str(len(monsters)),
    "num_places": str(len(places)),
  }
  with open(os.path.join(DATA_DIR, "data.json"), "w") as fp:
    json.dump(data, fp)


if __name__ == "__main__":
  main()
