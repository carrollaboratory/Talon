```bash
$ talon refresh -h
usage: talon refresh [-h] [-p PROJECT_DIR] [-s STUDY_ID] [-dd DATA_DICTIONARY_ID] [-t TABLE_ID]

Pull mapping contents from a MapDragon instance to curate a local copy of reusable mappings

options:
  -h, --help            show this help message and exit
  -p, --project-dir PROJECT_DIR
                        Directory where the curated dataset file(s) will be found.
  -s, --study-id STUDY_ID
                        Pull all harmony for one or more studies (you may add more than one of these arguments to a single run)
  -dd, --data-dictionary-id DATA_DICTIONARY_ID
                        Pull all harmony for one or more data dictionaries (you may add more than one of these arguments to a single run)
  -t, --table-id TABLE_ID
                        Pull all harmony for one or more tables (you may add more than one of these arguments to a single run)
```
