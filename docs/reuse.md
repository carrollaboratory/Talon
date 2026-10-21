# Reuse

The reuse command is intended to allow users to attach mappings from their
[curated mappings file](reusable_mappings.md#Mappings-Format) to terms that are
present in a MapDragon table. Talon provides a tool, [refresh](refresh.md) to pull/refresh a locally curated
set of mappings to be "reused" by this tool or a user can provide their own terms to attach mappings into MapDragon.

```bash
$ talon reuse -h
Usage: talon reuse [-h] [-dd DATA_DICTIONARY_ID] [-t TABLE_ID] [--fuzzy {Levenshtein,Jaro–Winkler}] [--fuzzy-threshold FUZZY_THRESHOLD] [-i] mappings

Update an existing MapDragon table or data-dictionary with terms from the curated mappings.

Positional Arguments:
  mappings              CSV file containing the curated list of mappings

Options:
  -h, --help            show this help message and exit
  -dd, --data-dictionary-id DATA_DICTIONARY_ID
                        Data dictionary ID whose tables should be updated
  -t, --table-id TABLE_ID
                        Table ID whose tables should be updated
  --fuzzy {Levenshtein,Jaro–Winkler}
                        Optionally use fuzzy matching. When matching with one of these, you can also provide a threshold. Each will have a default (see docs for more details)
  --fuzzy-threshold FUZZY_THRESHOLD
                        Threshold used in identifying matches when using one of the similarity metrics. See docs for details and defaults.
  -i, --ignore-case     When matching the **source_text** to a table's **variable name** or **enumerated value**, allow matches even if there is a difference in case.

Update either a single table or an entire data dictionary with terms from the curated mappings file. ❗Please note you should provide only one or the other for a single run.❗
```

The `reuse` command can apply mappings at the data dictionary (`-dd`) or table (`-t`) level, depending on how many 
mappings you have so you cannot specify both in one run of the command. Variable mappings and specific enumeration
mappings will come from the mapping file and only exact matches will be added.

```bash
$ head my-mappings/mappings.csv
source_text,mapped_code,mapped_display,mapped_system,mapping_relationship,ignore
consanguinity,SNOMED:842009,Consanguinity,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,equivalent,False
consanguinity_detail,SNOMED:842009,Consanguinity,file:///nfs/production/parkinso/spot/ols4/prod/local_ontologies/snomed-inferred.owl,source-is-narrower-than-target,False
```

Note that the same source text and mapping could import if there is more than one row with the same information.
For example, "Unknown" is a reasonable enumeration for multiple fields so always review MapDragon after a load
to ensure that there are proper mappings and to remove any duplicates. Another way to solve duplicate mappings
is to set the "ignore" filed in the extra mapping(s) file to `TRUE`.

For more information, please see the overview for
[reusable mappings](reusable_mappings.md)
