# eCommons ETDs to DOIs

## Goal

We want to take eCommons handles and metadata - in particular, for electronic dissertations and theses - once loaded, use the handles and basic eCommons metadata to generate DOIs using the [EZID DOI API](http://ezid.cdlib.org/doc/apidoc.html#python-example), then push those DOIs back into the dc.identifier.doi metadata field in eCommons.

Eventually, this will be migrated into the ETDs processing workflow as an automatic post-processing/post-ingest enhancement step.

## How to Use

```$ python etddoi.py -d '2016-01' 1813-47.csv ```

## Overall Workflow

Currently expected to run locally. Will eventually move this to metasrv most likely for inclusion in the ETDs workflows.

### 1. Grab eCommons ETDs metadata for specific cycle

- Log into eCommons, export collection CSV from https://ecommons.cornell.edu/handle/1813/47
- Move CSV export into working directory.
- Manually review if/as needed.

To be done: automate this step.

### 2. Prepare/Queue CSV metadata for DOI generation

- Remove rows not in selected date range or conferral cycle.
- Verify DOIs do not already exist in CSV export selection.
- Remove fields not to be used in generation of DOI or eCommons update (see mapping)

### 3. DOI generation part 1: EZID Metadata Files Creation

- Create subdirectory for job to store EZID Metadata .txt files following example given
- Create new text file with ANVL metadata added for each row in eCommons CSV / each eCommons handle. Store in subdirectory

### 4. DOI generation part 2: EZID Creation and Capture

- Run ezid.py script for each eCommons handle to mint DOI and use metadata in related text ANVL file.
- If successful, capture handle and doi in output.csv (output of this ezid.py creation command should be along the lines of 'doi:10.5072/FK2XK89N0Q | ark:/b5072/fk2xk89n0q')
- If unsuccessful, stop script and write out error to CLI for review.
- how to determine DOI generation here?

### 5. Update eCommons

- Manually review (look over briefly) of the output.csv
- Should have handle (dc.identifier.uri) , DOI (dc.identifier.doi), mapped back to eCommons columns/fields
- Send output.csv to eCommons staff for batch update.

## Moving Parts


## Details from Wendy
DOIscript.sh – run this to generate DOIs from EZID. Need to edit so that in addition to writing generated DOI to the txt files, it makes (or appends to old) a csv of the new dois that we can just batch upload back into eCommons
Ezid.py – DOIscript.sh calls this
201605_ETDList_ForDOIs.csv – the list of info that needs to be converted to txt files
201605_TestDOIMetadata.txt – sample of the format needed as input for the DOI API
