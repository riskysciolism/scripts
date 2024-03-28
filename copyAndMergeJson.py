import json
import argparse

def merge_dicts(source: dict[str, any], target: dict[str, any], force=False):
    '''
    Combines the output of two nested dictionaries and respects existing values unless forced to overwrite them
    '''
    merged = target.copy()
    # Iterate over entries of json which should be copied to target file
    for key, value in source.items():
        # Step one nested dictionary deeper if entry is a dict itself and exists in the target file
        if key in merged and isinstance(value, dict) and isinstance(merged[key], dict):
            merged[key] = merge_dicts(value, merged[key], force)
        # Write value to leaf if it not exists or if forced
        elif key not in merged or force:
            merged[key] = value
    return merged

def extract_dict(dictionary: dict[str, any], parts: list[str]) -> dict[str, any]:
    '''
    Returns only the given path of the dictionary and dismisses the rest
    '''
    # Reached end of defined keys
    if not parts:
        return dictionary
    current_key = parts[0]
    if current_key in dictionary:
        if len(parts) == 1:
            return {current_key: dictionary[current_key]}
        else:
            return {current_key: extract_dict(dictionary[current_key], parts[1:])}
    else:
        raise Exception(f"Key {current_key} not found.")

def main():
    parser = argparse.ArgumentParser(description='Copy defined keys from one json file to another')
    parser.add_argument('source_file', metavar='source_file', type=str, help='Path to source json file')
    parser.add_argument('target_file', metavar='target_file', type=str, help='Path to target json file')
    parser.add_argument('--keys', metavar='keys', type=str, nargs='+', help='Keys to copy in json format (foo.bar.test)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing values')

    args = parser.parse_args()

    # Load source file
    try:
        with open(args.source_file, 'r', encoding='utf-8') as source_f:
            source_json = json.load(source_f)
    except:
        print("Source file not found:" , args.source_file)
        exit()

    # Load target file
    try:
        with open(args.target_file, 'r', encoding='utf-8') as target_f:
            target_json = json.load(target_f)
    except:
        target_json = {}
        
    # Collect keys user is interested in and merge them with the target file
    merged = {}

    if args.keys:
        for key in args.keys:
            key = key.strip()
            try:
                merged = merge_dicts(extract_dict(source_json, key.split(".")), merged)
            except:
                print("Key not found in source file:", key)
                exit()
        merged = merge_dicts(merged, target_json, args.force)
    else:
        merged = merge_dicts(source_json, target_json, args.force)

    # Write target json
    with open(args.target_file, 'w+', encoding='utf-8') as target_f:
        json.dump(merged, target_f, ensure_ascii=False, indent=4)

    print('Done.')

if __name__ == "__main__":
    main()
