import pandas as pd
from openpyxl.styles import Font  
from dataclasses import dataclass, field

@dataclass
class Xl_workbook:
    title: str
    writer: pd.ExcelWriter = field(init=False)

    # In the context of a dataclass, using __post_init__ is useful 
    # when you need to perform additional 
    # initialization after the automatic __init__ has been called.
    def __post_init__(self): 
        # Initialize the ExcelWriter with the provided title
        self.writer = pd.ExcelWriter(self.title, engine='openpyxl')

    def save_workbook(self):
        # Save the workbook using the ExcelWriter's save method
        self.writer._save()

@dataclass
class Sheet:
    title: str
    workbook: Xl_workbook

    def insert_data(self, dataframe):
        # Write the DataFrame to the specified sheet within the workbook
        dataframe.to_excel(self.workbook.writer, sheet_name=self.title, index=False)

    def apply_style(self):
        # Access the workbook and the specified worksheet
        workbook = self.workbook.writer.book  
        worksheet = workbook[self.title]
        
        # Apply bold font to the header row
        for cell in worksheet[1]:  # Loop through cells in the header row
            cell.font = Font(bold=True) 

        # Apply filter to the entire header row
        worksheet.auto_filter.ref = worksheet.dimensions

    

def find_extra_cols(src1, src2):
    src1_exclusive = set(src1.columns).difference(set(src2.columns))
    src2_exclusive = set(src2.columns).difference(set(src1.columns))
    return src1_exclusive, src2_exclusive
    

def find_extra_records(df1, df2, cols, source1_name, source2_name):

    new_df1 = df1.copy()
    new_df1['Source'] = source1_name
    new_df2 = df2.copy()
    new_df2['Source'] = source2_name
    
    combined = pd.concat([new_df1, new_df2], ignore_index=True)
    
    # Find rows exclusive to each DataFrame
    only_in_df1 = combined[~combined.duplicated(subset=cols, keep=False) & (combined['Source'] == source1_name)]
    only_in_df2 = combined[~combined.duplicated(subset=cols, keep=False) & (combined['Source'] == source2_name)]
    
    return only_in_df1, only_in_df2


combine_exclusives = lambda src1_exclusive, src2_exclusive: pd.concat([src1_exclusive, 
                                                   src2_exclusive], 
                                                  ignore_index=True)

save_processed_file_to_csv = lambda normalized_df, filename: normalized_df.to_csv(filename,encoding='utf-8', index=False)


#Driver code
base_path = "C:/Users/AM874RK/OneDrive - EY/Documents/Python_Scripts/Exclusives/" 
src1_df = pd.read_csv(base_path + "src1_data.csv")
src2_df = pd.read_csv(base_path + "src2_data.csv")

src1_exclusive_cols, src2_exclusive_cols = find_extra_cols(src1_df, src2_df)
exclusive_cols_df = pd.DataFrame({
    'src1_exclusive_cols': list(src1_exclusive_cols),
    'src2_exclusive_cols': list(src2_exclusive_cols)
})

print("exclusive_cols : ", exclusive_cols_df)

src1_df.drop(src1_exclusive_cols, axis=1,inplace=True)
src2_df.drop(src2_exclusive_cols, axis=1,inplace=True)


#print(src1_df.columns)
#print(src2_df.columns)

#print("src1_df:",src1_df)
#print("src2_df:",src2_df)

# Find exclusive records
src1_exclusive_records, src2_exclusive_records = find_extra_records(src1_df, src2_df, ['ID'], "QA", "Prod")

# Combine exclusive records from src1 and src2
combined_exclusive_records = combine_exclusives(src1_exclusive_records, src2_exclusive_records)
print("Combined exclusive records:\n", combined_exclusive_records)

src1_exclusive_records = src1_exclusive_records.drop('Source', axis=1)
print(f"src1_exclusive_records\n{src1_exclusive_records}")
src2_exclusive_records = src2_exclusive_records.drop('Source', axis=1)
print(f"src2_exclusive_records\n{src2_exclusive_records}")

# Normalize src1_df and src2_df by removing rows present in respective exclusive records
normalized_src1_df = src1_df.drop(src1_exclusive_records.index)

normalized_src2_df = src2_df[~src2_df.index.isin(src1_exclusive_records.index)]

print("Normalized src1_df:\n", normalized_src1_df)
print("Normalized src2_df:\n", normalized_src2_df)

save_processed_file_to_csv(normalized_src1_df, "normalized_src1_df_1.csv")
save_processed_file_to_csv(normalized_src2_df, "normalized_src2_df_1.csv")

# Create workbook and sheets
workbook = Xl_workbook("Extras.xlsx")
sheet1 = Sheet("extra_cols", workbook)
sheet1.insert_data(exclusive_cols_df)
sheet1.apply_style()

sheet2 = Sheet("extra_records", workbook)
sheet2.insert_data(combined_exclusive_records)
sheet2.apply_style() 

workbook.save_workbook()