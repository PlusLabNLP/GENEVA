import json
import argparse
from collections import OrderedDict, Counter

from read_frames import get_all_files, get_frames_dict

def read_frames_from_file(folder_name):
    frame_files = get_all_files(folder_name)
    frames_dict = get_frames_dict(frame_files, non_core=True, description=True)
    return frames_dict

def get_arg_mappings(frames_dict):
    id2args = {}
    args2id = {}
    for f in frames_dict:
        for arg in frames_dict[f]['fe']:
            arg_name = frames_dict[f]['name'] + "." + arg['name']
            id2args[arg['id']] = arg_name
            args2id[arg_name] = arg['id']
        if 'nc_fe' in frames_dict[f]:
            for arg in frames_dict[f]['nc_fe']:
                arg_name = frames_dict[f]['name'] + "." + arg['name']
                id2args[arg['id']] = arg_name
                args2id[arg_name] = arg['id']
    return id2args, args2id

def read_annotations(filename, frames_dict, args2id):

    fn2geneva_args, id2args_geneva = {}, {}
    event_ontology = {}

    def read_frame(fields):
        frame_name, frame_desc = fields[1], fields[4]
        assert frame_name != ""
        assert frame_desc != ""
        assert frame_name in frames_dict
        return frame_name, frames_dict[frame_name]["id"], frame_desc

    def read_fe(fields, event_name, frame_name):
        is_core, fe_name, fe_desc = fields[2], fields[3], fields[4]
        assert is_core in ["Core", "Non-Core"]
        is_core = is_core == "Core"
        assert fe_name != ""
        assert fields[5] == "", fields

        is_arg, merged_fe, is_entity = fields[6], fields[7], fields[8]
        assert is_arg != "", (fields, frame_name)
        is_arg = int(is_arg)

        if is_arg == 0:
            arg_obj = {
                "is_core": is_core
            }
            return 0, arg_obj
        elif is_arg == 1:
            assert is_entity != ""
            arg_id = frame_name + "." + fe_name
            arg_id = args2id[arg_id]
            arg_obj = {
                "arg_name": fe_name,
                "arg_id": arg_id,
                "arg_desc": fe_desc,
                "is_core": is_core,
                "is_entity": bool(int(is_entity))
            }
            fn2geneva_args[arg_id] = arg_id
            id2args_geneva[arg_id] = event_name + "." + fe_name
            return 1, arg_obj
        elif is_arg == 2:
            assert False, "is_arg can't be 2"
        elif is_arg == 3:
            assert merged_fe != ""
            arg_id = frame_name + "." + fe_name
            arg_id = args2id[arg_id]
            arg_obj = {
                "arg_name": fe_name,
                "arg_id": arg_id,
                "is_core": is_core,
                "merged_fe_name": merged_fe
            }
            return 3, arg_obj
        else:
            raise NotImplementedError()            

    total_fes, filtered_fes, merged_fes, total_args = 0, 0, 0, 0
    core_fes, core_args, noncore_args = 0, 0, 0
    entity_args = 0
    total_unique_args, entity_unique_args = 0, 0
    
    with open(filename, 'r') as f:
        prev_event = 0
        header = 1
        for line in f:

            if header:
                header = 0
                continue

            fields = line.split("\t")

            # Check if line has new event
            if fields[0] != "":
                if prev_event:
                    # Save old data
                    matched_frame = next(iter(event_info["frames"]))
                    for frame in event_info["frames"]:
                        if frame == event_name:
                            matched_frame = frame
                    event_info["description"] = event_info["frames"][matched_frame]["description"]
                    for fe in merge_frame_elements:
                        merged_fe_name = merge_frame_elements[fe]["merged_fe_name"]
                        assert merged_fe_name in event_info["arguments"], (merged_fe_name, fe, matched_frame)
                        fn2geneva_args[merge_frame_elements[fe]["arg_id"]] = event_info["arguments"][merged_fe_name]["arg_id"]
                
                    event_ontology[event_name] = event_info

                # Create new event
                prev_event = 1
                event_name = fields[0]
                event_info = {"frames": OrderedDict(), "arguments": {}, "description": ""}
                merge_frame_elements = {}
                frame_name, frame_id, frame_desc = read_frame(fields)
                event_info["frames"][frame_name] = {"id": frame_id, "description": frame_desc}
        
            # Check if line has new frame
            elif fields[1] != "":
                frame_name, frame_id, frame_desc = read_frame(fields)
                event_info["frames"][frame_name] = {"id": frame_id, "description": frame_desc}

            # Check if line has frame element
            else:
                is_arg, arg_obj = read_fe(fields, event_name, frame_name)
                total_fes += 1
                if is_arg == 0:
                    filtered_fes += 1
                    if arg_obj["is_core"]:
                        core_fes += 1
                elif is_arg == 1:
                    event_info["arguments"][arg_obj["arg_name"]] = arg_obj
                    if arg_obj["is_core"]:
                        core_fes += 1
                        core_args += 1
                    else:
                        noncore_args += 1
                    if arg_obj["is_entity"]:
                        entity_args += 1
                    total_args += 1
                elif is_arg == 3:
                    merge_frame_elements[frame_name + "." + arg_obj["arg_name"]] = arg_obj
                    if arg_obj["is_core"]:
                        core_fes += 1
                        core_args += 1
                    else:
                        noncore_args += 1
                    merged_fes += 1
        
        # Save old data
        matched_frame = next(iter(event_info["frames"]))
        for frame in event_info["frames"]:
            if frame == event_name:
                matched_frame = frame
        event_info["description"] = event_info["frames"][matched_frame]["description"]
        for fe in merge_frame_elements:
            merged_fe_name = merge_frame_elements[fe]["merged_fe_name"]
            assert merged_fe_name in event_info["arguments"]
            fn2geneva_args[merge_frame_elements[fe]["arg_id"]] = event_info["arguments"][merged_fe_name]["arg_id"]
        event_ontology[event_name] = event_info

        unique_args = []
        for event in event_ontology:
            unique_args += list(event_ontology[event]["arguments"])
        unique_args = list(set(unique_args))

        # Print statistics
        print ("Total FEs filtered: %d/%d : %.2f" % (filtered_fes, total_fes, float(filtered_fes)/total_fes * 100))
        print ("Total FEs merged: %d/%d : %.2f" % (merged_fes, total_fes, float(merged_fes)/total_fes * 100))
        print ("Total FEs as args: %d/%d : %.2f" % (total_args, total_fes, float(total_args)/total_fes * 100))
        
        print ("Total Core FEs: %d/%d : %.2f" % (core_fes, total_fes, float(core_fes)/total_fes * 100))
        print ("Total Core FEs as args: %d/%d : %.2f" % (core_args, core_fes, float(core_args)/core_fes * 100))
        print ("Total args which are Non Core FEs: %d/%d : %.2f" % (noncore_args, total_args+merged_fes, float(noncore_args)/(total_args+merged_fes) * 100))

        print ("Total args which are entities: %d/%d : %.2f" % (entity_args, total_args, float(entity_args)/total_args * 100))

        print ("Total unique args: %d" % len(unique_args))
        print ("-"*20)

    return event_ontology, fn2geneva_args, id2args_geneva

