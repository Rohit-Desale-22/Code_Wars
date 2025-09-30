import random
import math
from teams.helper_function import Troops, Utils

team_name = "404 Not Found"
troops = [
    Troops.wizard, Troops.minion, Troops.archer, Troops.musketeer,
    Troops.dragon, Troops.barbarian, Troops.valkyrie, Troops.prince
]
deploy_list = Troops([])

team_signal = "False,king,None,None,None,False"


def update_team_signal(team_signal, **kwargs):
    """
    Updates values inside the team_signal string while keeping it within 200 characters.
    """
    # Split the string into a list of values
    signal_parts = team_signal.split(",")

    # Define the mapping of variable names to their positions
    mapping = {
        "started_deploying": 0,
        "opp_last_deployed_troop": 1,
        "opp_latest_deployed_troop": 2,
        "my_last_troop_deployed": 3,
        "last_seen_balloon": 4,
        "attack_balloon": 5
    }

    # Update only the provided values
    for key, value in kwargs.items():
        if key in mapping:
            signal_parts[mapping[key]] = str(value)  # Convert value to string

    # Convert back to a string
    updated_signal = ",".join(signal_parts)

    # Ensure it does not exceed 200 characters
    if len(updated_signal) > 200:
        raise ValueError("team_signal exceeds 200 characters!")

    return updated_signal



def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal



def max_score(troop_list, scores):
    if not troop_list:
        return None
    return max(troop_list, key=lambda troop: scores.get(troop.name, 0))  # Use troop.name as key


def max_score_prince(troop_list, scores):
    filtered_troops = [troop for troop in troop_list if troop.name.lower() != "prince"]
    if not filtered_troops:  
        print("⚠ DEBUG: No suitable troop found for prince pairing.")
        return None  
    return max(filtered_troops, key=lambda troop: scores.get(troop.name, 0))  # Fixed key lookup

def max_score_wizard(troop_list, scores):
    filtered_troops = [troop for troop in troop_list if troop.name.lower() != "wizard"]
    if not filtered_troops:  
        print("⚠ DEBUG: No suitable troop found for wizard pairing.")
        return None  
    return max(filtered_troops, key=lambda troop: scores.get(troop.name, 0))  # Fixed key lookup


def get_actually_deployable_troops(arena_data):
    my_tower = arena_data["MyTower"]
    deployable_troops = my_tower.deployable_troops
    available_elixir = my_tower.total_elixir
    #print("elixir available is")
    #print(available_elixir)

    actually_deployable = []

    #print(f"🔍 DEBUG: Deployable troops: {deployable_troops}, Available Elixir: {available_elixir}")

    for troop_name in deployable_troops:
        troop = Troops.troops_data.get(troop_name)
        #print(troop)
        if available_elixir >= troop.elixir:
            actually_deployable.append(troop)
            #print(f"✅ DEBUG: Added {troop.name} to deployable list")

    #print(f"⚠ DEBUG: Actually deployable troops: {actually_deployable}")
    #print(actually_deployable)
    return actually_deployable if actually_deployable else []


def enemy_deployed_troop (arena_data) :
    global team_signal
    print("entered enemy deployed_troop")
    if arena_data["OppTroops"] :
        print("arena data troops not empty")
        print(arena_data["OppTroops"][-1].name)
        if team_signal :
            print(team_signal.split(",")[1])
        if team_signal and arena_data["OppTroops"][-1].name == team_signal.split(",")[1] :
                print("enemy did not deploy troops")
                return False, None
        else :
            print("enemy deployed troops")
            print("position =")
            print(min (3,math.floor((arena_data["OppTroops"][-1].position[1])/25)))
            opp_latest_deployed_troop = arena_data["OppTroops"][-1].name
            team_signal = update_team_signal(team_signal, opp_last_deployed_troop = opp_latest_deployed_troop) 
            print("returning True")
            return True, min (3,math.floor((arena_data["OppTroops"][-1].position[1])/25))
        
    else :
        return False, None

def pairing_position_prince_2 (best_troop, position_prince_2) :
    return position_prince_2.get(best_troop, None)

def pairing_position_wizard_2 (best_troop, position_wizard_2) :
    return position_wizard_2.get(best_troop, None)

