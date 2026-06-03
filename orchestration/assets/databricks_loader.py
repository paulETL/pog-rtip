import pandas as pd


def execute_insert(cursor, table_name, rows, batch_size=5000):
    """
    Optimized bulk insert rows into Databricks.

    rows = list of dictionaries
    cursor = databricks cursor (kept open for transaction management)
    """

    if not rows:
        return

    # Convert to DataFrame for easier processing
    df = pd.DataFrame(rows)
    
    # Get column names
    columns = df.columns.tolist()
    column_list = ", ".join(columns)
    
    # Process in batches and build multi-row INSERT statements
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        
        # Build VALUES clauses for all rows in batch
        values_parts = []
        for _, row in batch_df.iterrows():
            row_values = []
            for val in row:
                if pd.isna(val):
                    row_values.append("NULL")
                elif isinstance(val, bool):
                    row_values.append(str(val).upper())
                elif isinstance(val, (int, float)):
                    row_values.append(str(val))
                else:
                    # Escape single quotes
                    row_values.append("'" + str(val).replace("'", "''") + "'")
            values_parts.append(f"({', '.join(row_values)})")
        
        # Build and execute single multi-row INSERT
        insert_sql = f"""
        INSERT INTO {table_name}
        ({column_list})
        VALUES
        {', '.join(values_parts)}
        """
        
        cursor.execute(insert_sql)
