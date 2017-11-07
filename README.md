# SwaggerValidate
Custom validation scripts for swagger documentation.

Instructions **Updated**

1. Check Validate.bat for the python environment filepath.
2. Run Validate.bat by double-clicking it.
3. A dialog will pop up for you to select your desired folder. Click on "Open" to execute the validate script on that directory.
4. Check the logs in the cmd prompt that will be opened. When prompted, enter 'Y' to run the modify script.
5. PROFIT! 

Changelog(v1.2)

- Script does not break when parsing an invalid json file
- Folder selection dialog to select your directory, no need to fill in full classpath now.
- Allows the choice of running modify script after the validate script finishes.
- Added in additional checks (hostname,schemes,error 201)
- Update accept-version header description and overview sections error messages.
- Error code clean-up

Changelog(v1.1) 

- Previous script only covers first api method of a given path. Current script has 100% coverage of all api methods.
- Current script now checks for valid json file.
- modify.py script is now working. 
