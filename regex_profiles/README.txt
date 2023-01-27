Put files in this directory to add custom regex profiles beyond the included profiles.
Any file put here will override identically named files in the default folder.

Each profile checks its associated language codes individually. Multiple
regex profiles can therefore run against the same subtitle if the same language is specified in the profiles.
You can disable all default profiles in the subcleaner.conf file.

Regex profiles need to have to a .conf extension.
Profiles starting with a "." will be also be ignored.

Use one of the default profiles as a template to avoid unwanted results. but make sure you go over all the
purge regexes so that they don't contain any words that are real words in your language.

