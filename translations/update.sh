#!/bin/bash
#
# Tested in Ubuntu 20.04.2 LTS.
# This script must strictly contain line endings in Linux format for correct work.
# Install QT5 dev tools packages before run this script,
# by the following commands:
#
# sudo apt update
# sudo apt install -y qttools5-dev-tools
# sudo apt install -y pyqt5-dev-tools
#
# This is array of supported languages.
# When adding new  languages, this list needs to be update.
languages=(es-ar es-es es-mx pt-br pt-pt ru)
for lang in ${languages[*]}
do
   # Creation of uifiles.ts file from ../*.ui files with designation of language code
   lupdate ../*.ui -ts uifiles.ts -source-language en_US -target-language $lang
   # lupdate ../*.ui -ts uifiles.ts
   # Creation of pyfiles.ts file from ../*.py files
   pylupdate5 ../*.py -ts pyfiles.ts -verbose
   # Join uifiles.ts and pyfiles.ts files to fasteners.ts
   lconvert -i uifiles.ts pyfiles.ts -o fasteners.ts
   # Join fasteners.ts to exist fasteners_(language).ts file (-no-obsolete)
   lconvert -i fasteners.ts fasteners_$lang.ts -o fasteners_$lang.ts
   # (Release) Creation of *.qm file from fasteners_(language).ts
   lrelease fasteners_$lang.ts
   # Delete unused files
   rm uifiles.ts
   rm pyfiles.ts
   rm fasteners.ts
done
