function go -d "Uses the go program to navigate shortcuts"
    set -l output (command go $argv)
    switch $status
    case 0
        cd $output
    case 1
        for line in $output
            echo $line
        end
    end
end
