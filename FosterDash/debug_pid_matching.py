import pandas as pd
import os

def debug_pid_matching():
    """Debug PID matching between foster parents database and FosterCurrent.csv"""
    
    # Load foster parents data
    excel_path = "../__Load Files Go Here__/Looking for Foster Care 2025.xlsx"
    foster_parents_df = pd.read_excel(excel_path, sheet_name="Available Foster Parents")
    
    # Clean up the data
    foster_parents_df = foster_parents_df.dropna(subset=['PID'])
    
    # Test different PID formatting approaches
    def format_pid_v1(pid):
        """Original approach: pad to 9 digits after P"""
        if pd.isna(pid):
            return ''
        pid_str = str(pid).strip()
        if pid_str.startswith('P'):
            return pid_str
        try:
            pid_int = int(float(pid_str))
            numeric_part = str(pid_int)
        except (ValueError, TypeError):
            numeric_part = pid_str
        numeric_part = numeric_part.zfill(9)
        return f"P{numeric_part}"
    
    def format_pid_v2(pid):
        """New approach: pad to 10 digits total"""
        if pd.isna(pid):
            return ''
        pid_str = str(pid).strip()
        if pid_str.startswith('P'):
            return pid_str
        try:
            pid_int = int(float(pid_str))
            numeric_part = str(pid_int)
        except (ValueError, TypeError):
            numeric_part = pid_str
        # Pad to 10 digits total (P + 9 digits)
        numeric_part = numeric_part.zfill(9)
        return f"P{numeric_part}"
    
    def format_pid_v3(pid):
        """Alternative: add P00 prefix to 8-digit numbers"""
        if pd.isna(pid):
            return ''
        pid_str = str(pid).strip()
        if pid_str.startswith('P'):
            return pid_str
        try:
            pid_int = int(float(pid_str))
            numeric_part = str(pid_int)
        except (ValueError, TypeError):
            numeric_part = pid_str
        # If it's 8 digits, add P00 prefix
        if len(numeric_part) == 8:
            return f"P00{numeric_part}"
        else:
            return f"P{numeric_part}"
    
    # Apply different formatting approaches
    foster_parents_df['Full_PID_v1'] = foster_parents_df['PID'].apply(format_pid_v1)
    foster_parents_df['Full_PID_v2'] = foster_parents_df['PID'].apply(format_pid_v2)
    foster_parents_df['Full_PID_v3'] = foster_parents_df['PID'].apply(format_pid_v3)
    
    # Load FosterCurrent data
    foster_current_path = "../__Load Files Go Here__/FosterCurrent.csv"
    foster_current_df = pd.read_csv(foster_current_path, encoding='utf-8', skiprows=6)
    
    print("=== DEBUG PID MATCHING ===")
    print(f"Foster Parents Database: {len(foster_parents_df)} records")
    print(f"FosterCurrent.csv: {len(foster_current_df)} records")
    
    # Show sample PIDs from foster parents database
    print("\n=== SAMPLE PIDs FROM FOSTER PARENTS DATABASE ===")
    sample_pids = foster_parents_df[['PID', 'Full_PID_v1', 'Full_PID_v2', 'Full_PID_v3']].head(5)
    for idx, row in sample_pids.iterrows():
        print(f"Original: {row['PID']}")
        print(f"  V1: {row['Full_PID_v1']}")
        print(f"  V2: {row['Full_PID_v2']}")
        print(f"  V3: {row['Full_PID_v3']}")
        print()
    
    # Show sample PIDs from FosterCurrent
    print("\n=== SAMPLE PIDs FROM FOSTERCURRENT ===")
    sample_foster_current = foster_current_df[['textbox10']].head(5)
    for idx, row in sample_foster_current.iterrows():
        print(f"PID: {row['textbox10']}")
    
    # Get unique PIDs from FosterCurrent
    foster_current_pids = set()
    for idx, row in foster_current_df.iterrows():
        pid = str(row.get('textbox10', ''))
        if pid and pid != 'nan':
            foster_current_pids.add(pid)
    
    # Test matching with different approaches
    database_pids_v1 = set(foster_parents_df['Full_PID_v1'].tolist())
    database_pids_v2 = set(foster_parents_df['Full_PID_v2'].tolist())
    database_pids_v3 = set(foster_parents_df['Full_PID_v3'].tolist())
    
    print(f"\n=== PID COMPARISON ===")
    print(f"Unique PIDs in FosterCurrent: {len(foster_current_pids)}")
    print(f"Unique PIDs in Database (V1): {len(database_pids_v1)}")
    print(f"Unique PIDs in Database (V2): {len(database_pids_v2)}")
    print(f"Unique PIDs in Database (V3): {len(database_pids_v3)}")
    
    # Find matching PIDs with each approach
    matching_pids_v1 = foster_current_pids.intersection(database_pids_v1)
    matching_pids_v2 = foster_current_pids.intersection(database_pids_v2)
    matching_pids_v3 = foster_current_pids.intersection(database_pids_v3)
    
    print(f"Matching PIDs (V1): {len(matching_pids_v1)}")
    print(f"Matching PIDs (V2): {len(matching_pids_v2)}")
    print(f"Matching PIDs (V3): {len(matching_pids_v3)}")
    
    # Show some matching PIDs with the best approach
    best_matches = matching_pids_v3 if matching_pids_v3 else (matching_pids_v2 if matching_pids_v2 else matching_pids_v1)
    if best_matches:
        print(f"\n=== SAMPLE MATCHING PIDs (BEST APPROACH) ===")
        for pid in sorted(list(best_matches))[:5]:
            print(f"✓ {pid}")

if __name__ == "__main__":
    debug_pid_matching() 