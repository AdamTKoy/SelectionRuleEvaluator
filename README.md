# Selection Rule Evaluator

This tool accepts either features (such as fuel tanks, wheels, brakes, etc.) or models (such as heavy duty trucks) or 'synonyms' (terms used to group similar features or models) used as positive (W/) and/or negative (N/) tokens in logic configurations used to match orders with necessary parts. The tool will then evaluate the net positive result while also checking features against Model Market Application Compatibility records so that only relevant results are provided.

Here are a few quick examples:

## Net Positive Features

The primary motiviation for creating this tool was to eliminate the hours of manual research involved to determine the net positive result when provided with gross positive and negative tokens. Here is an example for rear axle codes that reduces 1 gross positive token and 14 negative tokens (including a mix of individual feature codes and a synonym) into a net positive of just 4 tokens (2 features and 2 synonyms)...and in less than 1 second!

<img width="100%" alt="L040081553 04 00 - 14AA Eval" src="https://github.com/user-attachments/assets/84da1ab8-8ed8-4038-8d2f-b7a8094b00b1" />

## Net Positive Models

The M-CE synonym refers to a particular type of bus. The rule in question was requiring CE bus but restricting the electric models, M-CE-ELECTRIC. The tool was able to match the remaining non-electric models with the M-CE-N/ELECTRIC synonym.

<img width="100%" alt="SA14098732 13 00 - Model Eval" src="https://github.com/user-attachments/assets/5c9b043d-f27a-4885-8c07-9de75a6f1302" />

## Simplification

If the goal is only to check for possible simplification of required individual features into synonyms, the N/ condition may be left blank. This example also demonstrates how the tool will automatically re-run the SQL query to the database (via Hadoop) on a once-daily basis.

<img width="100%" alt="SR14062032_04_00_Evaluation" src="https://github.com/user-attachments/assets/dbc68bff-735c-4124-aaf4-812988e90298" />
