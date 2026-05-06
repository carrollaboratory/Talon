# Reusable Mappings
To leverage the use of existing annotations, we have built a simple system to 
allow users to "curate" a set of mappings to use during data-dictionary load. 
The flow is simple enough:
- The user pulls the mappings of interest down using the [refresh](refresh.md) 
  command. Data pulled can be based on any combinations of the following: 
    - study_id
    - datadictionary_id
    - table_id 
- An extra column is appended, called "ignore". When "True" is added here, those
  mappings will be ignored.
- The curator can append new mappings by rerunning the script. It will create an
  error report, 'errors.yaml' inside the project directory with any conflicts 
  identified during the pull. These have typically been related to some earlier
  pulls from OLS where the systems changed depending on the build. 
- The curator can copy the value from "MD Line" of a particular error on top of
  an existing mapping to enable that as the new currated mapping. This would 
  presumably be an updated system or display, since a change to the code would 
  result in separate mapping entry altogether.

Once the curated list is ready, a separate command can be used to load a data-
dictionary into MapDragon and any matching variable names or enumarated values 
that match the curated mapping list will be loaded with those mapping in tact. 

Any mapping that is deemed undesirable should be marked "True" under ignore 
so that subsequent refreshes won't try to add it back if it were deleted. 
Any mappings marked to be ignored will simply be ignored.

# Project Directory
When running the **refresh** command, it expects a **project** directory. This
is simply a location where all of the relevant files are written. The default
name for this directory is **curated** within the current working directory, but
can be any path name that can be written to by the user. 

## Project Files
Inside the project directory there will be a handful of files/directories:

| File/Folder | Purpose | Note | 
| ----------- | ------- | ---- | 
| mappings.csv | This file contains the curated mappings. | Users can edit this file however they wish. However, it is worth noting that Excel will lock files and the script will fail if it is still open in excel when it is trying to read or write to the file |
| errors.yaml | This is the most recent error report from the **refresh** command. | | 
| backup | This directory contains a backup of the mappings.csv file just as it was before writing any new mappings to it. | |

## Merge Conflicts 
When you pull new data from MapDragon, if a value with the same **source_text**
is found with the same **mapped_code**, it will indicate what sort of conflicts
were encountered. For instance, if the local copy had the display for a given 
mapping changed, it may show up as follows: 

```yaml
- mapped_display:
    CSV Value: Increased subcutaneous truncal adipose tissue-Updated Display
    MD Value: Increased subcutaneous truncal adipose tissue
    MD Line: adipose_subcutaneous,HP:0009003,Increased subcutaneous truncal adipose tissue,http://purl.obolibrary.org/obo/hp.owl,False
```
### Remedying Conflicts
Right now, there is no graceful mechanism for merging conflicted entries in. It
is expected to be done on a line-by-line basis by the curator. 

To do so, curators can simply grab the contents from the desired "MD Line" and 
paste over the relevant lines in the local CSV copy to officially accept a 
conflicted entry. 

# Mappings Format

| Column Name | Description | 
| ----------- | ----------- | 
| source_text | Text used to match either **variable name** or **enumerated value** in the incoming data-dictionary |
| mapped_code | The code associated with the mapped value |
| mapped_display | The display associated with the mapped value |
| mapped_system | The system associated with the mapped value |
| ignore | If the value here is True (case insensitive) the mapping will not be used |
