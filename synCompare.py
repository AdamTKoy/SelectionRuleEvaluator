# Function to evaluate GROUPINGS of synonyms and feature codes

import functions

print("This function will compare two groupings of synonyms/features and return only those features that exist in both AND are compatible with the specified models in MMAC.")
s1 = input("Grouping 1: ")
s2 = input("Grouping 2: ")
M = input("Models: ")

result, removed = functions.syn_compare(s1, s2, M)

print("Features in both groupings and compatible with models: ", result)
print("Removed features: ", removed)