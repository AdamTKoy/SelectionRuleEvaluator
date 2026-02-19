import pandas as pd
pd.options.mode.chained_assignment = None # this will suppress the warning about modifying a copied slice of a df
import time

# global variables for excel files
actv_ftrs = 'Data/active_features_01.23.26.csv'
actv_fgs = 'Data/active_FGs_01.23.26.csv'
actv_mdls = 'Data/active_models_01.23.26.csv'
actv_mmac = 'Data/all_active_mmac_01.23.26.csv'
ftr_syn_table = 'Data/feature_synonym_table_01.23.26.csv'
mdl_syn_table = 'Data/model_synonym_table_01.23.26.csv'

# Function to Validate Input
def validate(input_set, unique_members, unique_synonyms=None):
    for x in input_set:
        if x[0:2] == "M-" or x[0:2] == "F-":  # SYNONYM
            if x not in unique_synonyms:
                print("Error: Invalid synonym: ", x)
                return 0
        elif "*" in x:  # ignore obsoletes here, then remove later
            continue
        elif (len(x) == 7): # FEATURE CODE
            if x not in unique_members:
                print("Error: Invalid model/feature: ", x)
                return 0
        elif len(x) == 4:   # FEATURE GROUP
            if len(input_set) != 1:
                print("Error: FG not allowed with additional arguments: ", input_set)
                return 0
            if x not in unique_members:
                print("Error: Invalid feature group: ", x)
                return 0
        else:
            print("Error: Invalid input: ", x)
            return 0
    return 1

# Function to convert list of strings (which may incl. synonyms) to set of distinct individual models/features
def build_set(inputs, df):
    result = set()
    for item in inputs:
        if item[0:2] == "M-" or item[0:2] == "F-":
            individuals = df.loc[df['synonym'] == item, 'members']
            to_add = [x for sublist in individuals for x in sublist]
            result.update(to_add)
        elif "*" in item:   # skip over obsoletes
            continue
        else:   # at this point, individual elements should already be validated
            result.add(item)
    return result

# Function to rewrite W/ & N/ to net positive W/ (Models)
def model_rewrite(with_string, not_with_string):
    with_string = with_string.upper()
    with_items = [item.strip() for item in with_string.split(',')]

    if not_with_string == "":
        not_with_items = []
    else:
        not_with_string = not_with_string.upper()
        not_with_items = [item.strip() for item in not_with_string.split(',')]

    mdf = pd.read_csv(mdl_syn_table, dtype=str)
    am = pd.read_csv(actv_mdls, dtype=str)
    unique_mdl_syns = set(mdf['synonym'])
    unique_mdls = set(am['modl_no'])

    validation_set = set(with_items + not_with_items)
    if not validate(validation_set, unique_mdls, unique_mdl_syns):
        return ['Input failed validation'], 'Input failed validation'

    # splits string into list of models that are members of respective synonyms
    mdf['members'] = mdf['members'].apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    # SORT df by list length (decreasing)
    # so that when rebuilding models into synonyms, we favor synonyms that provide the most coverage
    mdf = mdf.sort_values(by='members', key=lambda x: x.apply(len), ascending=False)

    if not_with_items != []:
        negative = build_set(not_with_items, mdf)
        gross_positive = build_set(with_items, mdf)
        net_positive = gross_positive.difference(negative)
    else:
        net_positive = build_set(with_items, mdf)

    # Convert back to synonyms when possible
    # - go through each row of model dataframe
    # - if ALL members exist in net_postive set, add synonym to set and remove individual members
    for row in mdf.itertuples():
        current = set(mdf.loc[row.Index, 'members'])
        if current.issubset(net_positive):
            net_positive.add(mdf.loc[row.Index, 'synonym'])
            net_positive = net_positive - current
    net_pos_list = list(net_positive)
    sorted_net_pos = sorted(net_pos_list)
    result_string = ", ".join(sorted_net_pos)
    return sorted_net_pos, result_string

# TODO: implement other input validations?
# TODO: modify so that input takes in an entire selection and has to parse out the W/, N/, models
    # and matches features/synonyms across W/ & N/ that are in same FG
