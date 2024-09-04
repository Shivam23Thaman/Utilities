# Utilities
Problem Statement:

While processing(Eg- comparing) huge data from two sources, we need to find which columns and records are extra in which source. Finding this via Excel could have some challenges. Other systems/ scripts may not be able to work with different no. of records.

challenges with Excel:
  1. It may lead to Excel window showing 'Not Responding' when there is huge data.
  2. Vlookup etc may not be beginner friendly
  3. Cannot directly use it as preprocessor that can be fed to an automated system (Manual intervention).
  4. Time Consuming

Solution
A Proprocessor utility built on python & pandas allows us to find exclusive columns and records from two sources. It stores the Extra results for later view and remove them from both python objects built on the data from CSV files. Note - Your original csv files both sources will remain intact.

Benifits
1. Quick results
2. Stores results in Excel workbook with proper highlights and filters preapplied.
3. Can be used as a preprocessor for further use. Can be integrated in other systems like Databases & Linux.
4. Uses the new dataclasses functionality in python.

Usage

python Preprocessor.py src1_data.csv src2_data.csv  sources=[qa,prod] pk=[ID] Extras2.xlsx

sources=give the names of the output Normalized csvs
pk=Primary key. Eg - ID

Output

qa_Normalized.csv
prod_Normalized.csv
Extras.xlsx







 
