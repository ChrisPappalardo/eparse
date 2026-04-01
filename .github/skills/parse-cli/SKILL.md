---
name: parse-cli
description: Use this skill to extract and list tables from Excel files using the eparse CLI. Call when you need to discover or extract tabular data from one or more Excel files or directories. Supports output to console, SQLite, or PostgreSQL.
license: MIT
---
# Parse Excel Files with eparse CLI

## When to use
- To discover, extract, or validate tables in Excel files or directories.
- For initial data exploration or to prepare data for querying.

## How to use
1. Run the following command, replacing `<path_to_files>` with your file or directory:
   ```sh
   eparse -v -f <path_to_files> parse
   ```
2. For output to SQLite (choose your own database file name):
   ```sh
   mkdir -p .files
   eparse -f <path_to_files> -o sqlite3:///.files/<your_db_file>.db parse -z
   ```
   - Replace `<your_db_file>` with your desired SQLite database file name.
3. For output to PostgreSQL (requires psycopg2):
   ```sh
   eparse -f <path_to_files> -o postgres://<user>:<password>@<host>:<port>/<db_name> parse -z
   ```
   - Replace `<user>`, `<password>`, `<host>`, `<port>`, and `<db_name>` with your PostgreSQL credentials and database name.

- Use `-t` to avoid truncation, `-l` for loose table detection, and `--exclude-nested` to skip nested tables.
- See README for more options.
