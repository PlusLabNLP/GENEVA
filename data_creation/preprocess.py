import argparse
import string
from transformers import BertTokenizer, RobertaTokenizer, AutoTokenizer
from tqdm import tqdm
import json

from read_frames import get_all_files, get_frames_dict
from read_docs import get_docs_dict

DOC_ID="doc_id"
SENT_ID="wnd_id"
TEXT="sentence"
ENTITIES="entity_mentions"
EVENTS="event_mentions"
SENT_START="sentence_starts"
TOKENS="tokens"
PIECES="pieces"
TOK_LENS="token_lens"

def tokenize(sent):
    for p in string.punctuation:
        sent = sent.replace(p, " " + p + " ")
    tokens = sent.split()
    return tokens

def get_word_for_char(sent, tokens, start_num, end_num):
    phrase_to_find = sent[start_num:end_num+1]
    tokens_to_find = tokenize(phrase_to_find)
    if tokens_to_find[0] not in tokens or tokens_to_find[-1] not in tokens:
        print ("Tokens not found in original sentence. Might be some parsing error!!! Ignoring annotation!!!")
        print (sent, tokens, tokens_to_find)
        return -1, -1
    start_token_nums = [ index for index, element in enumerate(tokens) if element == tokens_to_find[0] ]
    for s in start_token_nums:
        curr_ind = s
        max_limit = curr_ind + len(tokens_to_find)
        while tokens[curr_ind] == tokens_to_find[curr_ind - s]:
            curr_ind += 1
            if curr_ind == max_limit:
                return s, max_limit
    assert False, (sent, tokens, start_num, end_num)

def convert_ee_format(docs_dict, tokenizer):
    ee_data = []
    for doc in tqdm(docs_dict):
        doc_id = doc["corpus_id"] + "_" + doc["doc_id"]
        for sent in doc["sentences"]:
            sent_datapoint = {}
            sent_datapoint[DOC_ID] = doc_id
            sent_datapoint[SENT_ID] = sent["sent_id"]
            sent_datapoint[TEXT] = sent["text"]
            sent_datapoint[TOKENS] = tokenize(sent["text"])
            sent_datapoint[SENT_START] = [0]
            
            pieces = [ tokenizer.tokenize(t) for t in sent_datapoint[TOKENS] ]
            word_lens = [ len(p) for p in pieces ]
            pieces = [ w for p in pieces for w in p ]
            sent_datapoint[PIECES] = pieces
            sent_datapoint[TOK_LENS] = word_lens

            sent_datapoint[ENTITIES] = []
            sent_datapoint[EVENTS] = []

            for i, annot in enumerate(sent["annotations"]):
                lu_start, lu_end = get_word_for_char(sent["text"], sent_datapoint[TOKENS],
                                    annot["lu_start"], annot["lu_end"])
                if lu_start == -1 and lu_end == -1:
                    continue
                event_info = {
                    "id": sent["sent_id"] + "_" + annot["lu_id"] + "_" + str(i),
                    "event_type": annot["frame_name"],
                    "trigger": {
                        "start": lu_start,
                        "end": lu_end,
                        "text": sent["text"][annot["lu_start"]:annot["lu_end"]+1]
                    },
                    "arguments": []
                }

                for j, fe in enumerate(annot["frame_elements"]):
                    fe_start, fe_end = get_word_for_char(sent["text"], sent_datapoint[TOKENS],
                                    fe["fe_start"], fe["fe_end"])
                    entity_id = "_".join([ sent["sent_id"], str(fe_start), str(fe_end) ])
                    entity_text = sent["text"][fe["fe_start"]:fe["fe_end"]+1]
                    entity_info = {
                        "id": entity_id,
                        "start": fe_start,
                        "end": fe_end,
                        "text": entity_text
                    }
                    if len([e for e in sent_datapoint[ENTITIES] if entity_id == e["id"] ]) == 0:
                        sent_datapoint[ENTITIES].append(entity_info)

                    argument_info = {
                        "entity_id": entity_id,
                        "text": entity_text,
                        "role": fe["fe_name"]
                    }
                    event_info["arguments"].append(argument_info)
                
                sent_datapoint[EVENTS].append(event_info)
        
            ee_data.append(sent_datapoint)

    return ee_data

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Preprocess the FrameNet data to ACE/ERE format')
    parser.add_argument('-t', '--text-folder', type=str,
                        help='path to the input folder to read text files of the different documents (fulltext)')
    parser.add_argument('-f', '--frames-folder', type=str,
                        help='path to the input folder to read frame files (frame)')
    parser.add_argument('-m', '--model-name', type=str,
                        help='Model name for tokenizer', default='bert-large-cased')
    parser.add_argument('-o', '--output-file', type=str,
                        help='Output file for saving data')                    
    args = parser.parse_args()

    frame_files = get_all_files(args.frames_folder)
    doc_files = get_all_files(args.text_folder)
    frames_dict = get_frames_dict(frame_files, non_core=True)
    docs_dict = get_docs_dict(doc_files, frames_dict)

    model_name = args.model_name
    if model_name.startswith('bert-'):
        tokenizer = BertTokenizer.from_pretrained(args.model_name, do_lower_case=False)
    elif model_name.startswith('roberta-'):
        tokenizer = RobertaTokenizer.from_pretrained(args.model_name,do_lower_case=False)
    else:
        tokenizer = AutoTokenizer.from_pretrained(args.model_name, 
                            do_lower_case=False, use_fast=False)

    data = convert_ee_format(docs_dict, tokenizer)

    with open(args.output_file, 'w') as outfile:
        for entry in data:
            outfile.write(json.dumps(entry) + "\n")
