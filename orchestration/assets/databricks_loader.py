import time
import pandas as pd


def execute_insert(cursor, table_name, rows, batch_size=500, max_retries=3, retry_delay=5):
    if not rows:
        return

    df = pd.DataFrame(rows)
    columns = df.columns.tolist()
    column_list = ", ".join(columns)

    total_batches = (len(df) + batch_size - 1) // batch_size

    for i in range(0, len(df), batch_size):
        batch_num = (i // batch_size) + 1
        batch_df = df.iloc[i:i + batch_size]

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
                    row_values.append("'" + str(val).replace("'", "''") + "'")
            values_parts.append(f"({', '.join(row_values)})")

        insert_sql = f"""
        INSERT INTO {table_name}
        ({column_list})
        VALUES
        {', '.join(values_parts)}
        """

        for attempt in range(max_retries):
            try:
                cursor.execute(insert_sql)
                print(f"Batch {batch_num}/{total_batches} inserted successfully")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"Batch {batch_num}/{total_batches} failed "
                        f"(attempt {attempt + 1}/{max_retries}): {e}. Retrying..."
                    )
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise RuntimeError(
                        f"Batch {batch_num}/{total_batches} failed after "
                        f"{max_retries} attempts: {e}"
                    ) from e

        # Small pause between batches to keep warehouse alive
        # and avoid overwhelming it
        time.sleep(0.5)