def pairing_position_prince_3 (best_troop, position_prince_3) :
    return position_prince_3.get(best_troop, None)

def pairing_position_wizard_3 (best_troop, position_wizard_3) :
    return position_wizard_3.get(best_troop, None)

def defend(arena_data, troop_scores_defend):
    print("entered defend")
    actually_deployable_troops = get_actually_deployable_troops(arena_data)
    if actually_deployable_troops:
        # Use get() with default value of 0 for missing troops
        print("available troops to defend are")
        for troops in actually_deployable_troops :
            print(f"Checking {troops.name.lower()} -> Score: {troop_scores_defend.get(troops.name.lower(), 'Not Found')}")
            print(troops.name)
        best_troop = max(actually_deployable_troops, key=lambda troop: troop_scores_defend.get(troop.name.lower(), 0),  # Use troop.name.lower()
    default=None  # Prevents errors if list is empty
)

        print("best troop to defend is")
        print(best_troop)
        if best_troop:
            print("adding best troop to defend to list")
            deploy_list.list_.append((best_troop.name, (0,1)))

def best_stratergy_2(arena_data, troop, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2):
    global team_signal
    print("entered best stratergy")
    elixir = arena_data["MyTower"].total_elixir
    troops = get_actually_deployable_troops(arena_data)
    position = None

    if troop == "prince":
        best_troop = max_score_prince(troops, prince_pairing)
        if best_troop is None:  # ✅ Prevent error
            return None, None
        elixir_required = 5 + best_troop.elixir
        position = pairing_position_prince_2(best_troop, position_prince_2)
    else:
        best_troop = max_score_wizard(troops, wizard_pairing)
        if best_troop is None:  # ✅ Prevent error
            return None, None
        elixir_required = 5 + best_troop.elixir
        position = pairing_position_wizard_2(best_troop, position_wizard_2)

    if elixir < elixir_required:
        team_signal = update_team_signal(team_signal, deploy=False)
        return None, None  # ✅ Return safely
    print("best troop to pair is")
    print(best_troop)
    return best_troop, position


def best_stratergy_3 (arena_data, troop, prince_pairing, wizard_pairing, position_prince_3, position_wizard_3) :
    global team_signal
    troops = get_actually_deployable_troops(arena_data)
    position = None
    if troop == "prince" :

        best_troop = max_score_prince (troops, prince_pairing)
        position = pairing_position_prince_3 (best_troop, position_prince_3)
    else :
        best_troop = max_score_wizard (troops, wizard_pairing)
        position = pairing_position_wizard_3 (best_troop, position_wizard_3)

    return best_troop, position

def best_troop_respond (arena_data, enemy_troop, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend) :
    print("entered best troop respond")
    actually_deployable_troops = get_actually_deployable_troops(arena_data)
    #print("actually deployable troops are")
    #print(actually_deployable_troops)
    name = enemy_troop.name.lower()
    #print("name of enemy troop is")
    #print(name)
    best_troop = None
    if name == "wizard" :
        best_troop = max_score(actually_deployable_troops, giant_defend)
    elif name == "dragon" :
        best_troop = max_score(actually_deployable_troops, dragon_defend)
        if best_troop and best_troop.name.lower() in ["valkyrie", "prince", "barbarian"]:
            return None
    elif name == "wizard" :
        best_troop = max_score(actually_deployable_troops, wizard_defend)
    elif name == "archer" :
        best_troop = max_score(actually_deployable_troops, archer_defend)
    elif name == "skeleton" :
        best_troop = max_score(actually_deployable_troops, skeleton_defend)
    elif name == "musketeer" :
        best_troop = max_score(actually_deployable_troops, musketeer_defend)
    elif name == "valkyrie" :
        best_troop = max_score(actually_deployable_troops, valkyrie_defend)
    elif name == "knight" :
        best_troop = max_score(actually_deployable_troops, knight_defend)
    elif name == "prince" :
        best_troop = max_score(actually_deployable_troops, prince_defend)
    elif name == "barbarian" :
        best_troop = max_score(actually_deployable_troops, barbarian_defend)
    elif name == "minion" :
        best_troop = max_score(actually_deployable_troops, minion_defend)
        if best_troop and best_troop.name in ["valkyrie", "prince", "barbarian"]:
            return None
    if best_troop == None :
        return None
    else :
        return best_troop

