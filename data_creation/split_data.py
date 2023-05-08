import argparse
import random
import json
import os

def split_data(input_filename, output_train_filename, output_val_filename, output_test_filename):

    train_examples = []
    val_examples = []
    test_examples = []

    event_mapper = {}
    done_mapper = {}
    with open(input_filename, 'r') as in_file:
        for line in in_file:
            in_example = json.loads(line)
            example_id = in_example["wnd_id"]
            event_mentions = in_example["event_mentions"]
            for event_mention in event_mentions:
                event_type = event_mention["event_type"]
                if event_type not in event_mapper:
                    event_mapper[event_type] = []
                if example_id not in event_mapper[event_type]:
                    event_mapper[event_type].append(example_id)
                done_mapper[example_id] = 0

    sorted_event_mapper = sorted(event_mapper.items(), key=lambda kv:len(kv[1]))
    for event_type, event_list in sorted_event_mapper:
        examples_to_sample = max(min_examples_test, int(min_percentage_test*len(event_list))+1)
        remaining_list = [ t for t in event_list if done_mapper[t] == 0 ]
        test_example_ids = random.sample(remaining_list, examples_to_sample)
        remaining_list = list(set(remaining_list) - set(test_example_ids))
        val_example_ids = random.sample(remaining_list, min(int(percentage_val*len(event_list))+1, len(remaining_list)))
        train_example_ids = list(set(remaining_list) - set(val_example_ids))
        
        train_examples.extend(train_example_ids)
        val_examples.extend(val_example_ids)
        test_examples.extend(test_example_ids)
        
        for e in event_list:
            done_mapper[e] = 1

    print ("Total number of train examples: %d" % len(train_examples))
    print ("Total number of val examples: %d" % len(val_examples))
    print ("Total number of test examples: %d" % len(test_examples))
    print ("Total number of examples: %d" % (len(train_examples) + len(val_examples) + len(test_examples)))

    with open(input_filename, 'r') as in_file, open(output_train_filename, 'w') as train_file, open(output_val_filename, 'w') as val_file, open(output_test_filename, 'w') as test_file:
        for line in in_file:
            in_example = json.loads(line)
            example_id = in_example["wnd_id"]
            if example_id in train_examples:
                train_file.write(line)
            elif example_id in val_examples:
                val_file.write(line)
            elif example_id in test_examples:
                test_file.write(line)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Filter the processed Framenet data based on frames')
    parser.add_argument('-i', '--input-file', type=str,
                        help='path to the input file/processed frames data')
    parser.add_argument('-o', '--output-folder', type=str,
                        help='path to folder for saving output files')
    parser.add_argument('-r', '--random-seed', type=int, default=42,
                        help='seed for randomization')
    args = parser.parse_args()
    random.seed(args.random_seed)

    # Hyperparameters for splitting data
    # Change for different settings
    min_examples_test = 5
    min_percentage_test = 0.1
    percentage_val = 0.1

    # Create output folders
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    output_train_filename = args.output_folder + "/train.json"
    output_val_filename = args.output_folder + "/val.json"
    output_test_filename = args.output_folder + "/test.json"

    # Split data
    split_data(args.input_file, output_train_filename, output_val_filename, output_test_filename)
