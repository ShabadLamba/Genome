import re

def fetchPossibleCombinations(text):
    combinations = []
    for i in "atgc":
        for j in "atgc":
            for k in range(0,len(text)):
                for l in range(0,len(text)):
                    temp = list(text)
                    temp[k] = i
                    if l != k:
                        temp[l] = j
                        combinations.append(''.join(temp))
    combinations = list(set(combinations))
    return combinations


def featureSearch(dna):
    windowNumber = 0
    resultDict = {}
    for i in range(40,len(dna)): 
        infoDict = {"tataBox":[0],"ttgacBox":[0],"atgBox":[0]}
        window = dna[i:i+3]
#         for sequence3 in fetchPossibleCombinations("atg"):
        for sequence3 in ["atg","gtg","ttg"]:
            if  window == sequence3:
                infoDict["atgBox"][0] = i+3
                # print(i)
                for sequence in fetchPossibleCombinations("tataa"):
                    if  dna[i-15:i-10] == sequence :
                        infoDict["tataBox"][0] += i-15
                        # print(i)
                        for sequence2 in fetchPossibleCombinations("ttgac"):
                            if dna[i-40:i-35] == sequence2:
                                infoDict["ttgacBox"][0] += i-40
                                # print(i)
        key = "set" + " " + str(windowNumber)
        resultDict[key] = infoDict
        windowNumber += 1
    return resultDict

def deterministicSearch(listOfFeatures):
    output = [listOfFeatures[sets] for sets in listOfFeatures if listOfFeatures[sets]["atgBox"][0] > 0 and listOfFeatures[sets]["tataBox"][0] > 0 and listOfFeatures[sets]["ttgacBox"][0] > 0]
    return output

def fetchingTheSequences(dna,listOfLocationsOfFeatures):
    sequenceList = []
    for sequence in listOfLocationsOfFeatures:
#         print sequence["atgBox"][0]-sequence["ttgacBox"][0]
        sequenceList.append({"promoter":dna[sequence["ttgacBox"][0]:sequence["atgBox"][0]],"features":sequence})
    return sequenceList