def feature_rewrite(with_features, not_with_features, model_string):
    # TIME functions used only for testing function efficiency
    #print("starting clock inside function...")
    #func_time = time.time()

    # allows simplification of W/ without needing to input a N/
    if not_with_features != "":
        not_with_features = not_with_features.upper()
        not_with_items = [item.strip() for item in not_with_features.split(',')]
    else:
        not_with_items = []

    # inputs are not case sensitive
    model_string = model_string.upper()
    with_features = with_features.upper()

    model_items = [item.strip() for item in model_string.split(',')]

    # import feature and model data
    fdf = pd.read_csv(ftr_syn_table, dtype=str)
    mdf = pd.read_csv(mdl_syn_table, dtype=str)
    af = pd.read_csv(actv_ftrs, dtype=str)
    am = pd.read_csv(actv_mdls, dtype=str)

    # check all model inputs against active models
    mdl_validation_set = set(model_items)
    unique_mdls = set(am['modl_no'])
    unique_mdl_syns = set(mdf['synonym'])
    if not validate(mdl_validation_set, unique_mdls, unique_mdl_syns):
        return ['Model input failed validation'], 'Model input failed validation'
    
    mmac_df = pd.read_csv(actv_mmac, dtype=str)
    # split synonym member single-strings into lists of individual features
    fdf['members'] = fdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])
    mdf['members'] = mdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    models = build_set(model_items, mdf)
    # if user inputs a single FG (and need to only allow one)
    # check it against a validation set of all active FGs
    # if it passes, then pull all compatible features 
    if len(with_features) == 4:
        # print("Input identified as FG ", with_features)
        fg_validation_set = set([with_features])

        # print("fg_validation_set: ", fg_validation_set)

        afg = pd.read_csv(actv_fgs, dtype=str)
        all_fgs = set(afg['fetr_grp_no'])

        if not validate(fg_validation_set, all_fgs):
            return ['FG input failed validation'], 'FG input failed validation'
        else:
            all_compat_in_fg = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == with_features)]
            # populate with_items with a list of strings for all compatible features
            with_items = all_compat_in_fg['feature'].astype(str).tolist()
            # print("with_items after attempted pull of all compatible in FG: ", with_items)
    else:
        with_items = [item.strip() for item in with_features.split(',')]

    # check all feature inputs against active features/synonyms
    # Note: a synonym with an inactive/obsolete member will be allowed (and ignored during analysis)
        # but if an inactive/obsolete feature is entered, it will cause an (expected) error
        # -- or should we just keep a separate set/list with invalid inputs?
    ftr_validation_set = set(with_items + not_with_items)
    unique_ftrs = set(af['feature'])
    unique_ftr_syns = set(fdf['synonym'])
    if not validate(ftr_validation_set, unique_ftrs, unique_ftr_syns):
        return ['Feature input failed validation'], 'Feature input failed validation'
    
    # go through all synonym members and remove features not present in all active features
    fdf['members'] = fdf['members'].apply(lambda item_list: [item for item in item_list if item in unique_ftrs])

    # subtract N/ from W/ to create net_positive set
    gross_positive = build_set(with_items, fdf)
    negative = build_set(not_with_items, fdf)
    net_positive = gross_positive.difference(negative)

    # print("after creating initial net_positive: %s" % (time.time() - func_time))

    # check if there's nothing to analyze/return
    if not net_positive:
        # print("No remaining features identified.")
        return ['No remaining features identified'], 'No remaining features identified'

    # check that all features belong to same FG
    fgs = set()
    fg_filter = af[af['feature'].isin(net_positive)]
    fgs.update(fg_filter['fg'].tolist())

    if len(fgs) > 1:
        #print("Error: Multiple feature groups detected.")
        return ['Error: Multiple feature groups detected'], 'Error: Multiple feature groups detected'
    elif len(fgs) < 1:
        #print("Error: No matching feature group identified for input.")
        return ['Error: No matching feature group identified for input.'], 'Error: No matching feature group identified for input.'

    fg = fgs.pop()

    # only grab features that match models and feature group
    filtered = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == fg)]

    # print("after creating filtered: %s" % (time.time() - func_time))
    compatible = set(filtered['feature'])

    # Need to remove any features in net_positive that are NOT in MMAC but may still be active/non-obsolete features
    # example: 0014BAB has no MMAC records but is an active, non-obsolete feature in the system (as of 10/28/2025)
    compat_not_net_pos = compatible.difference(net_positive) # active/compatible features not allowed in W/
    net_positive = net_positive.intersection(compatible) # removes features with no MMAC

    # print("FG features compatible w/ models but not allowed: ", compat_not_net_pos)
    # print("net positive intersection with compatible: ", net_positive)

    # check if there's nothing to analyze/return after removing excluded features
    if not net_positive:
        # print("No remaining features identified.")
        return ['No remaining features identified'], 'No remaining features identified'

    # we only want synonyms that have at least 1 member from net_positive
    # and do NOT contain any other FG features compatible with models but restricted by inputs
    mask1 = fdf['members'].apply(lambda x: set(x).isdisjoint(compat_not_net_pos))
    mask2 = fdf['members'].apply(lambda x: set(x).intersection(net_positive))
    filtered_df = fdf[mask1 & mask2]

    # it's possible at this point that NO synonyms will work
    if filtered_df.empty:
        #print("No compatible synonyms. Returning remaining features.")
        net_pos_list = list(net_positive)
        sorted_net_pos = sorted(net_pos_list)
        result_string = ", ".join(sorted_net_pos)
        return sorted_net_pos, result_string

    # print("filtered_df: ", filtered_df)

    # adding calculation for # of feature overlap with net_positive (for ranking)
    filtered_df['values'] = filtered_df.apply(lambda row: len(set(row['members']).intersection(net_positive)), axis=1)
    filtered_df = filtered_df.sort_values(by='values', ascending=False)

    # At this point can export filtered_df to get all synonym candidates

    # at this point we could save/export all matching synonyms with ranking to excel/csv
        # TODO: 
            # make a copy of filtered_df
            # separate each synonym/members line into 2: 1 with net_positive overlap, 1 with incompatible
            # Add in created and last_modified dates
                # do we want to throw away older synonyms that duplicate coverage?
                # and how would we handle tie-breaks? (prob leave both in?)
                    # what if: created in same but last_mod is different? (does last_mod matter enough?)
            # and a bonus would be to figure out the most EFFICIENT combination of synonyms based on this data
                # efficiency based on:
                    # - minimal number of synonyms
                    # - minimal overlap
    # filtered_df_copy.to_excel("output.xlsx", sheet_name='Sheet1', index=False)

    # print("filtered_df: ", filtered_df)

    for row in filtered_df.itertuples():
        current = set(filtered_df.loc[row.Index, 'members'])
        # since we are modifying net_positive, have to keep checking if this synonym's members intersect with net_positive
        # if so, add synonym to net_positive and remove individual members
        # TODO: if multiple synonyms provide same coverage, give priority to NEWER synonym
            # > should it be based on created date or last modified date?
            # > in tie situations, should we provide all options (as separated output) so user can manually decide?
        if current.intersection(net_positive):
            syn_to_add = filtered_df.loc[row.Index, 'synonym']
            net_positive.add(syn_to_add)
            net_positive = net_positive.difference(current)

    # print("after converting back into synonyms: %s" % (time.time() - func_time))

    # this will convert the result set into a list and sort it,
    net_pos_list = list(net_positive)
    sorted_net_pos = sorted(net_pos_list)

    # but should we instead send back a single, comma-delimited string so that the result is ready for copy-paste?
    result_string = ", ".join(sorted_net_pos)

    #print("Query took %s seconds to run. Sending back final result..." % (time.time() - func_time))

    return sorted_net_pos, result_string

