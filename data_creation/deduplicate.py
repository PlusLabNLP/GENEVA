import argparse
import json

def deduplicate(input_filename, output_filename):

    with open(input_filename, 'r') as in_file, open(output_filename, 'w') as out_file:
        for line in in_file:
            in_example = json.loads(line)
            example_id = in_example["wnd_id"]
            event_mentions = in_example["event_mentions"]
            new_event_mentions = []
            
            done_examples_id = []
            for e1 in event_mentions:
                if e1['id'] in done_examples_id:
                    continue
                    
                affected = 0
                copy_events = [e1]
                for e2 in event_mentions:
                    if e1['id'] == e2['id']:
                        continue
                    if e1["event_type"] == e2["event_type"] and e1["trigger"] == e2["trigger"]:
                        affected = 1
                        copy_events.append(e2)
                
                if affected == 0:
                    new_event_mentions.append(e1)
                    done_examples_id.append(e1['id'])
                    
                else:                
                    new_event = {}
                    new_event["id"] = "_".join(e1["id"].split("_")[:-1])
                    new_event["id"] += "_m_" + "_".join([ e['id'].split("_")[-1] for e in copy_events ])
                    new_event["event_type"] = e1["event_type"]
                    new_event["trigger"] = e1["trigger"]
                    new_event["arguments"] = []
                    for e in copy_events:
                        new_event["arguments"] += e1["arguments"]
                    new_event["arguments"] = [dict(t) for t in {tuple(d.items()) for d in new_event["arguments"]}]
                    new_event_mentions.append(new_event)
                    
                    for e in copy_events:
                        assert e['id'] not in done_examples_id
                        done_examples_id.append(e['id'])
                    
            in_example["event_mentions"] = new_event_mentions
            out_file.write(json.dumps(in_example) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Filter the processed Framenet data based on frames')
    parser.add_argument('-i', '--input-file', type=str,
                        help='path to the input file/processed frames data')
    parser.add_argument('-o', '--output-file', type=str,
                        help='path file for saving output file/filtered frames data')
    args = parser.parse_args()

    deduplicate(args.input_file, args.output_file)