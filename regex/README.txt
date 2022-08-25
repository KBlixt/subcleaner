    TL;DR: files here override same named files in default.
    valid config names: "*.conf".


Put files in this directory to add custom regex configs.
Any file put here will override identically named files in the default folder.

Each config should check its associated language codes individually. Multiple
regex configs can run against the same subtitle. You can disable all default
configs in the subcleaner.conf file.

Regex configs need to have to a .conf extension.
Configs starting with a "." will be also be ignored.

Use one of the default configs as a template to avoid unwanted results.
