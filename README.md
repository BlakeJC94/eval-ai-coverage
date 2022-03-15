# eval-ai-coverage

Python package to compute statistics about the eval.ai dataset.

## Usage

Create a softlink to the dataset:

```bash
$ ln -s <path-to-eval-al-data> ./edf
```

Expected file structure in `path-to-eval-al-data`:
```
  edf/1110/
  ├── testing
  │   ├── 1588104564
  │   │   ├── Empatica-ACC.edf
  │   │   ├── Empatica-BVP.edf
  │   │   ├── Empatica-EDA.edf
  │   │   ├── Empatica-HR.edf
  │   │   └── Empatica-TEMP.edf
  │   ...
  └── training
      ├── 1582758851
      │   ├── Empatica-ACC.edf
      │   ├── Empatica-BVP.edf
      │   ├── Empatica-EDA.edf
      │   ├── Empatica-HR.edf
      │   └── Empatica-TEMP.edf
      ...
```

Set parameters in `sweep.py` and then run

```bash
$ python3 sweep.py
```

To run a test with sample data, simply run `main.py`,

```bash
$ python3 main.py
```
