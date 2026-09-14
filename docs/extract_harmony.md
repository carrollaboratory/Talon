# Extract Harmony

Users can extract harmony files using talon's command, 'extract-harmony'. This
allows integration with script based pipelines and automations.

The harmony files generated can be based on any combination of the following
ids:

- Study ID
- Data Dictionary ID
- Table ID

Users can provide as many of any of those IDs in any combination.

The chosen format,
[Whistle](https://nih-ncpi.github.io/locutus/#/harmony?id=whistle) or
[FTD](https://nih-ncpi.github.io/locutus/#/harmony?id=ftd) allows these harmony
files to integrate with our Whistler application or with the scripts used in the
dbt-pipeline and indicates which format the data will be written in.

```bash
$ talon --host gcp-alpha extract-harmony -h
usage: talon extract-harmony [-h] [--replace] [-s STUDY_ID] [-dd DATA_DICTIONARY_ID] [-t TABLE_ID] [-f {Whistle,FTD}] mappings

positional arguments:
  mappings              CSV file to be written to. Leave blank to write to stdout

options:
  -h, --help            show this help message and exit
  --replace             When writing to file, --replace will replace any existing content. Otherwise, it will be merged in along with the existing values
  -s, --study-id STUDY_ID
                        Pull all harmony for one or more studies (you may add more than one of these arguments to a single run)
  -dd, --data-dictionary-id DATA_DICTIONARY_ID
                        Pull all harmony for one or more data dictionaries (you may add more than one of these arguments to a single run)
  -t, --table-id TABLE_ID
                        Pull all harmony for one or more tables (you may add more than one of these arguments to a single run)
  -f, --format {Whistle,FTD}
                        Column structure may vary based on the formatting choice.
```
