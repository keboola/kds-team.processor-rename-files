Takes all files in `/data/in/files` and creates or updates the manifest file move all files to `/data/out/files`. 

Adds or updates these manifest attributes

 - `tags` --  Required array of tags, Assigns one or more tags to the file.
 - `is_permanent` -- DEFAULT `false` If is_permanent is false, the file will be automatically deleted after 15 days.
 - `notify` -- When notify is true, the members of the project will be notified that a file has been uploaded to the project. 
 - `encrypted` -- If true, the file content will be encrypted in the S3 storage. Default: false 
 
 Supports dynamic nestable functions to process the filename into tags.


## Sample configurations

All parameters:

```
{  
    "definition": {
        "component": "kds-team.processor-create-file-manifest"
    },
    "parameters": {
        "tags": ["my_tag"],
        "is_permanent":true,
         "notify": false,
         "encrypted": false,
    "tag_functions": [
      {
        "function": "filename_split",
        "args": [
          "_"
        ],
        "optional_args": {
          "position": 1,
          "tag_prefix": "FILENAME_PART"
        }
      }
    ]
    }
}
```