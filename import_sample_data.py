from utils.csv_importer import CSVImporter


def import_all_data():
    try:
        print("Bắt đầu import dữ liệu mẫu...")

        print("1. Import danh mục...")
        CSVImporter.import_categories('sample_data/categories.csv')
        print("✓ Import danh mục thành công!")

        print("2. Import menu...")
        CSVImporter.import_menu_items('sample_data/menu_items.csv')
        print("✓ Import menu thành công!")

        print("3. Import users...")
        CSVImporter.import_users('sample_data/users.csv')
        print("✓ Import users thành công!")

        print("4. Import tables...")
        CSVImporter.import_tables('sample_data/tables.csv')
        print("✓ Import tables thành công!")

        print("5. Import inventory...")
        CSVImporter.import_inventory('sample_data/inventory.csv')
        print("✓ Import inventory thành công!")

        print("\nImport dữ liệu mẫu hoàn tất!")

    except Exception as e:
        print(f"\nLỗi khi import dữ liệu: {str(e)}")
        print("Vui lòng kiểm tra lại các file CSV và thử lại.")


if __name__ == "__main__":
    import_all_data()
