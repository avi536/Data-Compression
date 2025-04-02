import os
from collections import Counter
from itertools import chain

class FPTree:
    def __init__(self, root_value, root_count, parent):
        self.value = root_value
        self.count = root_count
        self.parent = parent
        self.children = {}
        self.link = None  


def rem_invalid_keys(compressed_dataset, mapping):
   
    used_keys = set(chain.from_iterable(compressed_dataset))
    updated_mapping = {key: itemset for key, itemset in mapping.items() if key in used_keys}
    return updated_mapping


def save_cmp_data(compressed_dataset, mapping, output_file):
   
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("Compressed Dataset:\n")
        for idx, transaction in enumerate(compressed_dataset):
            sanitized_transaction = ' '.join(e for e in transaction if e.isalnum() or e == ':')
            file.write(f"Transaction {idx + 1}: {sanitized_transaction}\n")
        
        file.write("\nMapping:\n")
        for key, itemset in sorted(mapping.items()):
            sanitized_itemset = ', '.join(e for e in itemset if e.isalnum() or e == ':')
            file.write(f"{key}: {sanitized_itemset}\n")


def load_cmp_map(file_path):
    dataset = []
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reading_dataset = True
        for line in file:
            line = line.strip()
            if not line:
                continue
            if "Mapping:" in line:
                reading_dataset = False
                continue
            if reading_dataset:
                parts = line.split()
                if len(parts) > 2:
                    transaction = set(parts[2:])
                    dataset.append(transaction)
            else:
                key, itemset = line.split(': ')
                mapping[key] = set(itemset.split(', '))
    return dataset, mapping


def main():
    compressed_dataset_path = "./compressed_dataset.txt"
    output_file = "./updated_compressed_dataset.txt"
    
    if not os.path.exists(compressed_dataset_path):
        print(f"File not found: {compressed_dataset_path}")
        return
    
    compressed_dataset, mapping = load_cmp_map(compressed_dataset_path)
    updated_mapping = rem_invalid_keys(compressed_dataset, mapping)
    save_cmp_data(compressed_dataset, updated_mapping, output_file)
    
    print(f"Updated compressed dataset saved to {output_file}")

if __name__ == "__main__":
    main()
