#!/bin/sh

cat <<EOF > js/myvar.js
env = {
    TITLE: "${TITLE}"
}
EOF

nginx -g 'daemon off;'