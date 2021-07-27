# processor-create-manifest


Takes all files in `/data/in/files` and renames the files matching the regex pattern and moves the result to `/data/out/files`. 

- All files that does not contain any match with the pattern's regular expression are left with actual name. 
- The manifest files are respected and updated accordingly.
- The pattern is applied to the filename itself, e.g. file
`/data/in/files/report.csv` is renamed from `report.csv`.
- If the replacement leads to duplicate file names, they will be overwritten.


 
 **Table of contents:**

[TOC]
   

# Configuration


## Supported parameters:

 - `pattern` --  The regular expression to match. May contain capturing groups that may be used in the replacement
 - `replacement` -- String to replace the matched file names. May contain references to capture groups if present e.g. `$0` (0-based). 
 Note that the pattern needs to be JSON-escaped. e.g. `.+\.csv` => `"pattern": ".+\\.csv"` 
 - `ignore_manifest` -- OPTIONAL (default `false`) Do not transfer manifest file if present. 

 
# Usage
 
The processor may run in two "modes":

- You may specify a simple pattern and then replace the entire file name that is matched. If the simple pattern is matched multiple times 
all occurrences are replaced by the `replacement` string.
- Regular expression pattern may contain capturing groups which can then be referenced from the pattern by `$x` 
where x is a 0 based index of the capturing group. **NOTE** that all groups in specified in the replacement string need to be present otherwise the file is ignored.
 
## Simple regular expressions

**Example 1:** 

Consider that you have a single file `/in/files/report.csv` which you want to rename to `new_report.csv`. The easiest way is to
match all files ending with `.csv`. You can use pattern `.+\.csv` to do that.

**NOTE** this is just example, the user needs to be sure there is only a single file present, otherwise it will drop all duplicate names randomly.

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": ".+\\.csv",
        "replacement": "new_report.csv"
    }
}
```

**Example 2:**

Consider that you want to remove invalid characters `#` from all files like `/in/files/report_#1234_#20200101.csv` 
which you want to rename to `report_1234_20200101.csv`. 
The easiest way is to match all `#` characters. You can use pattern `#` to do that and replace it with empty string.

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": "#",
        "replacement": ""
    }
}
```



## Using Capture groups

Regular expression pattern may contain capturing groups which can then be referenced from the pattern by `$x` 
where x is a 0 based index of the capturing group. 

**NOTE** that all groups in specified in the replacement string need to be present **otherwise the file is ignored**.   


**Example**

Let's say you receive files `/data/in/files/salesreport-&CZ.csv` and you want to rename this to drop the invalid `&` character, 
while keeping the report type (`salesreport`) and the country `CZ`.

You can create expression with two simple capturing groups: `^(.+)-&(.+)\.csv` => this will match `salesreport` and `CZ` in our example.

Let's say we want to rename this to `salesreport_CZ`. We can use pattern `$0_$1` to achieve that. `$0` matches the first capturing group (`salesreport`),
 `$1` matches the second.

Example processor configuration:

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": "^(.+)-&(.+)\\.csv",
        "replacement": "$0_$1"
    }
}
```



## Development

