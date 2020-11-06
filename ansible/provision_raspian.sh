#! /bin/sh

THIS_DIR="$(dirname $0)"

if [ -z "$1" ]; then
    echo "Usage: $0 HOST [HOST []]"
    exit 1
fi

TEMP_HOSTS=$(mktemp -d)
for h in "$@"; do
    echo $h >> $TEMP_HOSTS/hosts
done

cd $THIS_DIR
ansible-playbook --user pi --ask-pass --ask-become-pass -i $TEMP_HOSTS initial.yaml

rm -rf $TEMP_HOSTS
