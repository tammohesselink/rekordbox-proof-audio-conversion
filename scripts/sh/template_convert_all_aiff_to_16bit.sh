#!/bin/bash

currentFinderPath=$(osascript <<EOD
tell application "Finder"
    if (count of Finder windows) is 0 then
        return ""
    else
        return POSIX path of (target of front Finder window as text)
    end if
end tell
EOD
)

osascript <<EOD
tell application "Terminal"
    do script "cd '$currentFinderPath'; /path/to/your/venv/bin/python /path/to/your/repo/scripts/convert_aiff_to_16bit.py"
    activate
end tell
EOD
