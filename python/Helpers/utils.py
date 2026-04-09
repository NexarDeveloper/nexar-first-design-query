def print_delimiter_1():
    print("########################################\n")

def print_delimiter_2():
    print("----------------------------------------\n")

def print_nested(data, indent=0):
    spacing = "  " * indent

    if not isinstance(data, dict):
        print(f"{spacing}{data}")
        return

    # Filter out unwanted keys and find the longest key at THIS level
    valid_keys = [k for k in data.keys() if str(k).lower() not in ['name', 'value']]

    if not valid_keys:
        return

    # Calculate max width of keys at this level for vertical colon alignment
    max_key_len = max(len(str(k)) for k in valid_keys)

    for key in valid_keys:
        value = data[key]

        if isinstance(value, dict):
            print(f"\n{spacing}{key}:")
            print_nested(value, indent + 2)

        elif isinstance(value, list):
            # Align the key and colon
            print(f"{spacing}{str(key):<{max_key_len}} :")
            for item in value:
                # Align bullet points under where the value would start
                print(f"{spacing}{' ' * (max_key_len + 3)} - {item}")

        else:
            # Key aligned to max width, followed by a colon and double tabs
            print(f"{spacing}{str(key):<{max_key_len}} :\t\t{value}")



