
import os
import re
import numpy as np
import json

DATA_DIR = "_data"


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
  def __init__(self, place, amount, cost_challenge, cost_strength):
    self.place = place
    self.amount = amount
    self.cost_challenge = cost_challenge
    self.cost_strength = cost_strength

  def __str__(self):
    return "%s, %d, %d, %d" % (self.place, self.amount, self.cost_challenge, self.cost_strength)


# (place_name, amount, cost_challenge, cost_strength)
def extract_places_amounts_costs(place_type, gq_name, place_and_amount):
  if place_type == "御魂":
    place_name = "%s/%s" % (place_type, gq_name)
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    amount = sum([int(x) for x in results])
    return (place_name, amount, 0, 4),
  elif place_type == "探索":
    results = re.findall("(.*?)\\(.*?\\*([0-9]*)\\)", place_and_amount)
    ans = []
    for result in results:
      place_name = "%s/%s/%s" % (place_type, gq_name, result[0])
      amount = int(result[1])
      ans.append((place_name, amount, 0, 3))
    return ans
  elif place_type == "挑战":
    result = re.findall("(.*?)\\(.*?\\*([0-9]*)\\)", place_and_amount)
    assert len(result) == 1
    result = result[0]
    place_name = "%s/%s/%s" % (place_type, gq_name, result[0])
    amount = int(result[1])
    return (place_name, amount, 1, 0),
  elif place_type == "秘闻":
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    place_name = "%s/%s" % (place_type, gq_name)
    amount = sum([int(r) for r in results])
    return (place_name, amount, 0, 3),
  elif place_type == "妖气":
    results = re.findall(".*?\\(.*?\\*([0-9]*)\\)", place_and_amount)
    place_name = "%s/%s" % (place_type, gq_name)
    amount = sum([int(r) for r in results])
    return (place_name, amount, 0, 3),
  else:
    raise NameError("Unknown place_type: %s" % place_type)


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

        #
        # try:
        places_amounts_costs = extract_places_amounts_costs(place_type, gq, place_and_amount)
        # except NameError:
        #   continue

        #
        costs = cost.split("/")
        total_amount = int(costs[0])
        total_cost_strength = int(costs[1])

        assert total_amount == sum([am for _, am, _, _ in places_amounts_costs])
        assert total_cost_strength == sum([cs for _, _, _, cs in places_amounts_costs])

        for place, amount, cost_challenge, cost_strength in places_amounts_costs:
          xs = XS(place, amount, cost_challenge, cost_strength)
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

  # mat_valid = np.zeros((n_places, n_monsters), dtype=np.int)
  mat_amount = np.zeros((n_places, n_monsters), dtype=np.int)
  mat_cost_challenge = np.zeros((n_places,), dtype=np.int)
  mat_cost_strength = np.zeros((n_places,), dtype=np.int)

  for m_ind, monster in enumerate(monsters):
    for xs in monster.xs_list:
      p_ind = np.where([p == xs.place for p in places])
      assert len(p_ind) == 1
      p_ind = p_ind[0]
      assert p_ind.shape[0] == 1
      p_ind = p_ind[0]
      # mat_valid[p_ind, m_ind] = 1
      mat_amount[p_ind, m_ind] = xs.amount
      mat_cost_challenge[p_ind] = xs.cost_challenge
      mat_cost_strength[p_ind] = xs.cost_strength

  # with open(os.path.join(DATA_DIR, "monsters.csv"), "w") as fp:
  #   fp.write("name" + "\n")
  #   for monster in monsters:
  #     fp.write(monster.name + "\n")
  #
  # with open(os.path.join(DATA_DIR, "places.csv"), "w") as fp:
  #   fp.write("name" + "\n")
  #   for place in places:
  #     fp.write(place + "\n")
  #
  # np.savetxt("valid.csv", mat_valid, "%2d")
  # np.savetxt("amount.csv", mat_amount, "%2d")
  # np.savetxt("cost_challenge.csv", mat_cost_challenge, "%2d")
  # np.savetxt("cost_strength.csv", mat_cost_strength, "%2d")

  data = {
    "monsters": [m.name for m in monsters],
    "places": places,
    "amounts": mat_amount.tolist(),
    "cost_challenge": mat_cost_challenge.tolist(),
    "cost_strength": mat_cost_strength.tolist(),
    # "valid": mat_valid.tolist(),
    "num_monsters": str(len(monsters)),
    "num_places": str(len(places)),
  }
  with open(os.path.join(DATA_DIR, "data.json"), "w") as fp:
    json.dump(data, fp)


if __name__ == "__main__":
  main()
