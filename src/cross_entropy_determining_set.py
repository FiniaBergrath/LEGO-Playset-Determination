import numpy as np
from database_connection_playground import db_connection

#Bausteinverteilung 
random_bricks = [("3004", 15), ("3001",1), ("3023",7), ("3003",16), ("3005",3), ("6141",36)]
random_brick_counts = [1, 5, 8, 2, 6, 2]

#Sets auswählen und laden
sets = [("abc", "7891-1") , ("efg","6020-1")]

def cross_entropy(detected_bricks, detected_counts, detected_total, set_bricks, set_counts, set_total, direct_matching = True):
    #Wahrscheinlichkeiten berechnen
    detected_probs = detected_counts / detected_total
    set_probs = set_counts / set_total

    # Wahrscheinlichkeiten den erkannten Steinen zuordnen - um log(0) zu vermeiden, werden nicht erkannte Steine mit einer sehr kleinen Wahrscheinlichkeit belegt
    set_probs_for_detection = np.full_like(detected_probs,fill_value=1e-5, dtype=float)  
   
    for i in range(len(detected_bricks)):
        
        if direct_matching:
            index = np.where((set_bricks[:,0] == detected_bricks[i,0])) #Prüft zuerst ob stein_id und im Anschluss für jeden Index ob dort auch die color_id übereinstimmt 
        else:
            index = np.where(set_bricks[:] == detected_bricks[i]) #Teilmatches bei denen Steinid oder Colorid übereinstimmt werden mitgezählt
    
        for idx in index[0]:
            print(set_bricks[idx])
            print(detected_bricks[i])

            color_is_equal = (set_bricks[idx,1] == detected_bricks[i,1])

            if not direct_matching or color_is_equal: #Fall 1: Teilmatching; Fall 2: Direktes Matching also Part_id und Color_id stimmen überein

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


def determine_matching_of_sets(detected_bricks, detected_counts, sets, db):
    
    detected_total = np.sum(detected_counts)
    cross_entropy_results = {}
    print("bricks:",detected_bricks)
    print("counts:",detected_counts)
    print("sets",sets)


    for set in sets:
        name, set_id = set
        print("Set_id:", set_id)
        set_total, set_bricks, set_counts = db.get_set_elements(set_id)

        if(set_total == None):
             cross_entropy_results[set_id] = 1000
        
        else:
            set_bricks = np.asarray(set_bricks, dtype=object)
            set_counts = np.asarray(set_counts)
            detected_bricks = np.asarray(detected_bricks, dtype=object)
            detected_counts = np.asarray(detected_counts)
            '''print("detected_bricks", detected_bricks)
            print(detected_counts)
            print(set_bricks)
            print(set_counts)
            print(set_bricks)'''

            #Direktes Matching soll exakte übereinstimmungen erkennen 
            direct_ce = cross_entropy(detected_bricks, detected_counts, detected_total, set_bricks, set_counts, set_total)
            print("direktes Matching:", direct_ce)
            #Indirektes Matching toleriert zusätzlich die Übereinstimmung von Farben und Steinform unabhängig voneinander
            # -> Damit soll auch bei einer kleinen Menge erkannter Steine mehr Aussagekraft gewonnen werden
            indirect_ce = cross_entropy(detected_bricks, detected_counts, detected_total, set_bricks, set_counts, set_total, direct_matching=False)
            print("indirektes Matching", indirect_ce)
            #Da das direkte Matching konkreter als indirektes Matching ist und indirektes Matching die direkten Matches zusätzlich beinhaltet gewichte ich direktes Matching stärker
            ce = 0.7 * direct_ce + indirect_ce * 0.3
            print("ce", ce)

            cross_entropy_results[set_id] = ce

    #return sorted(cross_entropy_results, key=sorting_key) #Sortiert die Liste in aufsteigender Reihenfolge, sodass min -> list[0]
    return cross_entropy_results



#db = db_connection()
#print(determine_matching_of_sets(random_bricks, random_brick_counts, sets, db))