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

Install the package
```bash
$ pip install .
```

To scan through data and save statistics, edit the parameters in
`./scripts/generate_file_stats_results.py` and run
```bash
$ python3 scripts/generate_file_stats_results.py
```

After generating stats, generate a coverage bar plot using
```bash
$ python3 scripts/plot_coverage_bars.py
```

After generating stats, generate a coverage timeline plot using
```bash
$ python3 scripts/plot_coverage_timelines.py
```
