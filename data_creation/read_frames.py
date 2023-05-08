import os
import argparse
import xml.etree.ElementTree as ET
import regex as re

# const_prefix = "{http://framenet.icsi.berkeley.edu}"

def get_frames_dict(frame_files, non_core=False, description=False):

    def clean_description(description):
        description = re.sub(r'\<(.*?)\>', '', description)         # Remove XLM encodings
        description = description.split("\n")[0]                    # Consider only description and no example
        return description

    def get_frame_info(frame_file):
        frame_info = {}
        tree = ET.parse(frame_file)
        for e in tree.iter():

            if e.tag.split("}")[1] == "frame":     # frame
                frame_info["name"] = e.attrib["name"]
                frame_info["id"] = e.attrib["ID"]
                if description:
                    assert e[0].tag.split("}")[1] == "definition", e[0]
                    frame_info["description"] = clean_description(e[0].text)
                frame_info["fe"] = []
                frame_info["nc_fe"] = []

            elif e.tag.split("}")[1] == "FE":      # frame element (or event arguments)
                if e.attrib["coreType"].lower() == "core":      # core FE
                    frame_element = {
                        "name": e.attrib["name"],
                        "id": e.attrib["ID"]
                    }
                    if description:
                        assert e[0].tag.split("}")[1] == "definition", e[0]
                        frame_element["description"] = clean_description(e[0].text)
                    frame_info["fe"].append(frame_element)
                elif non_core:
                    frame_element = {
                        "name": e.attrib["name"],
                        "id": e.attrib["ID"]
                    }
                    if description:
                        assert e[0].tag.split("}")[1] == "definition"
                        frame_element["description"] = clean_description(e[0].text)
                    frame_info["nc_fe"].append(frame_element)
                    
        return frame_info

    frames_dict = {}
    for f in frame_files:
        if not f.endswith(".xml"):
            continue
        f_info = get_frame_info(f)
        frames_dict[f_info["name"]] = f_info
    return frames_dict

def get_all_files(folder_path):
    return [ os.path.join(folder_path,f) for f in os.listdir(folder_path) 
            if os.path.isfile(os.path.join(folder_path, f)) ]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Read frame(s) data')
    parser.add_argument('frames_folder', type=str,
                        help='path to the input folder to read frame files')
    args = parser.parse_args()
    
    frame_files = get_all_files(args.frames_folder)
    frames_dict = get_frames_dict(frame_files)