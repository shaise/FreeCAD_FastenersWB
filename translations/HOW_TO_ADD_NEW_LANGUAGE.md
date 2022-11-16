# How to add new language

For example, if user want to add Italian language to fasteners WB.

At first, check language for support in FreeCAD core: https://github.com/shaise/FreeCAD_FastenersWB/issues/209

If everything goes well, you will know that the short code for the Italian language is "it". Remember that code.

Next step is download fasteners WB to Linux OS (Ubuntu, recommended).

Enter to **/translations** folder.

Create new empty fastener_**it**.ts file with content (place **"it"** after **language=**):

    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE TS>
    <TS version="2.1" language="it" sourcelanguage="en_US">
    </TS>

Open update.sh and add **"it"** language code at end of list.

    languages=(es-ar es-es pt-br pt-pt ru it)

Save update.sh and run update.sh

As a result, empty *.ts file will be generated to fill.

After adding the translations to *.ts file, run the update.sh again to get an updated *.qm file.

And finally send pull-request contained files:

    update.sh (updated)
    fastener_it.ts
    fastener_it.qm
