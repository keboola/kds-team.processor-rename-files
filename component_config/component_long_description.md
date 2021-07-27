Takes all files in `/data/in/files` and renames the files matching the regex pattern and moves the result to `/data/out/files`. 

- All files that does not contain any match with the pattern's regular expression are left with actual name. 
- The manifest files are respected and updated accordingly.
- The pattern is applied to the filename itself, e.g. file
`/data/in/files/report.csv` is renamed from `report.csv`.
- If the replacement leads to duplicate file names, they will be overwritten.