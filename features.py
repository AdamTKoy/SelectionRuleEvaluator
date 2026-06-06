# Function to simplify W/ & N/ feature statements into single net-positive W/ statement
import functions

# Prompt for input (string)
# W: gross positive tokens (feature codes or feature synonyms)
# N: negative tokesn (feature codes or feature synonyms)
# M: model tokens (model codes or model synonyms)
print("This function will simplify W/ & N/ features into a single combined W/ statement.")
W = input("W/: ")
N = input("N/: ")
M = input("Models: ")

np_list, np_string = functions.feature_rewrite(W, N, M)

# (For my use, I only need the string)
print("Final net positive: ", np_string)
