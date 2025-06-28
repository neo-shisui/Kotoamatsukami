import os
import sys

def classify_c_files(source_path, store_root_path):
    if not os.path.isdir(source_path):
        print(f"Error: {source_path} is not a directory or doesn't exist.", file=sys.stderr)
        return

    # Tên thư mục gốc của source path (vd: 'sard')
    base_folder_name = os.path.basename(os.path.normpath(source_path))
    store_path = os.path.join(store_root_path, "out")# base_folder_name)

    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(".c"):
                source_file = os.path.join(root, file)
                target_dir = store_path
                target_file = os.path.join(target_dir, file)

                os.makedirs(target_dir, exist_ok=True)

                if not os.path.exists(target_file):
                    with open(source_file, 'r') as fr, open(target_file, 'w') as fw:
                        for line in fr:
                            fw.write(line)

def main():
    if len(sys.argv) != 3:
        print("Usage: python classify_files.py <sourcePath> <outputRootPath>", file=sys.stderr)
        return

    source_path = sys.argv[1]
    output_root_path = sys.argv[2]

    if not os.path.exists(source_path):
        print("Error: Source path does not exist.", file=sys.stderr)
        return

    print(f"Source Path: {source_path}")
    print(f"Output Root Path: {output_root_path}")

    try:
        classify_c_files(source_path, output_root_path)
    except Exception as e:
        print("Exception occurred:", file=sys.stderr)
        print(e, file=sys.stderr)

if __name__ == "__main__":
    main()
