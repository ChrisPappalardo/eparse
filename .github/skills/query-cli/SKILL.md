---
name: query-cli
description: Use this skill to query parsed Excel data using the eparse CLI. Call when you need to analyze, filter, or summarize data stored in SQLite or PostgreSQL databases created by eparse.
license: MIT
---
# Query Parsed Data with eparse CLI

## When to use
- To analyze, filter, or summarize data extracted from Excel files and stored in a database.
- For reporting, data validation, or extracting subsets of data.

## How to use
1. Query distinct column headers:
   ```sh
   eparse -i sqlite3:///.files/mydb.db -o stdout:/// query -m get_c_header
   ```
2. Query all data (untruncated):
   ```sh
   eparse -t -i sqlite3:///.files/mydb.db -o stdout:/// query
   ```
3. Filter data (e.g., by file name):
   ```sh
   eparse -i sqlite3:///.files/mydb.db -o stdout:/// query --filter f_name "somefile.xlsx"
   ```
- Replace `sqlite3:///.files/mydb.db` with your database URI. PostgreSQL is also supported.
- See README for filter options and advanced usage.