def troop_and_position (enemy_troop, area, arena_data, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, position_prince_3, position_wizard_3, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend) :
    print("entered troop-and_position")
    my_troops = get_actually_deployable_troops(arena_data)
    #print("available troops")
    #print(my_troops)
    elixir = arena_data["MyTower"].total_elixir
    x = int(enemy_troop.position[0])
    #print(x)
    #print("x coordinate")

    if area == 2 :
        print("entered to attack area 2")   
        best_troop = best_troop_respond (arena_data, enemy_troop, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend)
        if best_troop and best_troop.name.lower() in ["prince", "wizard"]:
            troop, position = best_stratergy_2 (arena_data, troop, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2)
            if troop == None :
                if best_troop.lower() == "wizard" :
                    deploy_list.list_.append((best_troop.name, (0,35)))
                else :
                    deploy_list.list_.append((best_troop.name, (0,35)))
                return

            if troop.elixir + 5 <= elixir :
                if best_troop.lower() == "wizard" :
                    deploy_list.list_.append((best_troop.name, (0,35)))
                    deploy_list.list_.append((troop, position))
                else :
                    deploy_list.list_.append((best_troop.name, (0,35)))
                    deploy_list.list_.append((troop.name, position))
            else :
                if best_troop.lower() == "wizard" :
                    deploy_list.list_.append((best_troop.name, (0,35)))
                else :
                    deploy_list.list_.append((best_troop.name, (0,35)))

        elif best_troop and best_troop.name.lower() in ["barbarian", "valkyrie"]:
            position = (x,50)
            deploy_list.list_.append((best_troop, position))
        elif best_troop and best_troop.name.lower() == "archer" :
            min_val = int(max(-25, x - 5))
            max_val = int(min(25, x + 5))
            position = (random.randint(min_val, max_val),35)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "musketeer" :
            min_val = int(max(-25, x - 6))
            max_val = int(min(25, x + 6))
            position = (random.randint(min_val, max_val),35)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "minion" :
            min_val = int(max(-25, x - 3.5))
            max_val = int(min(25, x + 3.5))
            position = (random.randint(min_val, max_val),35)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "dragon" :
            min_val = int(max(-25, x - 3.5))
            max_val = int(min(25, x + 3.5))
            position = (random.randint(min_val, max_val),35)
            deploy_list.list_.append((best_troop.name, position))

    else :
        print("entered to attack area 3")
        if enemy_troop.name.lower() in ["archer", "barbarian", "balloon"]:
            return
        #print("entered to attack area 3")
        best_troop = best_troop_respond (arena_data, enemy_troop, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend)

        print("best troop to attack is")
        if best_troop :
            print(best_troop.name)
        if best_troop and best_troop.name.lower() in ["prince", "wizard"] :
            troop, position = best_stratergy_3 (arena_data, best_troop, prince_pairing, wizard_pairing, position_prince_3, position_wizard_3)
            print("pairing troop is")
            print(troop)
            if troop != None and troop.elixir + 5 <= elixir :
                print("elixir available to pair")
                if best_troop.name.lower() == "wizard" :
                    deploy_list.list_.append((best_troop, (0,50)))
                    deploy_list.list_.append((troop.name, position))
                else :
                    deploy_list.list_.append((best_troop, (0,50)))
                    deploy_list.list_.append((troop.name, position))
            else :
                print("elixir not available to pair")
                if best_troop.name.lower() == "wizard" :
                    deploy_list.list_.append((best_troop.name, (0,50)))
                else :
                    deploy_list.list_.append((best_troop.name, (0,50)))
        elif best_troop and best_troop.name.lower() in ["barbarian", "valkyrie"]:
            print("adding troop")
            position = (x,50)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "archer" :
            print("adding troop")
            min_val = int(max(-25, x - 5))
            max_val = int(min(25, x + 5))
            position = (random.randint(min_val, max_val),45)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "musketeer" :
            print("adding troop")
            min_val = int(max(-25, x - 6))
            max_val = int(min(25, x + 6))
            position = (random.randint(min_val, max_val),45)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "minion" :
            print("adding troop")
            min_val = int(max(-25, x - 3.5))
            max_val = int(min(25, x + 3.5))
            position = (random.randint(min_val, max_val),45)
            deploy_list.list_.append((best_troop.name, position))
        elif best_troop and best_troop.name.lower() == "dragon" :
            print("adding troop")
            min_val = int(max(-25, x - 3.5))
            max_val = int(min(25, x + 3.5))
            position = (random.randint(min_val, max_val),45)
            deploy_list.list_.append((best_troop.name, position))


