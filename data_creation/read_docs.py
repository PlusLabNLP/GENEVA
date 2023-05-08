import argparse
import xml.etree.ElementTree as ET
from pprint import pprint

from read_frames import get_all_files, get_frames_dict

def get_tag(element):
    return element.tag.split("}")[1]

def get_docs_dict(doc_files, frames_dict):

    def get_doc_dict(doc_file):
        doc_info = {}
        tree = ET.parse(doc_file)
        for e in tree.iter():

            if get_tag(e) == "corpus":         # corpus
                doc_info["corpus_name"] = e.attrib["name"]
                doc_info["corpus_id"] = e.attrib["ID"]

            elif get_tag(e) == "document":     # document
                doc_info["doc_name"] = e.attrib["name"]
                doc_info["doc_id"] = e.attrib["ID"]
                doc_info["sentences"] = []
                
            elif get_tag(e) == "sentence":     # sentence
                sent_info = {
                    "sent_id": "_".join([e.attrib["corpID"], e.attrib["docID"], e.attrib["ID"]]),
                    "annotations": []
                    }
                for s in e.iter():
                    
                    if get_tag(s) == "text":    # text
                        sent_info["text"] = s.text
                    elif get_tag(s) == "annotationSet" and "luID" in s.attrib:     # annotation with lexical unit
                        ann_info = {
                            "lu_id": s.attrib["luID"],
                            "lu_name": s.attrib["luName"],
                            "frame_id": s.attrib["frameID"],
                            "frame_name": s.attrib["frameName"],
                            "frame_elements": []
                        }
                        core_fe_list = [ f['id'] for f in frames_dict[ ann_info["frame_name"] ]["fe"] + frames_dict[ ann_info["frame_name"] ]["nc_fe"] ] 

                        for a in s.iter():
                            if get_tag(a) == "label" and a.attrib["name"] == "Target":      # lexical unit info
                                ann_info["lu_start"] = int(a.attrib["start"])
                                ann_info["lu_end"] = int(a.attrib["end"])
                            elif get_tag(a) == "label" and "feID" in a.attrib:              # frame elements
                                if "itype" in a.attrib:
                                    continue
                                elif a.attrib["feID"] not in core_fe_list:
                                    continue

                                fe_info = {
                                    "fe_id": a.attrib["feID"],
                                    "fe_name": a.attrib["name"],
                                    "fe_start": int(a.attrib["start"]),
                                    "fe_end": int(a.attrib["end"])
                                }
                                ann_info["frame_elements"].append(fe_info)

                        # Ensure lexical unit have start and end defined
                        assert "lu_start" in ann_info, (ann_info)

                        sent_info["annotations"].append(ann_info)
                doc_info["sentences"].append(sent_info)
        
        return doc_info
                    
    docs_list = []
    for d in doc_files:
        if not d.endswith(".xml"):
            continue
        d_info = get_doc_dict(d)
        docs_list.append(d_info)
    
    return docs_list

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Read doc(s) data')
    parser.add_argument('docs_folder', type=str,
                        help='path to the input folder to read doc files')
    parser.add_argument('frames_folder', type=str,
                        help='path to the input folder to read frame files')
    args = parser.parse_args()

    frame_files = get_all_files(args.frames_folder)
    doc_files = get_all_files(args.docs_folder)
    frames_dict = get_frames_dict(frame_files, non_core=True)
    docs_dict = get_docs_dict(doc_files, frames_dict)