# Function that will determine feature overlap between two GROUPINGS of synonyms/features
# TODO: specify which features didn't have MMAC and which just didn't exist in both groupings
def syn_compare(syn1, syn2, models_input):
    syn1 = syn1.upper()
    syn2 = syn2.upper()
    syn1_items = [item.strip() for item in syn1.split(',')]
    syn2_items = [item.strip() for item in syn2.split(',')]

    models_input = models_input.upper()
    model_items = [item.strip() for item in models_input.split(',')]

    validation_set = set(syn1_items + syn2_items)
    mdl_validation_set = set(model_items)

    fdf = pd.read_csv(ftr_syn_table, dtype=str)
    af = pd.read_csv(actv_ftrs, dtype=str)
    mdf = pd.read_csv(mdl_syn_table, dtype=str)
    am = pd.read_csv(actv_mdls, dtype=str)

    unique_mdls = set(am['modl_no'])
    unique_mdl_syns = set(mdf['synonym'])
    if not validate(mdl_validation_set, unique_mdls, unique_mdl_syns):
        return ['Model input failed validation'], ['Model input failed validation']

    unique_ftrs = set(af['feature'])
    unique_ftr_syns = set(fdf['synonym'])
    if not validate(validation_set, unique_ftrs, unique_ftr_syns):
        return ['Feature input failed validation'], ['Feature input failed validation']

    fdf['members'] = fdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])
    mdf['members'] = mdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    syn1_set = build_set(syn1_items, fdf)
    syn2_set = build_set(syn2_items, fdf)
    in_both = syn1_set.intersection(syn2_set)
    
    removed = syn1_set.symmetric_difference(syn2_set)

    models = build_set(model_items, mdf)

    fgs = set()
    fg_filter = af[af['feature'].isin(in_both)]

    if fg_filter.empty:
        print("No overlapping features detected. Group 1 and Group 2 are distinct.")
        return [],[]

    fgs.update(fg_filter['fg'].tolist())

    # print("fgs: ", fgs)

    if len(fgs) != 1:
        # print("Error: Multiple feature groups detected: ", fgs)
        return ['Multiple FGs detected.'], ['Multiple FGs detected.']

    fg = fgs.pop()
    
    mmac_df = pd.read_csv(actv_mmac, dtype=str)

    filtered = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == fg)]
    compatible = set(filtered['feature'])

    # remove anything from in_both that isn't also in compatible (has no MMAC for models)
    in_both = in_both.intersection(compatible)

    result_list = list(in_both)
    sorted_result = sorted(result_list)
    result_string = ", ".join(sorted_result)

    # print("sorted_result: ", result_string)

    removed_list = list(removed)
    sorted_removed = sorted(removed_list)
    removed_string = ", ".join(sorted_removed)

    # print("sorted_removed: ", removed_string)

    return result_string, removed_string