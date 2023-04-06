import copy
import json
import os


def is_rng_in_keys(keys):
    """ Check for RNG inside the key sequence """
    for key in keys:
        if isinstance(key, str):
            if 'rng' in key:
                return True
    return False


def find_tensors(value, keys: list = None):
    """ Search for tensors within a checkpoint
    and return the key sequences to those tensors,
    except for RNG tensors """
    if keys is None:
        keys = []
    if isinstance(value, dict):
        new_tensor_keys = []
        for key, val in value.items():
            if key == 'tensor':
                if not is_rng_in_keys(keys):
                    return [keys]
                return None

            new_keys = copy.deepcopy(keys)
            new_keys.append(key)
            tensor_keys = find_tensors(val, new_keys)
            if tensor_keys:
                new_tensor_keys.extend(tensor_keys)
        return new_tensor_keys
    if isinstance(value, (list, set, tuple)):
        new_tensor_keys = []
        for i, val in enumerate(value):
            new_keys = copy.deepcopy(keys)
            new_keys.append(i)
            tensor_keys = find_tensors(val, new_keys)
            if tensor_keys:
                new_tensor_keys.extend(tensor_keys)
        return new_tensor_keys

    return None


def main():
    framework = 'megatron-lm'
    model = 'gpt'
    model_size = 'xl'
    # precision = 'fp16'
    # seq_length = 1024
    pp_size = 2
    mp_size = 1
    dp_size = 2
    total_size = pp_size * mp_size * dp_size
    # direc = f'{framework}/{precision}/seq_{seq_length}/pp{pp_size:02d}/mp{mp_size:02d}/dp{dp_size:02d}'
    direc = f'{framework}/{model}/{model_size}/pp{pp_size:02d}/mp{mp_size:02d}/dp{dp_size:02d}'

    model_keys = {}

    for rank in range(total_size):
        rank_dir = os.path.join(direc, f'rank{rank:02d}')

        if not os.path.exists(rank_dir):
            continue

        path = ""
        for entry in os.scandir(rank_dir):
            if not entry.is_file():
                continue
            path = entry.path

        with open(path, "r") as json_file:
            rank_struct = json.load(json_file)

        model_keys[rank] = find_tensors(rank_struct["model"], ["model"])

    #  import pprint
    #  pprint.pprint(model_keys)

    with open(os.path.join(direc, "model_keys.json"), "w") as json_file:
        json.dump(model_keys, json_file, indent=4)


if __name__ == "__main__":
    main()
