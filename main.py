import random
import math
from teams.helper_function import Troops, Utils

team_name = "404 Not Found"
troops = [
    Troops.wizard, Troops.giant, Troops.archer, Troops.musketeer,
    Troops.dragon, Troops.skeleton, Troops.valkyrie, Troops.prince
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
    deploy_list.list_ = []  # Ensure it's reset
    logic(arena_data)
    
    print(f"✅ DEBUG: Final Deploy List (Before Return): {deploy_list.list_}")
    print(f"✅ DEBUG: Team Signal (Before Return): {team_signal}")
    
    return deploy_list.list_, team_signal





def predict_fight_outcome(arena_data):
    my_dps, my_hp = 0, 0
    enemy_dps, enemy_hp = 0, 0
    my_troops_in_base = []
    opp_troops_in_base = []

    troops_avl = get_actually_deployable_troops(arena_data)

    for troop in arena_data["MyTroops"]:
        if troop.position[1] <= 25:
            my_troops_in_base.append(troop)

    for troop in arena_data["OppTroops"]:
        if troop.position[1] <= 25:
            opp_troops_in_base.append(troop)

    for troop in my_troops_in_base:
        if troop.name.lower() != "giant":
            my_dps += troop.damage / troop.attack_speed
        my_hp += troop.health

    for troop in opp_troops_in_base:
        if troop.name.lower() != "giant":
            enemy_dps += troop.damage / troop.attack_speed
        enemy_hp += troop.health

    my_survival_time = my_hp / enemy_dps if enemy_dps > 0 else float("inf")
    enemy_survival_time = enemy_hp / my_dps if my_dps > 0 else float("inf")

    return "win" if my_survival_time >= enemy_survival_time else "lose"

def max_score(troop_list, scores):
    if not troop_list:
        return None  # If troop_list is empty, return None instead of causing an error
    return max(troop_list, key=lambda troop: scores.get(troop, 0))  # Use .get() to avoid KeyError


def max_score_prince(troop_list, scores):
    filtered_troops = [troop for troop in troop_list if troop != Troops.prince]
    if not filtered_troops:  
        return None  
    return max(filtered_troops, key=lambda troop: scores[troop])

def max_score_giant(troop_list, scores):
    filtered_troops = [troop for troop in troop_list if troop.name.lower() != "giant"]

    if not filtered_troops:  
        return None  

    # Ensure troop objects, not strings
    corrected_scores = {Troops.troops_data[t] if isinstance(t, str) else t: v for t, v in scores.items()}

    return max(filtered_troops, key=lambda troop: corrected_scores[troop])

def get_actually_deployable_troops(arena_data):
    my_tower = arena_data["MyTower"]
    deployable_troops = my_tower.deployable_troops
    available_elixir = my_tower.total_elixir

    actually_deployable = []

    print(f"🔍 DEBUG: Deployable troops: {deployable_troops}, Available Elixir: {available_elixir}")

    for troop_name in deployable_troops:
        troop = Troops.troops_data.get(troop_name)
        if troop:
            print(f"🔍 DEBUG: Checking {troop.name}, Elixir cost: {troop.elixir}") 
            if available_elixir >= troop.elixir:
                actually_deployable.append(troop)
                print(f"✅ DEBUG: Added {troop.name} to deployable list")

    print(f"⚠️ DEBUG: Actually deployable troops: {actually_deployable}")
    return actually_deployable if actually_deployable else []


def get_min_elixir_troop(arena_data):
    actually_deployable_troops = get_actually_deployable_troops(arena_data)
    
    if not actually_deployable_troops:
        return None  

    return min(actually_deployable_troops, key=lambda troop: troop.elixir)

def enemy_deployed_troop (arena_data) :
    if arena_data["OppTroops"] :
        if arena_data["OppTroops"][-1].name == team_signal.split(",")[1] :
            return False, None
        else :
            return True, min (3,math.floor((arena_data["OppTroops"][-1].position[1])/25))
    else :
        return False, None

def pairing_position_prince_2 (best_troop, position_prince_2) :
    return position_prince_2.get(best_troop, None)

def pairing_position_giant_2 (best_troop, position_giant_2) :
    return position_giant_2.get(best_troop, None)

def pairing_position_prince_3 (best_troop, position_prince_3) :
    return position_prince_3.get(best_troop, None)

def pairing_position_giant_3 (best_troop, position_giant_3) :
    return position_giant_3.get(best_troop, None)

def defend (arena_data, troop_scores_defend) :
    actually_deployable_troops = get_actually_deployable_troops(arena_data)
    if actually_deployable_troops :
        best_troop = max(actually_deployable_troops, key=lambda troop: troop_scores_defend[troop])
        deploy_list.list_.append((best_troop, (0,0)))

def best_stratergy_2 (arena_data, troop, prince_pairing, giant_pairing, position_prince_2, position_giant_2,) :
    global team_signal
    elixir = arena_data["MyTower"].total_elixir
    troops = get_actually_deployable_troops (arena_data)
    position = None
    if troop == "prince" :
        best_troop = max_score_prince (troops, prince_pairing)
        elixir_required = 5 + best_troop.elixir
        position = pairing_position_prince_2 (best_troop, position_prince_2)
    else :
        best_troop = max_score_giant (troops, giant_pairing)
        elixir_required = 5+ best_troop.elixir
        position = pairing_position_giant_2 (best_troop, position_giant_2)
    if elixir < elixir_required :
        team_signal = update_team_signal(team_signal, deploy=False)

    return best_troop, position

def best_stratergy_3 (arena_data, troop, prince_pairing, giant_pairing, position_prince_3, position_giant_3) :
    global team_signal
    elixir = arena_data["MyTower"].total_elixir
    troops = get_actually_deployable_troops(arena_data)
    position = None
    if troop == "prince" :
        best_troop = max_score_prince (troops, prince_pairing)
        elixir_required = 5 + best_troop.elixir
        position = pairing_position_prince_3 (best_troop, position_prince_3)
    else :
        best_troop = max_score_giant (troops, giant_pairing)
        elixir_required = 5+ best_troop.elixir
        position = pairing_position_giant_3 (best_troop, position_giant_3)
    if elixir < elixir_required :
        team_signal = update_team_signal(team_signal, deploy=False)

    return best_troop, position

def best_troop_respond (arena_data, enemy_troop, giant_defend, dragon_defend, wizard_defend, archer_defend, skeleton_defend, musketeer_defend, valkyrie_defend, knight_defend, prince_defend, barbarian_defend, minion_defend) :
    actually_deployable_troops = get_actually_deployable_troops(arena_data)
    name = enemy_troop.name

    if name == "giant" :
        best_troop = max_score(actually_deployable_troops, giant_defend)
    elif name == "dragon" :
        best_troop = max_score(actually_deployable_troops, dragon_defend)
        if best_troop.name in ["valkyrie", "prince", "skeleton"]:
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
        if best_troop.name in ["valkyrie", "prince", "skeleton"]:
            return None
    return best_troop

def troop_and_position (enemy_troop, area, arena_data, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3) :

    my_troops = get_actually_deployable_troops(arena_data)
    elixir = arena_data["MyTower"].total_elixir
    x = enemy_troop.position[0]

    if area == 2 :          
        best_troop = best_troop_respond (arena_data, enemy_troop)
        if best_troop and best_troop.name.lower() in ["prince", "giant"]:
            troop, position = best_stratergy_2 (arena_data, troop, prince_pairing, giant_pairing, position_prince_2, position_giant_2)
            if troop == None :
                if best_troop.lower() == "giant" :
                    deploy_list.list_.append((best_troop, (0,25)))
                else :
                    deploy_list.list_.append((best_troop, (0,12)))
                return

            if troop.elixir + 5 <= elixir :
                if best_troop.lower() == "giant" :
                    deploy_list.list_.append((best_troop, (0,25)))
                    deploy_list.list_.append((troop, position))
                else :
                    deploy_list.list_.append((best_troop, (0,12)))
                    deploy_list.list_.append((troop, position))
            else :
                if best_troop.lower() == "giant" :
                    deploy_list.list_.append((best_troop, (0,25)))
                else :
                    deploy_list.list_.append((best_troop, (0,12)))

        elif best_troop and best_troop.name.lower() in ["skeleton", "valkyrie"]:
            position = (x,50)
            deploy_list.list_.append((best_troop, position))
        elif best_troop and best_troop.name.lower() == "archer" :
            min_val = max(-25, x - 5)
            max_val = min(25, x + 5)
            position = (random.randint(min_val, max_val),25)
            deploy_list.list_.append((best_troop, position))
        elif best_troop and best_troop.name.lower() == "musketeer" :
            min_val = max(-25, x - 6)
            max_val = min(25, x + 6)
            position = (random.randint(min_val, max_val),25)
            deploy_list.list_.append((best_troop, position))
        elif best_troop and best_troop.name.lower() == "wizard" :
            min_val = max(-25, x - 5.5)
            max_val = min(25, x + 5.5)
            position = (random.randint(min_val, max_val),25)
            deploy_list.list_.append((best_troop, position))
        elif best_troop and best_troop.name.lower() == "dragon" :
            min_val = max(-25, x - 3.5)
            max_val = min(25, x + 3.5)
            position = (random.randint(min_val, max_val),25)
            deploy_list.list_.append((best_troop, position))

    else :      
        if enemy_troop.name.lower() in ["musketeer", "valkyrie", "prince"]:
            best_troop = best_troop_respond (arena_data, enemy_troop)
        if best_troop and best_troop.lower() in ["prince", "giant"] :
            troop, position = best_stratergy_3 (arena_data, troop, prince_pairing, giant_pairing, position_prince_3, position_giant_3)
            if troop.elixir + 5 <= elixir :
                if best_troop.name.lower() == "giant" :
                    deploy_list.list_.append((best_troop, (0,50)))
                    deploy_list.list_.append((troop, position))
                else :
                    deploy_list.list_.append((best_troop, (0,45)))
                    deploy_list.list_.append((troop, position))
            else :
                if best_troop.name.lower() == "giant" :
                    deploy_list.list_.append((best_troop, (0,50)))
                else :
                    deploy_list.list_.append((best_troop, (0,45)))

def attack(arena_data, list_attack, prince_pairing, giant_pairing, position_prince_2, position_giant_2):
    troops = get_actually_deployable_troops(arena_data)

    print(f"🔍 DEBUG: Troops available for attack: {[t.name for t in troops]}")

    if not troops:
        print("⚠️ DEBUG: No troops available for attack!")
        return

    for troop in troops:  # Loop through multiple troops
        if troop.name.lower() in ["prince", "giant"]:
            Troop, position = best_stratergy_2(arena_data, troop, prince_pairing, giant_pairing, position_prince_2, position_giant_2)
            if Troop is None:
                print(f"⚠️ DEBUG: No valid pairing strategy found for {troop.name}")
                continue

            print(f"✅ DEBUG: Deploying {troop.name} at (0,0) and {Troop.name} at {position}")
            deploy_list.list_.append((troop, (0, 0)))
            deploy_list.list_.append((Troop, position))
        else:
            best_troop = max_score(troops, list_attack)
            if best_troop:
                print(f"✅ DEBUG: Deploying best attack troop {best_troop.name} at (0,0)")
                deploy_list.list_.append((best_troop, (0, 0)))
            else:
                print("⚠️ DEBUG: No best troop found for attack!")

def counter (arena_data, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3) :
    troop_to_counter = arena_data["OppTroops"][-1]     
    area = enemy_deployed_troop (arena_data)[1]
    troop_and_position (troop_to_counter, area, arena_data, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3)

def priority_function(arena_data, troop_scores_defend, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3, list_attack):
    elixir = arena_data["MyTower"].total_elixir
    actually_deployable_troops = get_actually_deployable_troops(arena_data)

    print(f"🔍 DEBUG: Checking priority function, Available Elixir: {elixir}")

    if predict_fight_outcome(arena_data) == "lose":
        print("⚠️ DEBUG: Predicted fight outcome is lose. Deploying defensive troops.")
        defend(arena_data, troop_scores_defend)
    else:
        if elixir == 10:
            print("🔍 DEBUG: Elixir is maxed (10). Attacking!")
            attack(arena_data, list_attack, prince_pairing, giant_pairing, position_prince_2, position_giant_2)

        if enemy_deployed_troop(arena_data)[0]:
            print("🔍 DEBUG: Enemy has deployed a troop. Countering!")
            counter(arena_data, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3)
        else:
            print("⚠️ DEBUG: No enemy troops detected. Skipping counter.")
        
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
	    Troops.giant: 2,
	    Troops.archer: 3,
	    Troops.skeleton: 4,
	    Troops.dragon: 7,
	    Troops.valkyrie: 5,
	    Troops.prince: 1,
	    Troops.musketeer: 6,
	    Troops.wizard: 8,
	}

    prince_pairing = {
	    Troops.giant: 1,
	    Troops.archer: 4,
	    Troops.skeleton: 2,
	    Troops.dragon: 7,
	    Troops.valkyrie: 9,
	    Troops.prince: 1,
	    Troops.musketeer: 3,
	    Troops.wizard: 8,
	}

    giant_pairing = {
	    Troops.giant: 1,
	    Troops.archer: 5,
	    Troops.skeleton: 2,
	    Troops.dragon: 7,
	    Troops.valkyrie: 6,
	    Troops.prince: 1,
	    Troops.musketeer: 4,
	    Troops.wizard: 8,
	}

    list_attack = {
	    Troops.giant: 8,
	    Troops.archer: 4,
	    Troops.skeleton: 2,
	    Troops.dragon: 5,
	    Troops.valkyrie: 3,
	    Troops.prince: 9,
	    Troops.musketeer: 6,
	    Troops.wizard: 7,
	}

    giant_defend = {
	    Troops.giant: 1,
	    Troops.archer: 3,
	    Troops.skeleton: 8,
	    Troops.dragon: 2,
	    Troops.valkyrie: 4,
	    Troops.prince: 7,
	    Troops.musketeer: 5,
	    Troops.wizard: 6,
	}

    dragon_defend = {
	    Troops.giant: 2,
	    Troops.archer: 5,
	    Troops.skeleton: 1,
	    Troops.dragon: 6,
	    Troops.valkyrie: 4,
	    Troops.prince: 3,
	    Troops.musketeer: 8,
	    Troops.wizard: 7,
	}

    wizard_defend = {
	    Troops.giant: 2,
	    Troops.archer: 3,
	    Troops.skeleton: 1,
	    Troops.dragon: 5,
	    Troops.valkyrie: 7,
	    Troops.prince: 8,
	    Troops.musketeer: 6,
	    Troops.wizard: 4,
	}

    archer_defend = {
	    Troops.giant: 1,
	    Troops.archer: 5,
	    Troops.skeleton: 2,
	    Troops.dragon: 6,
	    Troops.valkyrie: 8,
	    Troops.prince: 4,
	    Troops.musketeer: 7,
	    Troops.wizard: 3,
	}

    skeleton_defend = {
	    Troops.giant: 2,
	    Troops.archer: 5,
	    Troops.skeleton: 4,
	    Troops.dragon: 8,
	    Troops.valkyrie: 6,
	    Troops.prince: 1,
	    Troops.musketeer: 3,
	    Troops.wizard: 7,
	}

    musketeer_defend = {
	    Troops.giant: 1,
	    Troops.archer: 8,
	    Troops.skeleton: 3,
	    Troops.dragon: 4,
	    Troops.valkyrie: 5,
	    Troops.prince: 7,
	    Troops.musketeer: 6,
	    Troops.wizard: 2,
	}

    valkyrie_defend = {
	    Troops.giant: 2,
	    Troops.archer: 5,
	    Troops.skeleton: 1,
	    Troops.dragon: 4,
	    Troops.valkyrie: 6,
	    Troops.prince: 8,
	    Troops.musketeer: 7,
	    Troops.wizard: 3,
	}

    knight_defend = {
		Troops.giant: 2,
		Troops.archer: 6,
		Troops.skeleton: 1,
		Troops.dragon: 5,
		Troops.valkyrie: 4,
		Troops.prince: 8,
		Troops.musketeer: 7,
		Troops.wizard: 3,
	}

    prince_defend = {
		Troops.giant: 2,
		Troops.archer: 6,
		Troops.skeleton: 8,
		Troops.dragon: 3,
		Troops.valkyrie: 6,
		Troops.prince: 7,
		Troops.musketeer: 5,
		Troops.wizard: 4,
	}

    barbarian_defend = {
		Troops.giant: 1,
		Troops.archer: 3,
		Troops.skeleton: 2,
		Troops.dragon: 8,
		Troops.valkyrie: 7,
		Troops.prince: 4,
		Troops.musketeer: 5,
		Troops.wizard: 6,
	}

    minion_defend = {
		Troops.giant: 4,
		Troops.archer: 8,
		Troops.skeleton: 1,
		Troops.dragon: 7,
		Troops.valkyrie: 2,
		Troops.prince: 3,
		Troops.musketeer: 5,
		Troops.wizard: 6,
	}

    position_prince_2 = {
		Troops.archer: (0, 11),
		Troops.giant: (0, 45),
		Troops.dragon: (0, 11),
		Troops.valkyrie: (0,15),
		Troops.prince: (0,0),
		Troops.musketeer: (0,11),
		Troops.skeleton: (0,25),
		Troops.wizard: (0,11)
	}

    position_prince_3 = {
		Troops.archer: (0, 40),
		Troops.giant: (0, 50),
		Troops.dragon: (0, 40),
		Troops.valkyrie: (0,50),
		Troops.prince: (0,0),
		Troops.musketeer: (0,40),
		Troops.skeleton: (0,50),
		Troops.wizard: (0,40)
	}

    position_giant_2 = {
		Troops.archer: (0, 15),
		Troops.giant: (0, 0),
		Troops.dragon: (0, 15),
		Troops.valkyrie: (0,20),
		Troops.prince: (0,0),
		Troops.musketeer: (0,15),
		Troops.skeleton: (0,25),
		Troops.wizard: (0,15)
	}

    position_giant_3 = {
		Troops.archer: (0, 40),
		Troops.giant: (0, 0),
		Troops.dragon: (0, 40),
		Troops.valkyrie: (0,45),
		Troops.prince: (0,40),
		Troops.musketeer: (0,40),
		Troops.skeleton: (0,50),
		Troops.wizard: (0,40)
	}

    ballon_defend = {
		Troops.giant: 4,
		Troops.archer: 6,
		Troops.skeleton: 1,
		Troops.dragon: 5,
		Troops.valkyrie: 2,
		Troops.prince: 3,
		Troops.musketeer: 7,
		Troops.wizard: 8,
	}

    
    my_tower = arena_data["MyTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]
    deployable_troops = my_tower.deployable_troops
    elixir = arena_data["MyTower"].total_elixir
    actually_deployable_troops = get_actually_deployable_troops(arena_data)

    
            
    started_deploying = team_signal.split(",")[0]

    if started_deploying == False :
        if elixir == 10 or opp_troops :
            team_signal = update_team_signal(team_signal, started_deploying=True)
            if elixir == 10 :
                attack (arena_data, list_attack, prince_pairing, giant_pairing, position_prince_2, position_giant_2)
                return
        else :
            return
        
    if enemy_deployed_troop(arena_data)[0]:
        opp_latest_deployed_troop = arena_data["OppTroops"][-1].name
        team_signal = update_team_signal(team_signal, opp_last_deployed_troop = opp_latest_deployed_troop) 

    priority_function (arena_data, troop_scores_defend, prince_pairing, giant_pairing, position_prince_2, position_giant_2, position_prince_3, position_giant_3, list_attack)
    return