def create_dataset(input_filename, output_filename, frame_mapping, arg_mapping, args2id, id2args):
    new_event_counter = Counter()
    total_datapoints = 0
    with open(input_filename, 'r') as in_file, open(output_filename, 'w') as out_file:
        for line in in_file:
            in_example = json.loads(line)
            event_mentions = in_example["event_mentions"]
            new_event_mentions = []
            for event_mention in event_mentions:
                event_type = event_mention["event_type"]
                if event_type in frame_mapping:
                    new_event_type = frame_mapping[event_type]
                    new_args = []
                    for arg in event_mention["arguments"]:
                        assert event_type + "." + arg["role"] in args2id
                        arg_id = args2id[event_type + "." + arg["role"]]
                        if arg_id in arg_mapping:
                            new_arg_name = id2args[arg_mapping[arg_id]].split(".")[-1]
                            new_args.append({
                                "entity_id": arg["entity_id"],
                                "text": arg["text"],
                                "role": new_arg_name
                            })
                    new_event = {
                        "id": event_mention["id"],
                        "event_type": new_event_type,
                        "trigger": event_mention["trigger"],
                        "arguments": new_args
                    }
                    new_event_mentions.append(new_event)
                    new_event_counter[new_event_type] += 1
            in_example["event_mentions"] = new_event_mentions
            out_line = json.dumps(in_example)
            out_file.write(out_line + "\n")
            total_datapoints += 1
    
    print ("Total datapoints: %d" % total_datapoints)
    print ("Total final event types: %d" % len(new_event_counter))
    return new_event_counter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read the human annotated excel files and convert to json')
    parser.add_argument('-a', '--ann-file', type=str,
                        help='path to the annotation file which is tsv')
    parser.add_argument('-f', '--frames_folder', type=str,
                        help='path to the input folder to read frame files')
    parser.add_argument('-i', '--input-file', type=str,
                        help='path to the input data file')
    parser.add_argument('-o', '--output-file', type=str,
                        help='path to the output data file')
    parser.add_argument('-d', '--output-dir', type=str,
                        help='path to the output directory for saving meta file')
    args = parser.parse_args()
    
    frames_folder = args.frames_folder
    frames_dict = read_frames_from_file(frames_folder)

    id2args, args2id = get_arg_mappings(frames_dict)

    event_ontology, fn2geneva_args, id2args_geneva = read_annotations(args.ann_file, frames_dict, args2id)
    fn2geneva_frame_mapping = {}
    for event in event_ontology:
        for frame in event_ontology[event]["frames"]:
            fn2geneva_frame_mapping[frame] = event

    print ("Number of events: ", len(event_ontology))
    print ("Number of frames: ", len(fn2geneva_frame_mapping))
    print ("Average number of arguments per event: ", sum([len(event_ontology[e]["arguments"]) for e in event_ontology]) / len(event_ontology))

    with open("%s/event_ontology.json" % args.output_dir, 'w') as fp:
        json.dump(event_ontology, fp)
    with open("%s/fn2geneva_args.json" % args.output_dir, 'w') as fp:
        json.dump(fn2geneva_args, fp)
    with open("%s/id2args_geneva.json" % args.output_dir, 'w') as fp:
        json.dump(id2args_geneva, fp)
    
    entity_map = {}
    for event in event_ontology:
        for arg in event_ontology[event]["arguments"]:
            entity_map[event + "," + arg] = "entity" if event_ontology[event]["arguments"][arg]["is_entity"] else "non-entity"
    with open("%s/entity_map.json" % args.output_dir, 'w') as fp:
        json.dump(entity_map, fp)
    
    # Return event counts if any statistics need to be calculated
    event_counts = create_dataset(args.input_file, args.output_file, fn2geneva_frame_mapping, fn2geneva_args, args2id, id2args)
    