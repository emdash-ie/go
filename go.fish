function go -d "Uses the go program to navigate shortcuts"
    set -l output (command go $argv)
    switch $status
    case 0
        cd $output
    case 1
        string join \n -- $output | less -S
    end
end
