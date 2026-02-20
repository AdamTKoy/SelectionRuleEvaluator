# Function to simplify W/ & N/ feature statements into single net-positive W/ statement

import functions

# Single prompt
# TODO: loop so that user can keep going if they have additional features to evaluate
print("This function will simplify W/ & N/ features into a single combined W/ statement.")
W = input("W/: ")
N = input("N/: ")
M = input("Models: ")

np_list, np_string = functions.feature_rewrite(W, N, M)

# (For my use, I only need the string)
print("Final net positive: ", np_string)