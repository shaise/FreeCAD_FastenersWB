#!/bin/bash
# Tested in Ubuntu 20.04.2 LTS.
# This script must containt Linux format lineedings for correctwork.
# Install QT5 dev tools packages before run this script:
# sudo apt update
# sudo apt install -y qttools5-dev-tools
# sudo apt install -y pyqt5-dev-tools
# This is array of supported languages:
languages=(es-ar es-es es_mx pt-br pt-pt ru)
for lang in ${languages[*]}
do
   # Create uifiles.ts from ../*.ui files
   #lupdate ../*.ui -ts uifiles.ts -source-language $lang -target-language en_US
   lupdate ../*.ui -ts uifiles.ts
   # Create pyfiles.ts from ../*.py files
   pylupdate5 ../*.py -ts pyfiles.ts -verbose
   # Join uifiles.ts pyfiles.ts files to fasteners.ts
   lconvert -i uifiles.ts pyfiles.ts -o fasteners.ts
   # Join fasteners.ts to exist language ts file
   lconvert -i fasteners.ts fasteners_$lang.ts -o fasteners_$lang.ts
   # Release ts file to qm
   lrelease fasteners_$lang.ts
   # Delete unused files
   rm uifiles.ts
   rm pyfiles.ts
   rm fasteners.ts
done
