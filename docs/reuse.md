# Reuse
The reuse command is intended to allow users to attach mappings from their [currated mappings file](reusable_mappings.md#Mappings-Format) to terms that are present in a MapDragon table. While the mapping used can come from any source, they should use the schema defined in the link provided above. 

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

For more information, please see the overview for [reusable mappings](reusable_mappings.md)