def attack(arena_data, list_attack, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, new_list):
    a = False
    for troop in arena_data["OppTroops"]:  
        if troop.position[1] <= 40:
            a = True
            break

    print("entered attack function")
    print("available troops to attack are")
    troops = get_actually_deployable_troops(arena_data)

    for troop in troops :
        print(troop.name)
    if a == True :
        print("troop in 40 so using different list")
        best_attack_troop = max_score(troops, new_list)
    else :
        print("using original list")
        best_attack_troop = max_score(troops, list_attack)
    print("best troop to attack is")
    print(best_attack_troop.name)
    if not best_attack_troop:
        print("⚠ DEBUG: No best attack troop found!")
        return
    # Handle special troop pairings
    if best_attack_troop.name.lower() in ["prince", "wizard"]:
        troop_type = best_attack_troop.name.lower()
        print("entering best stratergy")
        paired_troop, position = best_stratergy_2(
            arena_data, 
            troop_type,
            prince_pairing, 
            wizard_pairing, 
            position_prince_2, 
            position_wizard_2
        )
        # Ensure we have valid position
        if paired_troop:
            print("deploying pair")
            if best_attack_troop.name.lower() == "wizard" :
                
                deploy_list.list_.append((best_attack_troop.name, (0, 30)))
                print("added wizard to list")
                deploy_list.list_.append((paired_troop.name, (0,31)))
                print("added the paired troop also")
            else :
                deploy_list.list_.append((best_attack_troop.name, (25, 30)))
                print("added prince to list")
                deploy_list.list_.append((paired_troop.name, (25,50)))
                print("added the paired troop also")
    else:
        deploy_list.list_.append((best_attack_troop.name, (0, 20)))

def counter (arena_data, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, position_prince_3, position_wizard_3, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend) :
    if arena_data["OppTroops"] :
        troop_to_counter = arena_data["OppTroops"][-1]
        print("troop to counter is")  
        print(troop_to_counter.name)   
        area = enemy_deployed_troop (arena_data)[1]
        print(area)
        #print("to be countered")
        print("calling troop_and_position")
        troop_and_position (troop_to_counter, area, arena_data, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, position_prince_3, position_wizard_3, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend)

def in_base(arena_data) :
    for troop in arena_data["OppTroops"]:  
        if troop.position[1] <= 40:
            return True


def should_defend(arena_data):
    enemy_in_base = False  # Flag to check if enemy is in base
    my_troops_in_base = False  # Flag to check if we have troops in base

    # Check opponent's troops
    for troop in arena_data["OppTroops"]:
        if troop.position[1] <= 30:
            print("troop in 30")
            return True
    for troop in arena_data["OppTroops"]:
        if troop.position[1] <= 50 and (troop.name.lower() == "giant" or troop.name.lower() == "prince"):
            return True
    for troop in arena_data["OppTroops"]:  
        if troop.position[1] <= 40:  
            enemy_in_base = True
            break  # No need to check further

    # Check our troops
    for troop in arena_data["MyTroops"]:  
        if troop.position[1] <= 40:  
            my_troops_in_base = True
            break  # No need to check further

    # We need to defend if enemy is present and we have no troops there
    if enemy_in_base and not my_troops_in_base:
        print("enemy in 40 but no troop to defend")
        return True

    return False  # No need to defend


def priority_function(arena_data, troop_scores_defend, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, position_prince_3, position_wizard_3, list_attack, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend, new_list):
    elixir = arena_data["MyTower"].total_elixir
    print("entered priority function")
    if should_defend(arena_data):
        defend(arena_data, troop_scores_defend)
    elif elixir > 9 :
        print("no need to defend")
        attack(arena_data, list_attack, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, new_list)
    else :
        return


    
        
