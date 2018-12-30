function go -d "Uses the go program to navigate shortcuts"
    set -l output (command go $argv)
    set -l exitcode $status
    switch "$output[1]"
    case navigate
        cd $output[2]
    case display
        string join \n -- $output[2..-1] | less -S
    end
    return $exitcode
end
