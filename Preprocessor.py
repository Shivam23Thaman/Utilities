import pandas as pd
from openpyxl.styles import Font  
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple
import argparse

@dataclass
class XlWorkbook:
    title: str
    writer: pd.ExcelWriter = field(init=False)

    def __post_init__(self): 
        """Initialize the ExcelWriter with the provided title."""
        self.writer = pd.ExcelWriter(self.title, engine='openpyxl')

    def save_workbook(self):
        self.writer._save()
        self.writer.close()

@dataclass
class Sheet:
    title: str
    workbook: XlWorkbook

    def insert_data(self, dataframe: pd.DataFrame):
        dataframe.to_excel(self.workbook.writer, sheet_name=self.title, index=False)

    def apply_style(self):
        workbook = self.workbook.writer.book  
        worksheet = workbook[self.title]
        
        # Apply bold font to the header row
        for cell in worksheet[1]:  # Loop through cells in the header row
            cell.font = Font(bold=True) 

        # Apply filter to the entire header row
        worksheet.auto_filter.ref = worksheet.dimensions

def find_extra_cols(src1: pd.DataFrame, src2: pd.DataFrame) -> Tuple[set, set]:
    src1_exclusive = set(src1.columns).difference(set(src2.columns))
    src2_exclusive = set(src2.columns).difference(set(src1.columns))
    return src1_exclusive, src2_exclusive

def find_extra_records(df1: pd.DataFrame, df2: pd.DataFrame, cols: list, source1_name: str, source2_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df1 = df1.assign(Source=source1_name)
    df2 = df2.assign(Source=source2_name)
    combined = pd.concat([df1, df2], ignore_index=True)
    
    only_in_df1 = combined[~combined.duplicated(subset=cols, keep=False) & (combined['Source'] == source1_name)]
    only_in_df2 = combined[~combined.duplicated(subset=cols, keep=False) & (combined['Source'] == source2_name)]
    
    return only_in_df1, only_in_df2

combine_exclusives = lambda src1_exclusive, src2_exclusive: pd.concat([src1_exclusive, src2_exclusive], ignore_index=True)

def save_processed_file_to_csv(normalized_df: pd.DataFrame, filename: str):
    normalized_df.to_csv(filename, encoding='utf-8', index=False)

def main(src1_file: str, src2_file: str, sources: list, pk: list, excel_output: str):
    base_path = Path().resolve()  # Use current directory for output files
    src1_df = pd.read_csv(src1_file)
    src2_df = pd.read_csv(src2_file)

    # Extract source names
    source1_name = sources[0]
    source2_name = sources[1]

    # Find exclusive columns
    src1_exclusive_cols, src2_exclusive_cols = find_extra_cols(src1_df, src2_df)
    exclusive_cols_df = pd.DataFrame({
        'src1_exclusive_cols': list(src1_exclusive_cols),
        'src2_exclusive_cols': list(src2_exclusive_cols)
    })

    print("Exclusive columns:\n", exclusive_cols_df)

    # Drop exclusive columns from the DataFrames
    src1_df.drop(src1_exclusive_cols, axis=1, inplace=True)
    src2_df.drop(src2_exclusive_cols, axis=1, inplace=True)

    # Find exclusive records
    src1_exclusive_records, src2_exclusive_records = find_extra_records(src1_df, src2_df, pk, source1_name, source2_name)

    # Combine exclusive records from src1 and src2
    combined_exclusive_records = combine_exclusives(src1_exclusive_records, src2_exclusive_records)
    print("Combined exclusive records:\n", combined_exclusive_records)

    # Drop the 'Source' column from exclusive records
    src1_exclusive_records = src1_exclusive_records.drop('Source', axis=1)
    src2_exclusive_records = src2_exclusive_records.drop('Source', axis=1)

    # Normalize src1_df and src2_df by removing rows present in respective exclusive records
    normalized_src1_df = src1_df.drop(src1_exclusive_records.index)
    normalized_src2_df = src2_df[~src2_df.index.isin(src1_exclusive_records.index)]

    print("Normalized src1_df:\n", normalized_src1_df)
    print("Normalized src2_df:\n", normalized_src2_df)

    # Save normalized DataFrames to CSV
    save_processed_file_to_csv(normalized_src1_df, base_path / f"{source1_name}_normalized_df.csv")
    save_processed_file_to_csv(normalized_src2_df, base_path / f"{source2_name}_normalized_df.csv")

    # Create workbook and sheets
    workbook = XlWorkbook(excel_output)
    sheet1 = Sheet("extra_cols", workbook)
    sheet1.insert_data(exclusive_cols_df)
    sheet1.apply_style()

    sheet2 = Sheet("extra_records", workbook)
    sheet2.insert_data(combined_exclusive_records)
    sheet2.apply_style() 

    # Save the workbook
    workbook.save_workbook()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process two CSV files and generate reports.")
    parser.add_argument("src1_file", type=str, help="Path to the first source CSV file.")
    parser.add_argument("src2_file", type=str, help="Path to the second source CSV file.")
    parser.add_argument("sources", type=str, help="Sources in the format sources=[source1,source2].")
    parser.add_argument("pk", type=str, help="Primary keys in the format pk=[key1,key2].")
    parser.add_argument("excel_output", type=str, help="Filename for the output Excel file.")

    args = parser.parse_args()
    
    # Extract sources and primary keys from the input strings
    sources = args.sources.split('=')[1].strip('[]').split(',')
    pk = args.pk.split('=')[1].strip('[]').split(',')

    # Clean up whitespace
    sources = [source.strip() for source in sources]
    pk = [key.strip() for key in pk]

    main(args.src1_file, args.src2_file, sources, pk, args.excel_output)