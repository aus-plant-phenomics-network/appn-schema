#!/bin/bash
cd ../vocabulary-schema/
git pull
cp -R ../appn-schema/vocabulary/* id/
cp ../appn-schema/appn-schema.ttl schema/
cp ../appn-schema/appn-schema.html schema/
cp ../appn-schema/context.json schema/
git status
echo "To commit changes, enter a commit message"
read MESSAGE
if [[ "$MESSAGE" != "" ]]; then
    echo "Committing and pushing changes"
    git add .
    git commit -m "$MESSAGE"
    git push
fi
cd -
