import os
from collections import defaultdict, Counter
from itertools import chain

class FPTree:
    def __init__(self, root_value, root_count, parent):
        self.value = root_value
        self.count = root_count
        self.parent = parent
        self.children = {}
        self.link = None

    def add_new_transaction(self, transaction, header_table):
        first_item = transaction[0]
        if first_item in self.children:
            self.children[first_item].count += 1
        else:
            self.children[first_item] = FPTree(first_item, 1, self)
            if header_table[first_item][1] is None:
                header_table[first_item][1] = self.children[first_item]
            else:
                current_node = header_table[first_item][1]
                while current_node.link is not None:
                    current_node = current_node.link
                current_node.link = self.children[first_item]

        remaining_items = transaction[1:]
        if remaining_items:
            self.children[first_item].add_new_transaction(remaining_items, header_table)

    def apply_conditional_prefix(self, item):
        conditional_patterns = []
        node = self.children.get(item)
        while node:
            prefix_path = []
            parent_node = node.parent
            while parent_node and parent_node.value is not None:
                prefix_path.append(parent_node.value)
                parent_node = parent_node.parent
            if prefix_path:
                conditional_patterns.extend([prefix_path] * node.count)
            node = node.link
        return conditional_patterns


def create_hd_table(dataset, min_support):
    item_frequency = Counter(chain.from_iterable(dataset))
    header_table = {item: [freq, None] for item, freq in item_frequency.items() if freq >= min_support}
    return header_table


def create_fp_tree(dataset, header_table):
    root = FPTree(None, 1, None)
    for transaction in dataset:
        filtered_transaction = [item for item in transaction if item in header_table]
        filtered_transaction.sort(key=lambda item: header_table[item][0], reverse=True)
        if filtered_transaction:
            root.add_new_transaction(filtered_transaction, header_table)
    return root


def mine_fp_tree(header_table, min_support, prefix, frequent_itemsets):
    sorted_items = sorted(header_table.items(), key=lambda x: x[1][0])
    for item, (frequency, node) in sorted_items:
        new_prefix = prefix.copy()
        new_prefix.add(item)
        frequent_itemsets[frozenset(new_prefix)] = frequency

        conditional_patterns = node.apply_conditional_prefix(item) if node else []
        conditional_header_table = create_hd_table(conditional_patterns, min_support)
        if conditional_header_table:
            conditional_tree = create_fp_tree(conditional_patterns, conditional_header_table)
            mine_fp_tree(conditional_header_table, min_support, new_prefix, frequent_itemsets)


def compress_fp_growth(dataset, min_support=2):
    header_table = create_hd_table(dataset, min_support)
    fp_tree = create_fp_tree(dataset, header_table)
    frequent_itemsets = {}
    mine_fp_tree(header_table, min_support, set(), frequent_itemsets)
    return frequent_itemsets


def bind_cmp_map(dataset, frequent_itemsets):
    mapping = {chr(65 + idx): itemset for idx, itemset in enumerate(frequent_itemsets.keys())}  # A, B, C...
    compressed_transactions = []
    
    for transaction in dataset:
        compressed_transaction = set()
        for key, itemset in mapping.items():
            if itemset.issubset(transaction):
                compressed_transaction.add(key)
                transaction -= itemset
        compressed_transaction.update(transaction)
        compressed_transactions.append(compressed_transaction)
    
    return compressed_transactions, mapping


def save_cmp_set(compressed_dataset, mapping, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("Compressed Dataset:\n")
        for idx, transaction in enumerate(compressed_dataset):
            sanitized_transaction = ''.join(e for e in transaction if e.isalnum() or e == ':')
            file.write(f"Transaction {idx + 1}: {' '.join(sanitized_transaction)}\n")
        
        file.write("\nMapping:\n")
        for key, itemset in sorted(mapping.items()):
            sanitized_itemset = ''.join(e for e in itemset if e.isalnum() or e == ':')
            file.write(f"{key}: {', '.join(sanitized_itemset)}\n")


def load_raw_data(file_path):
    dataset = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            transaction = set(line.strip().split())
            dataset.append(transaction)
    return dataset


def analyze_dataset(dataset):
    """Analyze the dataset and print basic statistics."""
    total_transactions = len(dataset)
    all_items = set(chain.from_iterable(dataset))
    item_frequency = Counter(chain.from_iterable(dataset))
    
    print(f"Total Transactions: {total_transactions}")
    print(f"Total Unique Items: {len(all_items)}")
    print(f"Top 10 Most Frequent Items: {item_frequency.most_common(10)}")


def main():

    file_path = "./dataset.dat"
    output_file = "./compressed_dataset.txt"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    dataset = load_raw_data(file_path)
    analyze_dataset(dataset)
    min_support = 2
    frequent_itemsets = compress_fp_growth(dataset, min_support)
    compressed_dataset, mapping = bind_cmp_map(dataset, frequent_itemsets)
    save_cmp_set(compressed_dataset, mapping, output_file)
    print(f"Compressed dataset saved to {output_file}")


if __name__ == "__main__":
    main()
