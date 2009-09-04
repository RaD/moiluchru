SSH_AGENT=/usr/bin/ssh-agent
eval `$SSH_AGENT -s 2>/dev/null`
unset SSH_AGENT
ssh-add

