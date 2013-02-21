RecordExpress
=============

RecordExpress lightweight EAD generator

A tool for creating lightweight, high level descriptive EAD files to which you can attach an internet hosted pdf file containing detailed collection descriptions.

Currently uses the DjangoDublinCore models, which makes the admin interface a bit brittle (need to have correct qualifier text field to make export correct).
I want to refactor into a direct EAD model of the data. This will cause numerous tables to be created but will simplify the design.

It currently also has a number of dependencies on OAC data and software.

TODO:
Test project bundled with package.
Make tests pass on clean install. 
Detail the mapping of QDC to EAD elements.
How to make the "preview" work when not on an OAC box?
Refactor to remove DjangoDublinCore and use direct foreign key metadata fields.
