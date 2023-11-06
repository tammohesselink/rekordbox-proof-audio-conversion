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
    do script "cd '$currentFinderPath'; <audio-conversion-tools/.venv/bin/python> <audio-conversion-tools/scripts/convert_lossless_to_aiff.py>"
    activate
end tell
EOD
