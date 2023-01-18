    TL;DR: Enable cleaning for a language by adding it to a regex profile.
    profiles here override same named profiles in default.
    valid profile names: "*.conf".

In order for the script to clean a subtitle the script need to have a profile for the
language in the subtitle file. or disable this feature in the main config.
Put files in this directory to add custom regex profiles beyond the included profiles.
Any file put here will override identically named files in the default folder.

Each profile checks its associated language codes individually. Multiple
regex profiles can therefore run against the same subtitle if the same language is specified in the profiles.
You can disable all default profiles in the subcleaner.conf file.

Regex profiles need to have to a .conf extension.
Profiles starting with a "." will be also be ignored.

Use one of the default profiles as a template to avoid unwanted results.
