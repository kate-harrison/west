#!/bin/bash

NUM_FILES=56
#BASE_URL="https://www2.census.gov/geo/tiger/GENZ2010"
BASE_URL="http://www2.census.gov/geo/tiger/GENZ2010/"

ZIP_OUTPUT_DIR="original_zips"

mkdir -p $ZIP_OUTPUT_DIR

for state_num in `seq 1 $NUM_FILES`;
do
	filename=`printf "gz_2010_%02d_140_00_500k.zip" $state_num`
	if [ ! -f "$ZIP_OUTPUT_DIR/$filename" ];
	then
		echo "*** Downloading shapefile: $filename"
		wget "$BASE_URL/$filename" --no-check-certificate
		mv $filename $ZIP_OUTPUT_DIR
	else
		echo "*** File already downloaded: $filename"
	fi

	output_dir=`basename $filename .zip`
	mkdir -p $output_dir
	unzip -u "$ZIP_OUTPUT_DIR/$filename" -d $output_dir
done

