# About translating Fasteners Workbench

## Translators:

Translations for this workbench is done by visiting the **FreeCAD-addons**
project on CrowdIn platform at <https://crowdin.com/project/freecad-addons> webpage,
then find your language, look for the **Fasteners** project and do the translation.

> [!IMPORTANT]
> PR system of translations is no longer accepted. Please use CrowdIn above.

## Maintainers:

> [!NOTE]
> All commands **must** be run in `./Resources/translations/` directory.

> [!WARNING]
> If you want to update/release the files you need to have installed
> `lupdate` and `lrelease` from Qt6 version. Using the versions from
> Qt5 is not advised because they're buggy.

## Updating translations template file

To update the template file from source files you should use this command:

```shell
./update_translation.sh -U
```

Once done you can commit the changes and upload the new file to CrowdIn platform
at <https://crowdin.com/project/freecad-addons> webpage and find the **Fasteners** project.

## Creating file for missing locale

This step is not really needed anymore because you should use the CrowdIn platform
to do the translation, take the information here as a reference.

### Using script

To create a file for a new language with all **Fasteners** translatable strings execute
the script with `-u` flag plus your locale:

```shell
./update_translation.sh -u de
```

### Renaming file

Also you can rename new `Fasteners.ts` file by appending the locale code,
for example, `Fasteners_de.ts` for German and change

```xml
<TS version="2.1">
```

to

```xml
<TS version="2.1" language="de" sourcelanguage="en">
```

As of 13/09/2024 the supported locales on **FreeCAD**
(according to `FreeCADGui.supportedLocales()`) are 43:

```python
{'English': 'en', 'Afrikaans': 'af', 'Arabic': 'ar', 'Basque': 'eu',
'Belarusian': 'be', 'Bulgarian': 'bg', 'Catalan': 'ca',
'Chinese Simplified': 'zh-CN', 'Chinese Traditional': 'zh-TW', 'Croatian': 'hr',
'Czech': 'cs', 'Dutch': 'nl', 'Filipino': 'fil', 'Finnish': 'fi', 'French': 'fr',
'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Hungarian': 'hu',
'Indonesian': 'id', 'Italian': 'it', 'Japanese': 'ja', 'Kabyle': 'kab',
'Korean': 'ko', 'Lithuanian': 'lt', 'Norwegian': 'no', 'Polish': 'pl',
'Portuguese': 'pt-PT', 'Portuguese, Brazilian': 'pt-BR', 'Romanian': 'ro',
'Russian': 'ru', 'Serbian': 'sr', 'Serbian, Latin': 'sr-CS', 'Slovak': 'sk',
'Slovenian': 'sl', 'Spanish': 'es-ES', 'Spanish, Argentina': 'es-AR',
'Swedish': 'sv-SE', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Valencian': 'val-ES',
'Vietnamese': 'vi'}
```

Alternatively, you can edit your language file on `Qt Linguist` from
`qt5-tools`/`qt6-tools` package (preferred) or in a text editor like `xed`, `mousepad`,
`gedit`, `nano`, `vim`/`nvim`, `geany` etc. (you'll suffer) and translate it.
After translating the file locally upload your changes to CrowdIn platform
in order for it to be synced.

## Compiling translations

To convert all `.ts` files to `.qm` files (merge) you can use this command:

```shell
./update_translation.sh -R
```

If you are a translator that wants to update only their language file
to test it on **FreeCAD** you can use this command:

```shell
./update_translation.sh -r de
```

This will update the `.qm` file for your language (German in this case).

## Updating translations

Some notes for maintainers to consider:

- First update the `fasteners.ts` file then upload it to CrowdIn
- Remember to pull the translations from CrowdIn periodically
- Make sure you're using the correct `lupdate` version
- Include both `.ts` and `.qm` files.
- Make sure changes are working before making a PR

<https://github.com/shaise/FreeCAD_FastenersWB>

## More information

You can read more about translating external workbenches here:

<https://wiki.freecad.org/Translating_an_external_workbench>
