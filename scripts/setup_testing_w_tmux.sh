username="$1"

tmux split-window -h
ssh "$1"@cs-1.cs.mcgill.ca

tmux split-window -v
tmux split-window -v
tmux select-pane -U
tmux select-pane -U
tmux split-window
