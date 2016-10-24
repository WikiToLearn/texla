#!/bin/bash

# This script helps finding the name of the blocks that contain broken math
# the plugin math_check_online returns the id of the broken blocks
# this script searches for the block name inside the .tree file
# this is intended as a temporary solution, it is not elegant
# how to use this:
# ./math-error-find $output-folder $error-block-id
# $output-folder is where the .tree file is saved
# $error-block-id does not contain the starting `@-` characters
# example
# ./math-error-find.sh test/Algebra_1-Appunti-out x7t-la0-v5f-j0p
# with
# >➜ ls test/Algebra_1-Appunti-out/
# >0File_principale-coll.json  0File_principale.json  0File_principale.tree
# >0File_principale.debug      0File_principale.mw    0File_principale_pages


current_dir=`pwd`
cd $1

tree_file=`find . -name *.tree`

error=$2
IFS='-' read -ra block_id <<< "$error"
for i in "${block_id[@]}"; do
    str_search=$i\",
    echo grep -F "$str_search" $tree_file
    grep -A 7 -F $str_search $tree_file
done

cd $current_dir
