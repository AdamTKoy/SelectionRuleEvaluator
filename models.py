# Function to simplify W/ & N/ model statements into single net-positive W/ statement

import functions

# Prompt user for string input
# TODO: Loop in case user has additional models to evaluate
print("This function will simplify W/ & N/ models into a single combined W/ statement.")
W = input("W/: ")
N = input("N/: ")

np_list, np_string = functions.model_rewrite(W, N)

print("Final net positive (list): ", np_list)
print("Final net positive (string): ", np_string)