def is_new_opp_balloon_in_base(arena_data):
    global team_signal 
    for troop in arena_data["OppTroops"]:
        if troop.name == "Balloon" and troop.position[1] <= 25:
            if troop != team_signal.split(",")[4]:
                team_signal = update_team_signal(team_signal, last_seen_balloon = True)
                return True
    return False

def logic(arena_data) :
    global team_signal
    x = None

    troop_scores_defend = {
        "barbarian": 2,
        "archer": 4,
        "minion": 6,
        "dragon": 7,
        "valkyrie": 3,
        "prince": 1,
        "musketeer": 5,
        "wizard": 8,
    }


    prince_pairing = {
	    Troops.barbarian: 2,
	    Troops.archer: 5,
	    Troops.minion: 6,
	    Troops.dragon: 7,
	    Troops.valkyrie: 4,
	    Troops.prince: 1,
	    Troops.musketeer: 3,
	    Troops.wizard: 8,
	}

    wizard_pairing = {
	    Troops.barbarian: 2,
	    Troops.archer: 4,
	    Troops.minion: 5,
	    Troops.dragon: 7,
	    Troops.valkyrie: 6,
	    Troops.prince: 8,
	    Troops.musketeer: 3,
	    Troops.wizard: 1,
	}

    list_attack = {
	    Troops.barbarian: 4,
	    Troops.archer: 1,
	    Troops.minion: 2,
	    Troops.dragon: 6,
	    Troops.valkyrie: 5,
	    Troops.prince: 8,
	    Troops.musketeer: 3,
	    Troops.wizard: 7,
	}

    new_list = {
	    Troops.barbarian: 2,
	    Troops.archer: 4,
	    Troops.minion: 3,
	    Troops.dragon: 7,
	    Troops.valkyrie: 6,
	    Troops.prince: 1,
	    Troops.musketeer: 5,
	    Troops.wizard: 8,
	}

    giant_defend = {
	    Troops.barbarian: 1,
	    Troops.archer: 2,
	    Troops.minion: 4,
	    Troops.dragon: 6,
	    Troops.valkyrie: 5,
	    Troops.prince: 7,
	    Troops.musketeer: 3,
	    Troops.wizard: 8,
	}

    dragon_defend = {
	    Troops.barbarian: 2,
	    Troops.archer: 5,
	    Troops.minion: 4,
	    Troops.dragon: 7,
	    Troops.valkyrie: 3,
	    Troops.prince: 1,
	    Troops.musketeer: 6,
	    Troops.wizard: 8,
	}

    wizard_defend = {
	    Troops.barbarian: 4,
	    Troops.archer: 1,
	    Troops.minion: 2,
	    Troops.dragon: 6,
	    Troops.valkyrie: 5,
	    Troops.prince: 7,
	    Troops.musketeer: 3,
	    Troops.wizard: 8,
	}

    archer_defend = {
	    Troops.barbarian: 4,
	    Troops.archer: 3,
	    Troops.minion: 2,
	    Troops.dragon: 6,
	    Troops.valkyrie: 1,
	    Troops.prince: 7,
	    Troops.musketeer: 5,
	    Troops.wizard: 8,
	}

    skeleton_defend = {
	    Troops.barbarian: 2,
	    Troops.archer: 4,
	    Troops.minion: 5,
	    Troops.dragon: 7,
	    Troops.valkyrie: 6,
	    Troops.prince: 1,
	    Troops.musketeer: 3,
	    Troops.wizard: 7,
	}

    musketeer_defend = {
	    Troops.barbarian: 4,
	    Troops.archer: 3,
	    Troops.minion: 2,
	    Troops.dragon: 6,
	    Troops.valkyrie: 1,
	    Troops.prince: 7,
	    Troops.musketeer: 5,
	    Troops.wizard: 8,
	}

    valkyrie_defend = {
	    Troops.barbarian: 1,
	    Troops.archer: 4,
	    Troops.minion: 3,
	    Troops.dragon: 6,
	    Troops.valkyrie: 2,
	    Troops.prince: 7,
	    Troops.musketeer: 5,
	    Troops.wizard: 8,
	}

    knight_defend = {
		Troops.barbarian: 1,
	    Troops.archer: 4,
	    Troops.minion: 3,
	    Troops.dragon: 6,
	    Troops.valkyrie: 2,
	    Troops.prince: 7,
	    Troops.musketeer: 5,
	    Troops.wizard: 8,
	}

    prince_defend = {
		Troops.barbarian: 3,
		Troops.archer: 1,
		Troops.minion: 5,
		Troops.dragon: 6,
		Troops.valkyrie: 4,
		Troops.prince: 7,
		Troops.musketeer: 2,
		Troops.wizard: 8,
	}

    barbarian_defend = {
		Troops.barbarian: 2,
	    Troops.archer: 4,
	    Troops.minion: 5,
	    Troops.dragon: 7,
	    Troops.valkyrie: 6,
	    Troops.prince: 1,
	    Troops.musketeer: 3,
	    Troops.wizard: 7,
	}

    minion_defend = {
		Troops.barbarian: 2,
	    Troops.archer: 5,
	    Troops.minion: 4,
	    Troops.dragon: 7,
	    Troops.valkyrie: 3,
	    Troops.prince: 1,
	    Troops.musketeer: 6,
	    Troops.wizard: 8,
	}

    position_prince_2 = {
		Troops.archer: (0,30),
		Troops.barbarian: (0, 32),
		Troops.dragon: (0, 35),
		Troops.valkyrie: (0,35),
		Troops.prince: (0,35),
		Troops.musketeer: (0,30),
		Troops.minion: (0,32),
		Troops.wizard: (0,32)
	}

    position_prince_3 = {
		Troops.archer: (0, 40),
		Troops.barbarian: (0, 42),
		Troops.dragon: (0, 42),
		Troops.valkyrie: (0,45),
		Troops.prince: (0,45),
		Troops.musketeer: (0,40),
		Troops.minion: (0,42),
		Troops.wizard: (0,42)
	}

    position_wizard_2 = {
		Troops.archer: (0, 32),
		Troops.barbarian: (0, 35),
		Troops.dragon: (0, 32),
		Troops.valkyrie: (0,35),
		Troops.prince: (0,37),
		Troops.musketeer: (0,32),
		Troops.minion: (0,32),
		Troops.wizard: (0,35)
	}

    position_wizard_3 = {
		Troops.archer: (0, 42),
		Troops.barbarian: (0, 45),
		Troops.dragon: (0, 42),
		Troops.valkyrie: (0,45),
		Troops.prince: (0,47),
		Troops.musketeer: (0,42),
		Troops.minion: (0,42),
		Troops.wizard: (0,45)
	}

    ballon_defend = {
		Troops.barbarian:3,
		Troops.archer: 5,
		Troops.minion: 4,
		Troops.dragon: 7,
		Troops.valkyrie: 2,
		Troops.prince: 1,
		Troops.musketeer: 6,
		Troops.wizard: 8,
	}
    elixir = arena_data["MyTower"].total_elixir
    priority_function(arena_data, troop_scores_defend, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2, position_prince_3, position_wizard_3, list_attack, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend, new_list)
    '''if elixir >9 :
        print("attacking")
        attack(arena_data, list_attack, prince_pairing, wizard_pairing, position_prince_2, position_wizard_2)
    return'''

    
    
    ''' my_tower = arena_data["MyTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]
    deployable_troops = my_tower.deployable_troops
    elixir = arena_data["MyTower"].total_elixir
    actually_deployable_troops = get_actually_deployable_troops(arena_data)

    if enemy_deployed_troop(arena_data)[0]:
        opp_latest_deployed_troop = arena_data["OppTroops"][-1].name
        team_signal = update_team_signal(team_signal, opp_last_deployed_troop = opp_latest_deployed_troop) 

            
    started_deploying = team_signal.split(",")[0]

    if started_deploying == False :
        if elixir == 10 or opp_troops :
            team_signal = update_team_signal(team_signal, started_deploying=True)
            if elixir == 10 :
                attack (arena_data, list_attack, prince_pairing, giant_pairing, position_prince_2, position_giant_2)
                return
            else :
                counter (arena_data, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3)
                return
        else :
            return
        

    priority_function (arena_data, troop_scores_defend, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3, list_attack)
    return
    '''
