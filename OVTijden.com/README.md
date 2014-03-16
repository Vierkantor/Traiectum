OVTijden.com Massage-O-Matic
============================

This script can convert the tables on [OVTijden.com](http://ovtijden.com), a website that displays the Dutch train schedule (including both planned trains and delays of current trains). Don't expect perfect results, though there *should* be no big problems.

# Getting the data

The input for massage.py is the HTML table containing the schedule, as can be found on [these pages](http://ovtijden.com/iff/dvs/ut/20131217). In the source, find the big time table and select the contents of the <tbody> tag. Place it into a text file named as the station code + ".txt", in the folder containing massage.py.

# Processing the data

Run massage.py in your favorite python3 interpreter, and send its output to a file. If something went wrong, this file will start with a warning, showing the file and the location where (for example) a tag is missing. If nothing went (immediately) wrong, your result file will start with a a version: line.

# Something went wrong

Sometimes the markup gets mashed up. Some open or close brackets might be missing, meaning the parser gets confused and doesn't display enough columns in the table. You will see a warning on the top of the output. To fix this, you'll have to manually fix the .txt files and run massage.py again.

# Nothing went wrong

Check for stray '<', '/' and '>' characters in your output file, it might have still gone wrong. Again, fix any broken tags and run massage.py.

# Importing the data

When you're confident the data is correct, add the output file to the folder DataSources and run group.py (see the main README for more info) to assemble it into a new servicedata.txt.
