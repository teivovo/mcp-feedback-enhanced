---
type: "agent_requested"
description: "Rules to follow for using esptool to compile arduino esp32 firmware"
---
- Always read the partitions.csv for max file size for the upload_maximum_size flag.
- Always run commands with full file path.
- Always run in verbose.
- Always export the binaries and save them to the ./build/ folder. Move old ones to ./build/archive/ folder inside a subfolder with the date as folder name in YYYY-MM-DD format.
- Always show the output in the terminal and also pipe it to a log file.
- Only analyse the success of the compile using the log file as you will not have sufficient context buffer to process the verbose log.
- Always delete the log file after verifying that everything is ok.
- Example of a working powershell compile command: 

powershell -Command "cd 'C:\Users\KelvinLAW\Documents\Arduino\Pointcast_Master2\Motherboard'; & 'C:\Users\KelvinLAW\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe' compile --fqbn esp32:esp32:esp32 --warnings all --verbose --build-property upload.maximum_size=1900544 --build-property build.partitions=custom --build-property board.build.partitions=partitions 'Motherboard.ino' 2>&1 | Tee-Object -FilePath 'compile_output.log'"