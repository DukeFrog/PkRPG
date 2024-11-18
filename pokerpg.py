import json
import random

# Load data from JSON files
def load_json(file):
    with open(file, 'r') as f:
        return json.load(f)

enemies = load_json('data/enemies.json')
gear = load_json('data/gear.json')
craftitems = load_json('data/craftitems.json')
craftrecipes = load_json('data/craftrecipes.json')
locations = load_json('data/locations.json')

# Player Stats and Data
player = {
    "name": "Hero",
    "level": 1,
    "xp": 0,
    "attack": 5,
    "defense": 5,
    "hp": 10,
    "current_hp": 10,
    "gear": [],
    "location": "Hajimeru Town",
    "inventory": []
}

# Functions to handle the game
def level_up():
    player["level"] += 1
    player["xp"] -= 100
    player["attack"] += 1
    player["defense"] += 1
    player["hp"] += 1
    player["current_hp"] = player["hp"]
    print(f"Level Up! You are now level {player['level']}.")

def check_area():
    current_location = player["location"]
    location_data = locations[current_location]
    description = location_data.get("description", "There's nothing notable about this area.")
    
    print(f"Location: {current_location}")
    print(f"Description: {description}")

def equip_item(item_name):
    if item_name not in player["inventory"]:
        print(f"You don't have a {item_name} in your inventory!")
        return
    
    if len(player["gear"]) >= 3:
        print("You can only equip up to 3 items at once!")
        return

    # Check for the item's validity
    if item_name in player["inventory"]:
        # Equip the item by adding it to the equipped list
        player["gear"].append(item_name)
        item = gear[item_name]
        player["attack"] += item.get("attack", 0)
        player["defense"] += item.get("defense", 0)
        player["hp"] += item.get("hp", 0)
        print(f"You have equipped {item_name}.")
    else:
        print(f"You don't have a {item_name} to equip.")


def unequip_item(item_name):
    if item_name not in player["gear"]:
        print("This item is not equipped.")
        return
    item = gear[item_name]
    player["gear"].remove(item_name)
    player["attack"] -= item.get("attack", 0)
    player["defense"] -= item.get("defense", 0)
    player["hp"] -= item.get("hp", 0)
    print(f"Unequipped {item_name}!")

def move(location):
    current = player["location"]
    if location not in locations[current]["connections"]:
        print("You can't move there from here!")
        return
    player["location"] = location
    print(f"You moved to {location}.")

def encounter():
    loc = locations[player["location"]]  # Get current location
    encounter_roll = random.uniform(0, 100)  # Roll a random number between 0 and 100

    # Calculate cumulative probabilities for each enemy type
    cumulative_probability = 0
    for enemy_type, chance in loc["encounter_rates"].items():
        cumulative_probability += chance
        if encounter_roll <= cumulative_probability:
            encounter_enemy(enemy_type)
            return
    # If no encounter happens, print a message
    print("No enemies found.")

def encounter_enemy(enemy_type):
    enemies_of_type = [e for e in enemies if e["class"] == enemy_type]
    enemy_template = random.choice(enemies_of_type)
    # Create a fresh copy of the enemy to avoid modifying the template
    enemy = {
        "name": enemy_template["name"],
        "class": enemy_template["class"],
        "hp": enemy_template["hp"],
        "attack": enemy_template["attack"],
        "defense": enemy_template["defense"],
        "xp": enemy_template["xp"],
        "drops": enemy_template["drops"]
    }
    print(f"A wild {enemy['name']} appears!")
    fight(enemy)

def fight(enemy):
    while player["current_hp"] > 0 and enemy["hp"] > 0:
        print(f"Player HP: {player['current_hp']} | {enemy['name']} HP: {enemy['hp']}")
        action = input("Choose your action: (a)ttack, (r)un: ").lower()
        if action == "a":
            damage = max(1, player["attack"] - enemy["defense"])
            enemy["hp"] -= damage
            print(f"You dealt {damage} damage to {enemy['name']}!")
            if enemy["hp"] <= 0:
                print(f"You defeated {enemy['name']}!")
                player["xp"] += enemy["xp"]
                if player["xp"] >= 100:
                    level_up()
                drop = random.choice(enemy["drops"])
                print(f"The enemy dropped {drop}!")
                player["inventory"].append(drop)
                break
            damage = max(1, enemy["attack"] - player["defense"])
            player["current_hp"] -= damage
            print(f"The {enemy['name']} hit you for {damage} damage!")
        elif action == "r":
            print("You ran away!")
            break
    else:
        if player["current_hp"] <= 0:
            print("You have been defeated...")
            # Player loses all items, including equipped gear
            player["inventory"].clear()
            player["gear"].clear()  # Assuming you have an "equipped" list
            print("You lost all your items!")
            # Optionally, you could send the player to a safe location, like "Front Village"
            player["location"] = "Front Village"  # Example of setting a starting location again

    # Heal player after the battle
    player["current_hp"] = player["hp"]
    print("You have healed to full HP!")


def craft_item(item_name):
    if item_name not in craftrecipes:
        print("This item cannot be crafted.")
        return
    recipe = craftrecipes[item_name]
    for ingredient, quantity in recipe.items():
        if player["inventory"].count(ingredient) < quantity:
            print(f"You lack the materials to craft {item_name}.")
            return
    for ingredient, quantity in recipe.items():
        for _ in range(quantity):
            player["inventory"].remove(ingredient)
    print(f"You crafted {item_name}!")
    player["inventory"].append(item_name)

def display_inventory():
    if not player["inventory"]:
        print("Inventory is empty.")
        return
    # Count the occurrences of each item
    item_counts = {}
    for item in player["inventory"]:
        if item in item_counts:
            item_counts[item] += 1
        else:
            item_counts[item] = 1
    # Display items and their counts
    print("Inventory:")
    for item, count in item_counts.items():
        print(f"  {item}: {count}")

# Game Loop
while True:
    print(f"Current Location: {player['location']} | HP: {player['current_hp']}/{player['hp']} | ATK: {player['attack']} | DEF: {player['defense']}")
    print("1. Move | 2. Check Inventory | 3. Equip | 4. Craft | 5. Encounter | 6. Check Area | 7. Exit")
    choice = input("Choose an action: ")
    if choice == "1":
        print(f"Available locations: {locations[player['location']]['connections']}")
        destination = input("Where do you want to go? ")
        move(destination)
    elif choice == "2":
        display_inventory()
    elif choice == "3":
        item_name = input("Enter item to equip or unequip: ")
        if item_name in player["gear"]:
            unequip_item(item_name)
        else:
            equip_item(item_name)
    elif choice == "4":
        item_name = input("Enter item to craft: ")
        craft_item(item_name)
    elif choice == "5":
        encounter()
    elif choice == "7":
        print("Goodbye!")
        break
    elif choice == "6":
        check_area()
    else:
        print("Invalid choice.")
