# Refresh

The refresh command provides the ability to pull terms down from an instance of
MD into a local CSV on the user's laptop to enable the user to curate mappings
for reuse. While the term 'refresh' suggests it only updates an existing set of
mappings, it will also create the baseline mappings file as well.

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

During the first run for a given "project directory", the mappings file is
created and reflects all mappings identified in the requested Studies, Data
Dictionaries and Tables. Subsequent "refreshes" will add new mappings found.
Where mapped codes match but are otherwise different, entries will be added to
the errors.yaml file inside the specified "project directory".

For more information, please see the overview for
[reusable mappings](reusable_mappings.md)

# Example Run

## Create New Project

The first time through, the user will use the refresh command to create a new
project, based on the contents from any combination of map-dragon Studies, Data
Dictionaries and Tables. Users can pull from as many different MapDragon sites
and resources as is appropriate for their needs. However, the first entry for
any given term/mapping is the one that is kept.

Also, users should be aware that if a term/mapping is ignored, it will always be
ignored even if the data comes from a different study, data-dictionary, table or
site.

```bash
$ talon --host gcp-alpha refresh -p my-mappings -dd dd-3AIOwTnNCKNvT7WBKVMml
INFO     GET: https://mapdragon-456608912345.us-central1.run.app/api/harmony?format=FTD&datadictionaries=dd-3AIOwTnNCKNvT7WBKVMml   __init__.py:31
Rows Added: 74
Confict Count: 0

$ wc -l my-mappings/mappings.csv
75 my-mappings/mappings.csv

$ head my-mappings/mappings.csv
source_text,mapped_code,mapped_display,mapped_system,mapping_relationship,ignore
consanguinity,SNOMED:842009,Consanguinity,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,equivalent,False
consanguinity_detail,SNOMED:842009,Consanguinity,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
family_history_detail,SNOMED:422432008,Family history section,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,equivalent,False
pedigree_file,SNOMED:12953007,File,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
pedigree_file_detail,SNOMED:224093006,Details of family,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
Unknown,SNOMED:261665006,Unknown,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,,False
proband_relationship,SNOMED:263498003,Relationship,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
proband_relationship_detail,SNOMED:263498003,Relationship,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
sex,SNOMED:184100006,Patient sex,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,equivalent,False
```

The command above resulted in 74 mappings with zero conflicts. At this point,
there is a CSV ready to be "curated". Rows that are not intended to be reused
should have their "ignored" status be set to True. Additional mappings from
other resources can also be appended using different refresh calls.

For example, I would like to change those old OLS local file paths with the
correct FHIR System. To do that, I simply replaced the fields "mapped_system"
that started with "file:///nfs/production..." with the correct system,
"http://snomed.info/sct". When I do that, I will get conflicts because they will
differ from whatever is found in map-dragon:

```bash
$ talon --host gcp-alpha refresh -p my-mappings -dd dd-3AIOwTnNCKNvT7WBKVMml
INFO     GET: https://mapdragon-456608912345.us-central1.run.app/api/harmony?format=FTD&datadictionaries=dd-3AIOwTnNCKNvT7WBKVMml                                        __init__.py:31
Rows Added: 0
Confict Count: 53

$ head my-mappings/errors.yaml
new_rows_added: 0
conflicts_found: 53
detailed_conflicts:
- mapped_system:
    CSV Value: http://snomed.info/sct
    MD Value: file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl
    MD Line: consanguinity,SNOMED:842009,Consanguinity,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,equivalent,False
- mapped_system:
    CSV Value: http://snomed.info/sct
    MD Value: file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl
```

Notice that the CSV still reflects the edits made prior to refresh. This is the
desired behavior, since the local file represents the curated, gold standard
values. The errors do note that the value inside map-dragon differ, but but
refuses to replace the values that current exist.

For situations where the user prefers what is current in MapDragon, they must
grab the value from the MD Line: and replace the existing line since there is
currently no way to automate merging in conflicts.
