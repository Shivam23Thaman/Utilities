# Utilities
Problem Statement:

While processing(Eg- comparing) huge data from two sources, we need to find which columns and records are extra in which source. Finding this via Excel could have some challenges. Other systems/ scripts may not be able to work with different no. of records.

challenges with Excel:
  1. It may lead to EXcel window showing 'Not Responding' when there is huge data.
  2. Vlookup etc may not be beginner friendly
  3. Cannot directly use it as preprocessor that can fed to an automated system (Manual intervention).
  4. Time Consuming

Solution
A Proprocessor utility built on python & pandas allows us to find exclusive columns and records from two sources. It stores the Extra results for later view and removes them from both python objects taken built on the data from CSV files. Note - Your original sources remain intact.

Benifits
1. Quick results
2. Stores results in Excel workbook with proper highlights and filters preapplied.
3. Can be used as a preprocessor for further use. Can be integrated in other systems like Databases & Linux.
4. Uses the new dataclasses functionality in python.

Usage
python Preprocessor.py

1. Read two CSV files 
2. In src1_exclusive_records, src2_exclusive_records = find_extra_records(src1_df, src2_df, ['ID'], "QA", "Prod")
   a. replace 'ID' with Primary key(Unique Column(s))
   b. Replace the two source names -> Eg - QA, prod

Output

Eg - Extras.xlsx






 
