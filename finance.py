import db

if __name__ == "__main__":
    import sys

    action = sys.argv[1]

    if action == "add_table":
        if len(sys.argv) < 3:
            print("Add table needs at least 2 parameters")
            sys.exit(1)
        table_name = sys.argv[2]

    if action == "add_column":
        if len(sys.argv) != 4:
            print("Add column needs 3 parameters")
            sys.exit(1)
        column_name = sys.argv[2]
        column_type = sys.argv[3]
        db.add_column_to_tables(column_name, column_type)

    if action == "save_snapshot":
        row_id = db.save_snapshot()
        print("Saved snapshot", row_id)

    if action == "snapshot":
        print(db.get_bucket("snapshot"))

    if action == "delete_table":
        print("delete")
        db.delete_table(sys.argv[2])
        print("deleted")

    if action == "show_buckets":
        buckets = db.get_all_buckets()
        for key,bucket in buckets.items():
            print(key)
            for transaction in bucket:
                print(transaction)
