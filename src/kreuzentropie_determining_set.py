import numpy as np
import database_connection_playground as db

#Bausteinverteilung 
random_bricks = [("3004", 15), ("3001",1), ("3023",7), ("3003",16), ("3005",3), ("6141",36)]
random_brick_counts = [1, 5, 8, 2, 6, 2]

#Sets auswählen und laden
sets = ["7891-1", "6020-1"]

db.connect_to_rebrick()

def cross_entropy(detected_bricks, detected_counts, detected_total, set_bricks, set_counts, set_total):
    #Wahrscheinlichkeiten berechnen
    detected_probs = detected_counts / detected_total
    set_probs = set_counts / set_total

    # Wahrscheinlichkeiten den erkannten Steinen zuordnen - um log(0) zu vermeiden, werden nicht erkannte Steine mit einer sehr kleinen Wahrscheinlichkeit belegt
    set_probs_for_detection = np.full_like(detected_probs,fill_value=1e-5, dtype=float)  
   
    for i in range(len(detected_bricks)):
           # index = np.where(set_bricks == detected_bricks[i]) -> Teilmatch 
            index = np.where((set_bricks[:,0] == detected_bricks[i][0]))
        
            for idx in index[0]:
                print(set_bricks[idx])
                print(detected_bricks[i])
                print(set_bricks[idx][1] == detected_bricks[i][1])
                if(set_bricks[idx][1] == detected_bricks[i][1]):

                    print("brick",detected_bricks[i])
                    print("equals brick",set_bricks[idx])
                    set_probs_for_detection[i] = set_probs[idx]

    print(set_probs_for_detection)
            

    #Kreuzentropie bilden 
    cross_entropy = -np.sum(detected_probs * np.log(set_probs_for_detection))
                                                                                                
    return cross_entropy

def sorting_key(cross_entropy_result):
    set_id, ce = cross_entropy_result
    return ce


def determine_matching_of_sets(detected_bricks, detected_counts, sets):
    
    db.connect_to_rebrick()
    detected_total = np.sum(detected_counts)
    cross_entropy_results = []

    for set_id in sets:
        set_total, set_bricks, set_counts = db.get_set_elements(set_id)
        set_bricks = np.asarray(set_bricks, dtype=object)
        set_counts = np.asarray(set_counts)
        detected_bricks = np.asarray(detected_bricks, dtype=object)
        detected_counts = np.asarray(detected_counts)
        print(detected_bricks)
        print(detected_counts)
        print(set_bricks)
        print(set_counts)
        print(set_bricks)
       
        ce = cross_entropy(detected_bricks, detected_counts, detected_total, set_bricks, set_counts, set_total)

        cross_entropy_results.append((set_id, ce))

    return sorted(cross_entropy_results, key=sorting_key) #Sortiert die Liste in aufsteigender Reihenfolge, sodass min -> list[0]




print(determine_matching_of_sets(random_bricks, random_brick_counts, sets))