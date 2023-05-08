import argparse
import json
from collections import defaultdict, Counter

def filter_frames(input_file, output_file, frame_names, min_examples=10):

    frame_list = defaultdict(list)
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            datapoint = json.loads(line)
            for event in datapoint['event_mentions']:
                frame_list[event['event_type']].append(i)
    
    min_frame_list = [ (frame, frame_list[frame]) for frame in frame_names if len(frame_list[frame]) >= min_examples ]
    print ("Number of frames after min_examples (%d) filtering: %d" % (min_examples, len(min_frame_list)))

    all_sent_index = [ i for frame in min_frame_list for i in frame[1] ]
    all_frames = [ frame[0] for frame in min_frame_list ]
    
    with open(input_file, 'r') as f, open(output_file, 'w') as out:
        for i, line in enumerate(f):
            if i in all_sent_index:
                datapoint = json.loads(line)
                new_event_mentions = []
                for event in datapoint['event_mentions']:
                    if event['event_type'] in all_frames:
                        new_event_mentions.append(event)
                datapoint['event_mentions'] = new_event_mentions
                out.write(json.dumps(datapoint) + "\n")
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Filter the processed Framenet data based on frames')
    parser.add_argument('-i', '--input-file', type=str,
                        help='path to the input file/processed frames data')
    parser.add_argument('-o', '--output-file', type=str,
                        help='path file for saving output file/filtered frames data')
    parser.add_argument('-f', '--frame-names', type=str,
                        help='file with frame names to filter')
    args = parser.parse_args()

    with open(args.frame_names, 'r') as fn:
        all_frames = fn.readlines()
        all_frames = [ f.strip() for f in all_frames ]
    print ("Number of frames to filter: %d" % len(all_frames))
    filter_frames(args.input_file, args.output_file, all_frames, min_examples=10)
