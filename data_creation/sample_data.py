import argparse
import random
import json
import os

def filter_example(event_sentence, keep_events_list):
    event_mentions = event_sentence["event_mentions"]
    keep_event_mentions = []
    for event_mention in event_mentions:
        event_type = event_mention["event_type"]
        if event_type in keep_events_list:
            keep_event_mentions.append(event_mention)
    assert len(keep_event_mentions) > 0, "There should be at least one mention of event"
    event_sentence["event_mentions"] = keep_event_mentions
    return event_sentence

def sample_data_by_sampling(input_path, output_folder, num_sample_events, sampling_method='random', rs=42):

    event_mapper = {}
    sent_mapper = {}
    with open(input_path, 'r') as in_file:
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
            if len(event_mentions) not in sent_mapper:
                sent_mapper[len(event_mentions)] = []
            sent_mapper[len(event_mentions)].append(example_id)
    
    if sampling_method == "random":
        reverse_sent_map = {}
        for k,v in sent_mapper.items():
            for e in v:
                reverse_sent_map[e] = k

        sampled_sents = []
        shuffled_example_ids = list(reverse_sent_map.keys())
        random.shuffle(shuffled_example_ids)
        total_sampled_instances = 0
        while total_sampled_instances < num_sample_events:
            sampled_sent = shuffled_example_ids[len(sampled_sents)]
            sampled_sents.append(sampled_sent)
            total_sampled_instances += reverse_sent_map[sampled_sent]
    
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        total_written_instances = 0
        with open(input_path, 'r') as in_file, open(output_folder+'/train-s%d.json' % rs, 'w') as train_file:
            for line in in_file:
                in_example = json.loads(line)
                example_id = in_example["wnd_id"]
                if example_id in sampled_sents:
                    event_mentions = in_example["event_mentions"]
                    new_event_mentions = event_mentions[:num_sample_events - total_written_instances]
                    in_example["event_mentions"] = new_event_mentions
                    total_written_instances += len(new_event_mentions)
                    train_file.write(json.dumps(in_example) + "\n")
                
        print ("Training sents: %d\t\tTraining instances: %d" % (len(sampled_sents), total_written_instances))
        # print (sampled_sents)
    
    elif sampling_method == "uniform":
        all_events = list(event_mapper.keys())
        sampled_sents_with_events = {}
        for e in all_events:
            sampled_example_id = random.sample(event_mapper[e], min(num_sample_events, len(event_mapper[e])))
            for s in sampled_example_id:
                if s not in sampled_sents_with_events:
                    sampled_sents_with_events[s] = []
                sampled_sents_with_events[s].append(e)
        
        print ("Total number of events: %d" % (len(all_events)))

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        total_sampled_instances = 0
        event_done = { e:0 for e in all_events }
        with open(input_path, 'r') as in_file, open(output_folder+'/train-s%d.json' % rs, 'w') as train_file:
            for line in in_file:
                in_example = json.loads(line)
                example_id = in_example["wnd_id"]
                
                if example_id in sampled_sents_with_events:
                    event_mentions = in_example["event_mentions"]
                    new_event_mentions = []
                    for event_mention in event_mentions:
                        event_type = event_mention["event_type"]
                        if event_type in sampled_sents_with_events[example_id] and event_done[event_type] < num_sample_events:
                            total_sampled_instances += 1
                            event_done[event_type] += 1
                            new_event_mentions.append(event_mention)
                    in_example["event_mentions"] = new_event_mentions
                    train_file.write(json.dumps(in_example) + "\n")

        print ("Training sents: %d\t\tTraining instances: %d" % (len(sampled_sents_with_events), total_sampled_instances))
        # print (sampled_sents)

    return

def sample_data_by_events(input_path, output_folder, num_sample_events=0, event_list=None, sort=True, num_sample_datapoints=None):

    event_mapper = {}
    with open(input_path, 'r') as in_file:
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
    
    all_events = list(event_mapper.keys())
    sampled_events = []

    if num_sample_events != 0:
        assert num_sample_events <= len(all_events), "Number of sampled events is more than actual number of events"
        if not sort:
            sampled_events = random.sample(all_events, num_sample_events)
        else:
            sorted_event_mapper = sorted(event_mapper.items(), key=lambda kv: len(kv[1]), reverse=True)
            sampled_events = [ kv[0] for kv in sorted_event_mapper[:num_sample_events] ]
    else:
        for event in event_list:
            assert event in all_events, (event, all_events)
        sampled_events = event_list
    
    print (sampled_events)
    seen_event_data = set([ s for e in sampled_events for s in event_mapper[e] ])
    unseen_event_data = set([ s for e in all_events for s in event_mapper[e] ]) - seen_event_data
    if num_sample_datapoints is not None:
        seen_event_data = random.sample(list(seen_event_data), num_sample_datapoints)
        dev_examples = random.sample(list(seen_event_data), 115)
    else:
        dev_examples = random.sample(list(seen_event_data), int(0.2*len(seen_event_data)))

    train_examples = list(set(seen_event_data) - set(dev_examples))
    test_examples = list(unseen_event_data)

    print ("Sampled Events are ", sampled_events)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_train, num_dev, num_test = 0, 0, 0
    with open(input_path, 'r') as in_file, open(output_folder+'/train.json', 'w') as train_file, \
    open(output_folder+'/dev.json', 'w') as dev_file, open(output_folder+'/test.json', 'w') as test_file:
        for line in in_file:
            in_example = json.loads(line)
            example_id = in_example["wnd_id"]
            if example_id in train_examples:
                cleaned_in_example = filter_example(in_example, sampled_events)
                train_file.write(json.dumps(cleaned_in_example) + "\n")
                num_train += 1
            elif example_id in dev_examples:
                cleaned_in_example = filter_example(in_example, sampled_events)
                dev_file.write(json.dumps(cleaned_in_example) + "\n")
                num_dev += 1
            elif example_id in test_examples:
                test_file.write(line)
                num_test += 1

    print ("Training sents: %d\nDev sents: %d\nTest sents: %d" % (num_train, num_dev, num_test))

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Filter the processed Framenet data based on frames')
    parser.add_argument('-i', '--input-path', type=str,
                        help='path to the input file/processed events data')
    parser.add_argument('-o', '--output-folder', type=str,
                        help='path to folder for saving output files')
    parser.add_argument('-n', '--num-sample-events', type=int,
                        help='number of samples to take. Total datapoints for Low resource. Number of datapoints per event for Few shot. Number of events for Zero shot.')
    parser.add_argument('-s', '--random-seed', type=int, default=42,
                        help='seed for randomization')
    args = parser.parse_args()
    random.seed(args.random_seed)

    # Low resource Split
    # sample_data_by_sampling(args.input_path, args.output_folder, args.num_sample_events, rs=args.random_seed)
    
    # Few shot Split
    # sample_data_by_sampling(args.input_path, args.output_folder, args.num_sample_events, sampling_method="uniform", rs=args.random_seed)

    # Zero shot Split
    # sample_data_by_events(args.input_path, args.output_folder, num_sample_events=args.num_sample_events, num_sample_datapoints=565)
    
    # CTT Split
    # SCENARIO_LIST = ["Emergency", "Achieve", "Competition", "Resolve_problem", "Rite", "Catastrophe", "Confronting_problem", "Process_start", "Process_end"]
    # sample_data_by_events(args.input_path, args.output_folder, event_list=SCENARIO_LIST)
    
