# GENEVA: Benchmarking Generalizability for Event Argument Extraction with Hundreds of Event Types and Argument Roles

Code for the ACL-2023 paper [GENEVA: Benchmarking Generalizability for Event Argument Extraction with Hundreds of Event Types and Argument Roles](https://arxiv.org/abs/2205.12505)

## Environment Details

You can setup a conda environment using the `environment.yml` file. The `Python` version used is `3.8.12`
```
conda env create -f environment.yml
```

## Data

You can access the original GENEVA data in the data folder. Below we provide a brief structure of the directory below

```
data
├── lr                              # Low Resource Test Suite
│    ├── lr10                       # 10 Training Instances
│    │    ├── train-s100.json       # Seed 100
│    │    ├── train-s101.json       # Seed 101
│    │    └── ...
│    ├── lr25                       # 25 Training Instances
│    ├── lr50                       # 50 Training Instances
│    └── ...
├── fs                              # Few Shot Test Suite
│    ├── fs1                        # 1 Training Instances per Event
│    │    ├── train-s200.json       # Seed 200
│    │    ├── train-s201.json       # Seed 201
│    │    └── ...
│    ├── fs2                        # 2 Training Instances per Event
│    ├── fs3                        # 3 Training Instances per Event
│    └── ...
├── zs                              # Zero-shot Test Suite
│    ├── zs1-s300                   # Train on 1 event - Seed 300
│    │    ├── train.json            # Train file
│    │    ├── dev.json              # Dev file
│    │    └── test.json             # Test file
│    ├── zs1-s301                   # Train on 1 event - Seed 301
│    ├── ...
│    ├── zs5-s310                   # Train on 5 events - Seed 310
│    ├── zs5-s311                   # Train on 5 events - Seed 311
│    ├── ...
│    ├── zs10-s310                  # Train on 10 events - Seed 320
│    ├── zs10-s311                  # Train on 10 events - Seed 321
│    └── ...
├── ctt                             # Cross-Type Transfer Suite
│    ├── scenario-s400              # Train on scenario events - Seed 400
│    │    ├── train.json            # Train file
│    │    ├── dev.json              # Dev file
│    │    └── test.json             # Test file
│    ├── scenario-s401              # Train on scenario events - Seed 401
│    └── ...
├── train.json                      # Main Train File
├── val.json                        # Main Validation File
└── test.json                       # Main Test File
```

The main splits of train/val/test are provided in the root directory. The splits for each benchmarking test suite are provided in their respective folders (along with the random seeds). For more details of each test suite, please refer to the paper.

The format of the data follows OneIE and we provide an example here. Note that the list of entities is not exhaustive and you have to run a separate entity extractor if you are using that information.
```
{
    "doc_id": "ABC",                                    # Document ID
"wnd_id": "ABC_XX",                                     # Sentence ID (unique to each line)
    "sentence": "Obama was born in 1961",               # Actual Input Sentence
    "tokens": ["Obama", "was", "born", "in", "1961"],   # Tokenized form of the sentence
    "sentence_starts": [0],                             # Starting token in the document
    "entity_mentions": [                                # List of entities (not exhaustive)
        {"id": "ABC_XX_0_1", "start": 0, "end": 1, "text": "Obama"},
        {"id": "ABC_XX_4_5", "start": 4, "end": 5, "text": "1961"}
    ],
    "event_mentions": [                                 # List of event mentions
        {
            "id": "ABC_XX_YY_0",                        # Event ID
            "event_type": "Be_Born",                    # Event Type
            "trigger": {"start": 2, "end": 3, "text": "born"},  # Trigger word
            "arguments": [                              # List of arguments
                {"entity_id": "ABC_XX_0_1", "text": "Obama", "role": "Person"}, 
                {"entity_id": "ABC_XX_4_5", "text": "1961", "role": "Time"}
            ]
        }
    ]
}

```

### Data with Time and Place

The original data doesn't comprise `Time` and `Place` argument roles for most events owing to the original MUC definition that we follow. We provide data with the same splits but with `Time` and `Place` arguments in the `data_time_place` folder.

## Data Creation

We provide the code and detailed steps for creating the data in the `data_creation` folder. Necessary files for data creation are stored in the `meta_data` folder. These files include

- `geneva-frames.txt`: Comprises all FrameNet frames used in the MAVEN ontology.
- `fn2geneva_mapping_annotations`: Comprises human annotations for mapping frames to events and frame elements to event argument roles.

## Citation

If you use this data or find our work useful in your research, please cite our paper.

    @inproceedings{parekh2023geneva,
        title={GENEVA: Benchmarking Generalizability for Event Argument Extraction with Hundreds of Event Types and Argument Roles},
        author={Tanmay Parekh and I-Hung Hsu and Kuan-Hao Huang and Kai-Wei Chang and Nanyun Peng},
        booktitle={Proceedings of the Conference of the 61st Annual Meeting of the Association for Computational Linguistics (ACL)},
        year={2023},
    }

Since our data is derived from FrameNet, please cite FrameNet as well in your work

    @inproceedings{baker1998berkeley,
        title={The berkeley framenet project},
        author={Baker, Collin F and Fillmore, Charles J and Lowe, John B},
        booktitle={COLING 1998 Volume 1: The 17th International Conference on Computational Linguistics},
        year={1998}
}

## License

GENEVA data uses FrameNet data and is licensed under a [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/)

## Contact

If you have any issues, please contact Tanmay Parekh (tparekh@g.ucla.edu)
