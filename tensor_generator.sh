mkdir singledata
mkdir singlewav

python midimaker.py

for file in singledata/*.mid
do 
    timidity -Ow -s 44100 -o "singlewav/`basename "$file" .mid`.wav" "$file"
done

rm -rf singledata

python wav2tensor.py

rm -rf singlewav
