# Rename Files Processor


Takes all files in `/data/in/files` (or `/data/in/tables`)  and renames the files matching the regex pattern 
and moves the result to `/data/out/files` (or `/data/out/tables`). 

- All files that do not contain any match with the pattern's regular expression are left with actual name. 
- The manifest files are respected and updated accordingly.
- The pattern is applied to the filename itself, e.g. file
`/data/in/files/report.csv` is renamed from `report.csv`.
- If the replacement leads to duplicate file names, they will be overwritten.


 
 **Table of contents:**

[TOC]
   

# Configuration


## Supported parameters:

---

- **`pattern`**: The regular expression to match file names. May contain capturing groups that can be used in the replacement.

  *Note*: The pattern needs to be JSON-escaped. For example, to match files ending with `.csv`, use `.+\.csv`, which should be JSON-escaped as `"pattern": ".+\\.csv"`.

- **`replacement`**: The string to replace the matched file names. May contain references to capturing groups if present, using `$1`, `$2`, etc. (1-based indexing), where `$0` refers to the entire match.

  - In the `replacement`, you can use functions within braces `{}` to generate dynamic values:

    - `{timestamp}`: Replaced by the current timestamp in the format `yyyyMMddHHmmss`.
    - `{date}`: Replaced by the current date in the format `yyyyMMdd`.
    - `{time}`: Replaced by the current time in the format `HHmmss`.

- **`to_uppercase`** *(Optional)*: Set to `true` or `false`. If `true`, the filenames of all files that match the pattern are converted to uppercase (excluding the extension). Default is `false`.

- **`mode`** *(Optional)*: Defines the input folders to process. Default is `both`.

  - `files`: Processes everything in `in/files`.
  - `tables`: Processes everything in `in/tables`.
  - `both`: Processes everything in both `in/tables` and `in/files`.

- **`ignore_manifest`** *(Optional)*: Set to `true` or `false`. If `true`, manifest files will not be transferred if present. Default is `false`.

---


 
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

**Context replace functions**

**Example 3:**

Using a contexts functions add date and time to file name. 
The following configration will add date and time to the file name.
Example configuration:

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": "^(.+)-&(.+)\\.csv",
        "replacement": "$0_{date}_{time}_$1.csv"
    }
}
```
Result will be `/data/in/files/salesreport-&CZ.csv` => `/data/out/files/salesreport_20220101_120000_CZ.csv`.

**Example 4:**

Be aware that your file name contains more occurrences of the pattern.
The following configration will add date to the every occurrence.
Example configuration:

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": "report",
        "replacement": "{date}_report"
    }
}
```
Result will be `/data/in/files/salesreport-report.csv` => `/data/out/files/sales20220101_report_20220101_report.csv`.

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


## Additional functions

**TO UPPERCASE**

Using a parameter `to_uppercase`, you can convert the filename of all files that match the pattern to uppercase.
Example configuration:

```json
{
    "definition": {
        "component": "kds-team.processor-rename-files"
    },
    "parameters": {
        "pattern": "(.+)(\\..+)",
        "replacement": "$0$1",
        "to_uppercase": true
    }
}
```

This converts the filename from `anything\lowercase.any_extension` into `ANYTHING\LOWERCASE.any_extension`
