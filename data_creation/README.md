# Data Creation

This folder comprises steps to create the data from FrameNet to GENEVA. You can modify specific steps to build a custom data according to your requirements.

## Download FrameNet data

You have to first download the FrameNet data. You can request for this data here - [Request FrameNet Data](https://framenet.icsi.berkeley.edu/fndrupal/framenet_request_data). We use the version 1.7 of this data for creating GENEVA and save it in this folder as `fndata-1.7`.

## Conversion to EE format

The FrameNet data, by default, is in the XML format. We first convert it into a Event Extraction (EE) format in form of a JSON file as used by OneIE.

```
python preprocess.py -t fndata-1.7/fulltext -f fndata-1.7/frame -o ../meta_data/all_framenet_data.json
```
where
* `t` - path to the folder to read text files of the different documents in FrameNet (fulltext)
* `f` - path to the folder to read frame files of FrameNet (frame)
* `o` - output file for saving EE format json file

Note that some sentences had parsing errors and they were manually corrected.

## Filter Frames and Data

Since our EAE ontology doesn't comprise of all the frames in FrameNet, we use the sampled set of frames to filter the data.

```
python filter_frames.py -i ../meta_data/all_framenet_data.json -o ../meta_data/filtered_geneva_data.json -f ../meta_data/geneva-frames.txt
```
where
* `i` - input EE format json file from FrameNet
* `o` - output file for saving EE format json file for the filtered data
* `f` - text file comprising of frame names to filter. For your custom filtering, you can modify this file

Note that we manually correct a couple of examples which had parsing error

## Map Frames to Events for GENEVA

Next, we map the frames and frame elements from FrameNet to events and argument roles for GENEVA. The mapping has been generated through human expert annotation.

```
python create_dataset_from_annotations.py -a ../meta_data/fn2geneva_mapping_annotations.tsv -f fndata-1.7/frame -i ../meta_data/filtered_geneva_data.json -o ../meta_data/filtered_geneva_mapped_data.json -d ../meta_data
```
where
* `a` - path to the human annotated FrameNet to GENEVA mapping. You can modify this file based on your requirements
* `f` - path to the folder to read frame files of FrameNet (frame)
* `i` - input EE format json file
* `o` - output file for saving EE format json file for the mapped data
* `d` - output directory for saving metadata about the FrameNet to GENEVA mapping

Note that we manually correct a couple of examples which had parsing error

## Deduplication

We execute some checks and steps to ensure deduplication of examples and event mentions in our data.

```
python deduplicate.py -i ../meta_data/filtered_geneva_mapped_data.json -o ../meta_data/final_filtered_geneva_mapped_cleaned_data.json
```
* `i` - input EE format json file
* `o` - output file for saving EE format json file for the cleaned and deduplicated data

## Data Split

We use the following script to split the data into train/val/test. We ensure that the test comprises at least 5 event mentions for each event and a minimum of 10% of the total data. You can alter these ratios in the hyperparameters of the script

```
python split_data.py -i ../meta_data/final_filtered_geneva_mapped_cleaned_data.json -o ../data
```

We provide our split of data currently in the data folder. If you want a different split, you can change the random seed.

## Sampling data for different benchmarks

To create different benchmarks, we sample data using different strategies. You can refer to `sample_data_scripts.sh` for the same. You need to comment out the setting you want to run in this file.