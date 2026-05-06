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
