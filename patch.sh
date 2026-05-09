ZIPFILE="$1"

bsdtar -xv --strip-components 1 -f "$ZIPFILE"
