#!/bin/bash

SYS_FILES=(
  "linux/root/usr/share/cinnamon/js/ui/messageTray.js"
)

for file in "$SYS_FILES" ; do
  dest=$(echo "$file" | sed -e 's@linux/root@@')
  sudo cp "$file" "$dest"
done
