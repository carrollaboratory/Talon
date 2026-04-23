# Sideload Command
Sideload provides MapDragon users with the ability to load mappings into their tables and enumerations via the command line. The process requires a properly defined CSV file. 

## Sideload Options
| Flags | Type/options | Description | Default |
| ----- | ------------ | ----------- | ------- |
| -e --editor | {your email address} | The user submitting the job (required) | | 
| mappings | {1 or more csv files} | 1 or more CSV files that conform to the sideload format | |

## File Format

| Column Name | Description | Required Y/N | Comment |
| ----------- | ----------- | ------------ | ------- |
| table_id    | This is the ID inside locutus where the source data can be found. | Y | |
| source_variable | Variable code or name from source table | Y | |
| source_enumeration | If mapping to value from an enumeration, this will be that enum value | N | Only required for enums, otherwise, it can be blank |
| code | The code from the external ontology | Y | |
| display | The human friendly text associated with the code | Y | |
| system | The system associated with the public ontology | Y | |
| mapping_relationship | N | Relationship of the mapped term to the source term | equivalent, source-is-narrower-than-target, source-is-broader-than-target | 
| provenance | The email or app name to attribute inside provenance | Y | |
| comment | This is not used by locutus but may be helpful for tracking on the user's end | N| |
